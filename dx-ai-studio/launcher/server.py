"""Minimal launcher server factory for test harness use."""
from http.server import ThreadingHTTPServer

from launcher.launcher import LauncherHandler


def create_server(port=8100):
    """Return a ThreadingHTTPServer bound to *port* (0 for ephemeral)."""
    srv = ThreadingHTTPServer(("127.0.0.1", port), LauncherHandler)
    srv.daemon_threads = True
    return srv
