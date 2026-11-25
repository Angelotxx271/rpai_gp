"""Start a service on one dual-stack socket (IPv6 and IPv4), so it answers Railway's public proxy and its
private network either way: python -m tfgpt_shared.serve web.app:create_app"""
import os
import socket
import sys

import uvicorn


def dual_stack_socket(port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    sock.bind(("::", port))
    return sock


def main() -> None:
    factory = sys.argv[1]
    port = int(os.environ.get("PORT", "8000"))
    config = uvicorn.Config(factory, factory=True, proxy_headers=True, forwarded_allow_ips="*",
                            log_level=os.environ.get("LOG_LEVEL", "info"))
    uvicorn.Server(config).run(sockets=[dual_stack_socket(port)])


if __name__ == "__main__":
    main()
