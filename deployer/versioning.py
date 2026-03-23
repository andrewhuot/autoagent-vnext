import yaml
import json
import hashlib
import time
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConfigVersion:
    version: int
    config_hash: str
    filename: str
    timestamp: float
    scores: dict  # composite score dict at time of deployment
    status: str  # "active", "canary", "retired", "rolled_back"


class ConfigVersionManager:
    def __init__(self, configs_dir: str = "configs"):
        self.configs_dir = Path(configs_dir)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.configs_dir / "manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        """Load or create manifest tracking all versions."""
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                return json.load(f)
        return {"versions": [], "active_version": None, "canary_version": None}

    def _save_manifest(self):
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def _config_hash(self, config: dict) -> str:
        return hashlib.sha256(yaml.dump(config, sort_keys=True).encode()).hexdigest()[:12]

    def get_next_version(self) -> int:
        if not self.manifest["versions"]:
            return 1
        return max(v["version"] for v in self.manifest["versions"]) + 1

    def save_version(self, config: dict, scores: dict, status: str = "canary") -> ConfigVersion:
        """Save a new config version."""
        version_num = self.get_next_version()
        filename = f"v{version_num:03d}.yaml"
        filepath = self.configs_dir / filename

        with open(filepath, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        cv = ConfigVersion(
            version=version_num,
            config_hash=self._config_hash(config),
            filename=filename,
            timestamp=time.time(),
            scores=scores,
            status=status,
        )
        self.manifest["versions"].append({
            "version": cv.version,
            "config_hash": cv.config_hash,
            "filename": cv.filename,
            "timestamp": cv.timestamp,
            "scores": cv.scores,
            "status": cv.status,
        })
        if status == "canary":
            self.manifest["canary_version"] = version_num
        elif status == "active":
            self.manifest["active_version"] = version_num
        self._save_manifest()
        return cv

    def promote(self, version: int):
        """Promote a version to active, retire the old active."""
        for v in self.manifest["versions"]:
            if v["version"] == self.manifest.get("active_version"):
                v["status"] = "retired"
            if v["version"] == version:
                v["status"] = "active"
        self.manifest["active_version"] = version
        self.manifest["canary_version"] = None
        self._save_manifest()

    def rollback(self, version: int):
        """Rollback a canary version."""
        for v in self.manifest["versions"]:
            if v["version"] == version:
                v["status"] = "rolled_back"
        self.manifest["canary_version"] = None
        self._save_manifest()

    def get_active_config(self) -> dict | None:
        """Load the active config."""
        active = self.manifest.get("active_version")
        if active is None:
            return None
        for v in self.manifest["versions"]:
            if v["version"] == active:
                filepath = self.configs_dir / v["filename"]
                with open(filepath) as f:
                    return yaml.safe_load(f)
        return None

    def get_canary_config(self) -> dict | None:
        """Load the canary config if one exists."""
        canary = self.manifest.get("canary_version")
        if canary is None:
            return None
        for v in self.manifest["versions"]:
            if v["version"] == canary:
                filepath = self.configs_dir / v["filename"]
                with open(filepath) as f:
                    return yaml.safe_load(f)
        return None

    def get_version_history(self) -> list[dict]:
        return list(self.manifest["versions"])
