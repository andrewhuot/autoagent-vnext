"""FastAPI server for the ADK agent."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent.config.loader import load_config, load_config_with_canary
from agent.root_agent import create_root_agent

app = FastAPI(title="AutoAgent VNext", version="0.1.0")

# Global state — initialized on startup
_runner: Runner | None = None
_session_service: InMemorySessionService | None = None
_app_name = "autoagent"
_user_id = "default_user"


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.on_event("startup")
async def startup() -> None:
    global _runner, _session_service

    configs_dir = os.environ.get("AUTOAGENT_CONFIGS_DIR", "configs")
    config_path = os.environ.get("AUTOAGENT_CONFIG_PATH", "")

    if config_path:
        config = load_config(config_path)
    elif Path(configs_dir).exists():
        config = load_config_with_canary(configs_dir)
    else:
        config = load_config(
            str(Path(__file__).parent / "config" / "base_config.yaml")
        )

    agent = create_root_agent(config)
    _session_service = InMemorySessionService()
    _runner = Runner(
        agent=agent,
        app_name=_app_name,
        session_service=_session_service,
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "agent_loaded": _runner is not None}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    if _runner is None or _session_service is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    session_id = request.session_id or str(uuid.uuid4())

    # Ensure session exists
    session = await _session_service.get_session(
        app_name=_app_name, user_id=_user_id, session_id=session_id
    )
    if session is None:
        session = await _session_service.create_session(
            app_name=_app_name, user_id=_user_id, session_id=session_id
        )

    # Build user content
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=request.message)],
    )

    # Run agent and collect response
    response_parts: list[str] = []
    async for event in _runner.run_async(
        user_id=_user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_parts.append(part.text)

    # Try logging (don't fail if logger not ready)
    try:
        from logger.middleware import log_conversation_turn  # noqa: F401
    except (ImportError, Exception):
        pass

    response_text = "\n".join(response_parts) if response_parts else "I'm sorry, I couldn't generate a response."

    return ChatResponse(response=response_text, session_id=session_id)
