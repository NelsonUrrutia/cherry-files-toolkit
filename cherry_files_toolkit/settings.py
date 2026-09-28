import json
from pathlib import Path

from platformdirs import user_config_dir


class Settings:
    def __init__(self) -> None:
        self.path = Path(user_config_dir("cherry-files-toolkit")) / "settings.json"

    def load(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def get(self, key, default=None):
        return self.load().get(key, default)

    def set(self, key, value) -> None:
        data = self.load()
        data[key] = value
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass
