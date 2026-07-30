import asyncio
from fastmcp import Client
from ai_api.mcp_server.server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        status = await client.call_tool("get_project_status", {})
        agent_tools = await client.call_tool("list_agent_tools", {})
        specialized_agents = await client.call_tool("list_specialized_agents", {})

    print("MCP Server: Applied AI Engineering Lab")
    print()
    print("Available MCP tools:")

    for tool in tools:
        print(f"- {tool.name}")

    print()
    print("Project status:")
    print(f"- Project: {status.data['project']}")
    print(f"- Status: {status.data['status']}")
    print(f"- Current milestone: {status.data['current_milestone']}")

    print()
    print("Agent tool registry:")
    print(f"- Total tools: {agent_tools.data['total_tools']}")

    print()
    print("Specialized agents:")
    print(f"- Total agents: {specialized_agents.data['agent_count']}")

    print()
    print("M6 Copilot:")
    print("- multi-agent-qa-copilot-v1")

    for agent in specialized_agents.data["agents"]:
        print(f"- {agent['name']}")


if __name__ == "__main__":
    asyncio.run(main())
