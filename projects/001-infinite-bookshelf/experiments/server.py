"""Local static demo and NDJSON API. Run with Python 3.10+, no dependencies."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit

from llm_client import GenerationError, ModelConfig, generate_book

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
MAX_BODY_BYTES = 64 * 1024


class RequestError(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message, self.status = message, status


def validate_generation(data: object) -> tuple[str, str, int]:
    if not isinstance(data, dict):
        raise RequestError("请求必须是 JSON 对象。")
    topic = data.get("topic", "")
    instructions = data.get("instructions", "")
    count = data.get("chapter_count", 3)
    if not isinstance(topic, str) or not 1 <= len(topic.strip()) <= 2000:
        raise RequestError("请填写主题，主题长度须为 1–2000 字符。")
    if not isinstance(instructions, str) or len(instructions) > 8000:
        raise RequestError("写作要求须为文本，且不超过 8000 字符。")
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 6:
        raise RequestError("章节数量须为 1–6 的整数。")
    return topic.strip(), instructions.strip(), count


class BookshelfServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address, handler_class, config: ModelConfig):
        super().__init__(server_address, handler_class)
        self.model_config = config
        self.generation_lock = threading.Lock()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=WEB_DIR, **kwargs):
        super().__init__(*args, directory=str(directory), **kwargs)

    def log_message(self, format, *args):
        # Default access logs may include user-provided query strings. Keep quiet.
        return

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def same_origin(self):
        host = self.headers.get("Host", "")
        try:
            parsed_host = urlsplit("http://" + host)
            actual_port = self.server.server_address[1]
            if parsed_host.hostname not in {"localhost", "127.0.0.1"} or (parsed_host.port or 80) != actual_port:
                raise RequestError("仅允许从本机演示地址访问。", 403)
            origin = self.headers.get("Origin")
            if origin:
                parsed_origin = urlsplit(origin)
                if parsed_origin.scheme != "http" or parsed_origin.netloc.lower() != host.lower() or parsed_origin.path or parsed_origin.query or parsed_origin.fragment:
                    raise RequestError("仅允许同源页面调用本机演示接口。", 403)
        except ValueError:
            raise RequestError("请求地址无效。", 403) from None

    def do_GET(self):
        path = urlsplit(self.path).path
        if path.startswith("/api/"):
            try:
                self.same_origin()
            except RequestError as exc:
                self.json_response({"error": exc.message}, exc.status)
                return
            if path == "/api/config":
                config = self.server.model_config
                self.json_response({"configured": config.configured, "model": config.public_model, "reason": config.reason})
            elif path == "/api/health":
                self.json_response({"ok": True})
            else:
                self.json_response({"error": "接口不存在。"}, 404)
            return
        # Serve only ../web, never experiments/.env or source directories.
        super().do_GET()

    def do_OPTIONS(self):
        self.json_response({"error": "本机演示不支持跨来源调用。"}, 403)

    def do_POST(self):
        try:
            self.same_origin()
            if urlsplit(self.path).path != "/api/generate":
                raise RequestError("接口不存在。", 404)
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise RequestError("请使用 application/json 请求格式。", 415)
            if self.headers.get("Transfer-Encoding"):
                raise RequestError("不支持分块上传。")
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise RequestError("请求长度无效。") from None
            if not 1 <= length <= MAX_BODY_BYTES:
                raise RequestError("请求为空或超过 64 KB 上限。", 413)
            self.connection.settimeout(10)
            try:
                data = json.loads(self.rfile.read(length))
            except (json.JSONDecodeError, UnicodeDecodeError, TimeoutError, OSError):
                raise RequestError("请求不是有效的 UTF-8 JSON，或上传超时。") from None
            topic, instructions, count = validate_generation(data)
            config = self.server.model_config
            if not config.configured:
                raise RequestError(config.reason, 503)
            if not self.server.generation_lock.acquire(blocking=False):
                raise RequestError("当前正在生成，请等待完成后再提交。", 409)
        except RequestError as exc:
            self.json_response({"error": exc.message}, exc.status)
            return
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            try:
                for event in generate_book(config, topic, instructions, count):
                    self.write_event(event)
            except GenerationError as exc:
                self.write_event({"type": "error", "message": str(exc)})
            except Exception:
                # Never forward provider internals, credentials, or tracebacks.
                self.write_event({"type": "error", "message": "生成遇到内部错误，请检查配置后重试。"})
        except (BrokenPipeError, ConnectionResetError, TimeoutError, OSError):
            pass
        finally:
            self.server.generation_lock.release()

    def write_event(self, event):
        self.wfile.write(json.dumps(event, ensure_ascii=False).encode("utf-8") + b"\n")
        self.wfile.flush()


def create_server(host="127.0.0.1", port=8765, config=None, web_dir=WEB_DIR):
    return BookshelfServer((host, port), partial(Handler, directory=web_dir), config or ModelConfig.from_environment())


def main():
    parser = argparse.ArgumentParser(description="Infinite Bookshelf 本机研究演示")
    parser.add_argument("--host", choices=("127.0.0.1", "localhost"), default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    print(f"本机演示：http://{args.host}:{server.server_address[1]}")
    print("真实模型已配置。" if server.model_config.configured else server.model_config.reason)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n演示已停止。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
