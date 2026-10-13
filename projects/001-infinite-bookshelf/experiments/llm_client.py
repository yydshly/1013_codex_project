"""Dependency-free, replaceable OpenAI-compatible book generation experiment.

The outline -> title -> sections workflow is independently rewritten from the
idea demonstrated by https://github.com/Bklieger/infinite-bookshelf.
No upstream application code is copied into this module.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import time
from dataclasses import dataclass, field
from typing import Iterator, Mapping
from urllib import error, parse, request


class GenerationError(Exception):
    """A safe, user-facing error; never contains provider response bodies."""


def read_dotenv(path: Path) -> dict[str, str]:
    """Read simple KEY=value configuration without expansion or shell execution."""
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        name, sep, value = line.partition("=")
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name.strip()):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].rstrip()
        values[name.strip()] = value
    return values


@dataclass(frozen=True)
class ModelConfig:
    base_url: str = ""
    model: str = ""
    api_key: str = field(default="", repr=False)
    section_max_tokens: int = 800
    timeout_seconds: int = 90
    reason: str = ""

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.model and not self.reason)

    @property
    def public_model(self) -> str:
        # Protect against accidentally assigning a credential to the model field.
        return "" if self.api_key and self.api_key in self.model else self.model

    @property
    def completion_url(self) -> str:
        if self.base_url.endswith("/chat/completions"):
            return self.base_url
        return self.base_url.rstrip("/") + "/chat/completions"

    @classmethod
    def from_environment(
        cls, environ: Mapping[str, str] | None = None, env_path: Path | None = None
    ) -> "ModelConfig":
        values = read_dotenv(env_path or Path(__file__).with_name(".env"))
        values.update(os.environ if environ is None else environ)
        base_url = values.get("BOOKSHELF_BASE_URL", "").strip().rstrip("/")
        model = values.get("BOOKSHELF_MODEL", "").strip()
        key_env = values.get("BOOKSHELF_API_KEY_ENV", "").strip()
        api_key = values.get(key_env, "") if key_env else values.get("BOOKSHELF_API_KEY", "")
        api_key = api_key.strip()
        reason = ""
        try:
            parsed = parse.urlsplit(base_url)
            parsed.port
        except ValueError:
            parsed = parse.urlsplit("")
        if not base_url or not model:
            reason = "尚未配置模型，请在 experiments/.env 中填写接口地址和模型名称。"
        elif (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            reason = "模型接口地址无效：请填写 http(s) 地址，不包含用户名、密码、查询参数或片段。"
        elif not re.fullmatch(r"[A-Za-z0-9_.:/-]{1,256}", model):
            reason = "模型名称无效，请使用服务商提供的模型标识。"
        elif key_env and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key_env):
            reason = "BOOKSHELF_API_KEY_ENV 必须是本机环境变量的名称。"
        elif api_key and (api_key in model or "\n" in api_key or "\r" in api_key):
            reason = "模型配置无效，请检查模型名称和密钥字段。"
        try:
            max_tokens = int(values.get("BOOKSHELF_SECTION_MAX_TOKENS", "800"))
            timeout = int(values.get("BOOKSHELF_TIMEOUT_SECONDS", "90"))
            if not 100 <= max_tokens <= 4000 or not 1 <= timeout <= 120:
                raise ValueError
        except (TypeError, ValueError):
            max_tokens, timeout = 800, 90
            reason = "配置范围无效：章节 token 上限须为 100–4000，单次超时须为 1–120 秒。"
        return cls(base_url, model, api_key, max_tokens, timeout, reason)


def parse_outline(content: str, chapter_count: int) -> list[dict[str, str]]:
    """Accept JSON or a fenced JSON response, then strictly validate its shape."""
    text = content.strip()
    if text.startswith("```"):
        match = re.fullmatch(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", text, re.IGNORECASE)
        if not match:
            raise GenerationError("模型返回的目录不是有效 JSON，请重试或更换支持结构化输出的模型。")
        text = match.group(1).strip()
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        raise GenerationError("模型返回的目录不是有效 JSON，请重试或更换支持结构化输出的模型。") from None
    if isinstance(data, dict):
        data = data.get("outline")
    if not isinstance(data, list) or len(data) != chapter_count:
        raise GenerationError("模型返回的目录章节数不符合要求，请重试。")
    outline: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            raise GenerationError("模型返回的目录格式不完整，请重试。")
        title, description = item.get("title"), item.get("description")
        if not isinstance(title, str) or not isinstance(description, str):
            raise GenerationError("模型返回的目录缺少章节标题或写作说明，请重试。")
        title, description = title.strip(), description.strip()
        if not 1 <= len(title) <= 200 or not 1 <= len(description) <= 2000:
            raise GenerationError("模型返回的章节标题或写作说明长度无效，请重试。")
        outline.append({"title": title, "description": description})
    return outline


class LLMClient:
    def __init__(self, config: ModelConfig):
        if not config.configured:
            raise GenerationError(config.reason)
        self.config = config
        self.requests = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.usage_reported = False
        # Do not follow redirects with an Authorization header.
        self.opener = request.build_opener(_NoRedirect())

    def complete(self, messages: list[dict[str, str]], max_tokens: int, json_mode: bool = False) -> tuple[str, bool]:
        payload = {"model": self.config.model, "messages": messages, "max_tokens": max_tokens, "stream": False}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = "Bearer " + self.config.api_key
        req = request.Request(self.config.completion_url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), headers=headers, method="POST")
        self.requests += 1
        try:
            with self.opener.open(req, timeout=self.config.timeout_seconds) as response:
                body = response.read(4 * 1024 * 1024 + 1)
                if len(body) > 4 * 1024 * 1024:
                    raise GenerationError("模型响应过大，请降低章节长度后重试。")
        except error.HTTPError as exc:
            if exc.code == 400 and json_mode:
                # Some compatible services omit response_format. Retry the same
                # JSON-instructed prompt once without that optional parameter.
                exc.close()
                return self.complete(messages, max_tokens, json_mode=False)
            messages_by_status = {
                400: "模型服务拒绝了请求，请确认模型和接口支持 Chat Completions 及 max_tokens 参数。",
                401: "模型服务认证失败，请检查本机 API 密钥。",
                403: "模型服务拒绝访问，请检查密钥权限和模型访问权限。",
                404: "未找到模型或接口，请检查模型名称及接口地址（通常以 /v1 结尾）。",
                429: "模型服务达到调用或余额限制，请稍后重试并检查服务账户。",
            }
            if 300 <= exc.code < 400:
                message = "模型接口返回重定向，请直接配置最终接口地址。"
            else:
                message = messages_by_status.get(exc.code, "模型服务暂时不可用，请稍后重试。")
            raise GenerationError(message) from None
        except (error.URLError, TimeoutError, OSError):
            raise GenerationError("无法连接模型服务或请求超时，请检查接口地址、网络和服务状态。") from None
        try:
            data = json.loads(body)
            choice = data["choices"][0]
            content = choice["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError
            usage = data.get("usage", {})
            if isinstance(usage, dict):
                for key, attr in (("prompt_tokens", "input_tokens"), ("completion_tokens", "output_tokens")):
                    value = usage.get(key)
                    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                        setattr(self, attr, getattr(self, attr) + value)
                        self.usage_reported = True
            return content.strip(), choice.get("finish_reason") == "length"
        except (json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError, UnicodeDecodeError):
            raise GenerationError("模型服务返回的内容不符合 Chat Completions 格式，或正文为空。") from None


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def generate_book(config: ModelConfig, topic: str, instructions: str, chapter_count: int = 3) -> Iterator[dict]:
    """Yield whole-stage events; each section is one actual provider call."""
    start = time.monotonic()
    client = LLMClient(config)
    outline_text, truncated = client.complete(
        [
            {"role": "system", "content": "你是一位中文非虚构内容编辑。只返回合法 JSON 对象，格式为 {\"outline\":[{\"title\":\"章节标题\",\"description\":\"本章目标与内容边界\"}]}。不要 Markdown，不要解释。"},
            {"role": "user", "content": f"主题：{topic}\n读者与写作要求：{instructions or '面向初学者，解释清楚，提供具体例子。'}\n恰好规划 {chapter_count} 章，各章循序渐进、避免重复；不要生成正文。"},
        ],
        max_tokens=min(2000, 300 * chapter_count + 200),
        json_mode=True,
    )
    if truncated:
        raise GenerationError("目录生成达到长度上限，请减少章节数或简化要求后重试。")
    outline = parse_outline(outline_text, chapter_count)
    yield {"type": "outline", "outline": outline}
    outline_json = json.dumps(outline, ensure_ascii=False)
    title, title_truncated = client.complete(
        [
            {"role": "system", "content": "根据主题和目录写一个简洁的中文书名，只返回书名文本，不要引号、Markdown、解释或副标题列表。"},
            {"role": "user", "content": f"主题：{topic}\n写作要求：{instructions}\n完整目录：{outline_json}"},
        ], max_tokens=120,
    )
    title = title.strip("\"'《》 \n")
    if title_truncated or not 1 <= len(title) <= 200 or "\n" in title:
        raise GenerationError("模型返回的书名格式不符合要求，请重试。")
    yield {"type": "title", "title": title}
    sections: list[dict] = []
    truncated_sections: list[int] = []
    for index, chapter in enumerate(outline):
        previous = [
            {"title": section["title"], "summary_excerpt": section["content"][:600]}
            for section in sections
        ]
        content, section_truncated = client.complete(
            [
                {"role": "system", "content": "你是一位中文非虚构作者。按给定章节边界撰写可阅读的 Markdown 正文，使用小标题、解释和具体例子。不要重复章标题，不要声称已查证未提供的事实，不要杜撰引用。参考完整目录安排顺序，沿用前文术语，避免重复已讲内容。"},
                {"role": "user", "content": f"书名：{title}\n主题：{topic}\n写作要求：{instructions or '面向初学者，解释清楚，提供具体例子。'}\n完整目录：{outline_json}\n前文章节的开头摘录（不是完整前文）：{json.dumps(previous, ensure_ascii=False)}\n当前章节：第 {index + 1} 章 {chapter['title']}\n本章内容边界：{chapter['description']}\n请控制篇幅，在最多 {config.section_max_tokens} 输出 tokens 内完成这一章；只写本章正文。"},
            ], max_tokens=config.section_max_tokens,
        )
        section = {"title": chapter["title"], "content": content, "truncated": section_truncated}
        sections.append(section)
        if section_truncated:
            truncated_sections.append(index)
        yield {"type": "section", "index": index, **section}
    yield {
        "type": "done",
        "book": {
            "title": title, "topic": topic, "instructions": instructions,
            "outline": outline, "sections": sections,
            "provenance": {
                "mode": "live", "model": config.public_model,
                "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "workflow": "outline-title-sequential-sections",
                "coherence_context": "full outline and first 600 characters of prior chapters",
                "source_project": "https://github.com/Bklieger/infinite-bookshelf",
            },
        },
        "stats": {
            "requests": client.requests, "input_tokens": client.input_tokens,
            "output_tokens": client.output_tokens, "usage_reported": client.usage_reported,
            "elapsed_seconds": round(time.monotonic() - start, 2),
            "truncated_sections": truncated_sections,
        },
    }
