from ai_api.mcp_server.server import mcp


def test_mcp_server_entrypoint_should_be_importable() -> None:
    assert mcp is not None
