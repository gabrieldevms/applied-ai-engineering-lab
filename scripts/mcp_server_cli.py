import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
API_SRC = REPO_ROOT / "apps" / "api" / "src"

sys.path.insert(0, str(API_SRC))

from ai_api.mcp_server.server import mcp as server  # noqa: E402


mcp = server
app = server
