"""Explicit local configuration; credentials never enter audit artifacts."""
from dataclasses import dataclass, field
import os
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent


def setting(name: str) -> str | None:
    if name in os.environ:
        return os.environ[name].strip() or None
    configured = os.environ.get("SITE_AUDIT_ENV_FILE")
    paths = [Path(configured).expanduser()] if configured else []
    paths += [Path.cwd() / ".env", ROOT / ".env"]
    for path in dict.fromkeys(paths):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip().removeprefix("export ")
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip("\"'") or None
    return None


@dataclass(frozen=True)
class ModelConfig:
    base_url: str
    model: str
    api_key: str = field(default="", repr=False)
    response_mode: str = "json_schema"
    max_tokens: int = 3000
    token_parameter: str = "max_completion_tokens"
    timeout: int = 120
    max_requests: int = 20

    def __post_init__(self):
        url = urlsplit(self.base_url)
        if url.scheme not in ("https", "http") or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("AUDIT_LLM_BASE_URL must be an HTTP(S) base URL without credentials, query or fragment")
        if not self.model.strip():
            raise ValueError("Set AUDIT_LLM_MODEL to your actual model ID")
        if self.response_mode not in ("json_schema", "json_object", "text"):
            raise ValueError("AUDIT_LLM_RESPONSE_MODE must be json_schema, json_object or text")
        if self.token_parameter not in ("max_completion_tokens", "max_tokens"):
            raise ValueError("AUDIT_LLM_TOKEN_PARAMETER must be max_completion_tokens or max_tokens")
        if min(self.max_tokens, self.timeout, self.max_requests) <= 0:
            raise ValueError("Model token, timeout and request limits must be positive")

    @classmethod
    def from_env(cls):
        base = setting("AUDIT_LLM_BASE_URL")
        model = setting("AUDIT_LLM_MODEL")
        if not base or not model:
            raise ValueError("Configure AUDIT_LLM_BASE_URL and AUDIT_LLM_MODEL in experiments/.env")
        return cls(
            base_url=base.rstrip("/"), model=model,
            api_key=setting("AUDIT_LLM_API_KEY") or "",
            response_mode=setting("AUDIT_LLM_RESPONSE_MODE") or "json_schema",
            max_tokens=int(setting("AUDIT_LLM_MAX_TOKENS") or "3000"),
            token_parameter=setting("AUDIT_LLM_TOKEN_PARAMETER") or "max_completion_tokens",
            timeout=int(setting("AUDIT_LLM_TIMEOUT") or "120"),
            max_requests=int(setting("AUDIT_LLM_MAX_REQUESTS") or "20"),
        )
