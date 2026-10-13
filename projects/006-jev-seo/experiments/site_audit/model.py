"""OpenAI-compatible Chat Completions adapter. No TypeSafe dependency."""
import json
import requests

from site_audit.config import ModelConfig
from site_audit.evaluation import SYSTEM_PROMPT, parse_json, response_schema, validate_answers


class ModelClient:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.ledger = {"attempts": 0, "succeeded": 0, "failed": 0, "skipped_limit": 0,
                       "input_tokens": 0, "output_tokens": 0, "usage_missing": 0,
                       "cost_usd": None, "model_requested": config.model}

    def ask(self, job: dict) -> dict:
        if self.ledger["attempts"] >= self.config.max_requests:
            self.ledger["skipped_limit"] += 1
            return {"status": "skipped", "error": "request_limit"}
        cfg = self.config
        body = {
            "model": cfg.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps({"state": job["state"], "questions": job["questions"]}, ensure_ascii=False)},
            ],
            cfg.token_parameter: cfg.max_tokens,
        }
        schema = response_schema(job["questions"])
        if cfg.response_mode == "json_schema":
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "website_review", "strict": True, "schema": schema}}
        elif cfg.response_mode == "json_object":
            body["response_format"] = {"type": "json_object"}
        if cfg.response_mode != "json_schema":
            body["messages"][1]["content"] += "\nJSON schema:\n" + json.dumps(schema, ensure_ascii=False)
        headers = {"Content-Type": "application/json"}
        if cfg.api_key:
            headers["Authorization"] = "Bearer " + cfg.api_key
        endpoint = cfg.base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint += "/chat/completions"
        self.ledger["attempts"] += 1
        try:
            # No automatic retry/fallback: a repeated request can be charged again.
            response = requests.post(endpoint, json=body, headers=headers, timeout=cfg.timeout, allow_redirects=False)
            if response.status_code != 200:
                raise ValueError(f"HTTP_{response.status_code}")
            data = response.json()
            usage = data.get("usage") or {}
            if isinstance(usage.get("prompt_tokens"), int) and isinstance(usage.get("completion_tokens"), int):
                self.ledger["input_tokens"] += usage["prompt_tokens"]
                self.ledger["output_tokens"] += usage["completion_tokens"]
            else:
                self.ledger["usage_missing"] += 1
            item = data["choices"][0]
            if item.get("finish_reason") != "stop" or item["message"].get("refusal"):
                raise ValueError("incomplete_or_refused")
            content = item["message"].get("content")
            if not isinstance(content, str):
                raise ValueError("missing_text_content")
            answers = validate_answers(job, parse_json(content))
            self.ledger["succeeded"] += 1
            return {"status": "ok", "answers": answers, "model": data.get("model") or cfg.model}
        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError, AttributeError):
            self.ledger["failed"] += 1
            # Do not persist provider bodies, exception messages, endpoint URLs or credentials.
            return {"status": "failed", "error": "invalid_response_or_request_failed"}
