import pytest
from pydantic import ValidationError
from ai_api.agents import ToolDefinition, ToolRegistry


def test_tool_registry_should_load_default_tools() -> None:
    registry = ToolRegistry()

    tools = registry.list_tools()
    tool_names = [tool.name for tool in tools]

    assert registry.count() == 3
    assert "rag.retrieve" in tool_names
    assert "rag.answer" in tool_names
    assert "requirements.analyze" in tool_names


def test_tool_registry_should_get_tool_by_name() -> None:
    registry = ToolRegistry()

    tool = registry.get("rag.retrieve")

    assert tool is not None
    assert tool.name == "rag.retrieve"
    assert tool.metadata["category"] == "rag"
    assert tool.metadata["requires_llm"] is False


def test_tool_registry_should_return_none_for_unknown_tool() -> None:
    registry = ToolRegistry()

    tool = registry.get("unknown.tool")

    assert tool is None


def test_tool_registry_should_register_custom_tool() -> None:
    registry = ToolRegistry(tools=[])

    custom_tool = ToolDefinition(
        name="custom.tool",
        description="Ferramenta customizada para testes.",
        input_schema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                }
            },
            "required": ["text"],
        },
        output_schema={
            "type": "object",
            "properties": {
                "result": {
                    "type": "string",
                }
            },
        },
        metadata={
            "category": "test",
        },
    )

    registry.register(custom_tool)

    assert registry.count() == 1
    assert registry.get("custom.tool") == custom_tool


def test_tool_registry_should_reject_duplicate_tool() -> None:
    custom_tool = ToolDefinition(
        name="custom.tool",
        description="Ferramenta customizada para testes.",
    )

    registry = ToolRegistry(tools=[custom_tool])

    with pytest.raises(
        ValueError,
        match="Tool already registered: custom.tool",
    ):
        registry.register(custom_tool)


def test_tool_registry_should_reject_blank_tool_name_lookup() -> None:
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="tool_name cannot be blank"):
        registry.get("   ")


def test_tool_definition_should_reject_blank_name() -> None:
    with pytest.raises(ValidationError):
        ToolDefinition(
            name="   ",
            description="Descrição válida.",
        )
