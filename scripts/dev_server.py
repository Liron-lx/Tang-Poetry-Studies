#!/usr/bin/env python3
"""项目开发服务器：静态服务当前目录。

端口解析优先级：
1. 命令行 `--port N`（npm run dev -- --port N 转发的参数）
2. 命令行末尾的纯数字参数（npm run dev -- N）
3. 环境变量 PORT
4. 默认 8000
"""
import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


def resolve_port(argv):
    args = list(argv)
    for i, a in enumerate(args):
        if a == "--port" and i + 1 < len(args) and args[i + 1].isdigit():
            return int(args[i + 1])
        if a.startswith("--port=") and a.split("=", 1)[1].isdigit():
            return int(a.split("=", 1)[1])
    for a in reversed(args):
        if a.isdigit():
            return int(a)
    if os.environ.get("PORT", "").isdigit():
        return int(os.environ["PORT"])
    return 8000


def main():
    port = resolve_port(sys.argv[1:])
    host = "127.0.0.1"
    for i, a in enumerate(sys.argv[1:]):
        if a == "--host" and i + 2 <= len(sys.argv[1:]):
            host = sys.argv[i + 2]
        elif a.startswith("--host="):
            host = a.split("=", 1)[1]

    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, fmt, *args):
            sys.stderr.write("[dev] " + fmt % args + "\n")

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"诗风侠影 dev server → http://{host}:{port}/index.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
