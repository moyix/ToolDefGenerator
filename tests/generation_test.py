import pytest
from tool_def_generator import ToolDefGenerator
from typing_extensions import Annotated

def test_initialization():
    # Test default initialization
    generator = ToolDefGenerator()
    assert generator.strict
    assert generator.type_map == {str: "string", int: "integer", float: "number", bool: "boolean"}

    # Test custom initialization
    custom_type_map = {str: "custom_string"}
    custom_name_mappings = [("func", "custom_func")]
    generator = ToolDefGenerator(type_map=custom_type_map, strict=False, name_mappings=custom_name_mappings)
    assert not generator.strict
    assert generator.type_map == custom_type_map
    assert generator.name_mapping == {"func": "custom_func"}


def test_generate_with_name_mapping():
    # Define test functions
    def func1():
        """Function one"""
        return "result1"

    def func2():
        """Function two"""
        return "result2"

    def func3():
        """Function three"""
        return "result3"

    # Create a ToolDescGenerator instance with a name mapping for func2
    name_mappings = [("func2", "custom_func2")]
    generator = ToolDefGenerator(name_mappings=name_mappings)

    # Generate tool descriptions
    tools_desc = generator.generate(func1, func2, func3)

    # Assert the length of the tools array
    assert len(tools_desc) == 3

    # Assert the names are as expected, especially the custom mapped one
    assert tools_desc[0]["function"]["name"] == "func1"
    assert tools_desc[1]["function"]["name"] == "custom_func2"  # Custom name for func2
    assert tools_desc[2]["function"]["name"] == "func3"

    # Additional assertions can be added to check the structure and content of the descriptions

def test_return_type_checking():
    generator = ToolDefGenerator(strict=True)

    def test_func_wrong_return_type() -> int:
        return 1

    with pytest.raises(ValueError):
        generator.generate(test_func_wrong_return_type)

def test_method_param_exclusion():
    generator = ToolDefGenerator()

    class A:
        def __init__(self):
            pass

        def instance_method(self, foo: Annotated[int, "foo"]):
            """instance_method docstring"""
            pass

        @classmethod
        def class_method(cls, bar: Annotated[int, "bar"]):
            """class_method docstring"""
            pass

        @staticmethod
        def static_method(baz: Annotated[int, "baz"]):
            """static_method docstring"""
            pass

    def regular_function(x: Annotated[int,"x"], y: Annotated[int,"y"]):
        """regular_function docstring"""
        pass

    schema = generator.generate(A.instance_method)
    assert len(schema) == 1
    assert set(schema[0]['function']['parameters']['properties'].keys()) == { 'foo' }
    schema = generator.generate(A().instance_method)
    assert len(schema) == 1
    assert set(schema[0]['function']['parameters']['properties'].keys()) == { 'foo' }
    schema = generator.generate(A.class_method)
    assert len(schema) == 1
    assert set(schema[0]['function']['parameters']['properties'].keys()) == { 'bar' }
    schema = generator.generate(A().class_method)
    assert len(schema) == 1
    assert set(schema[0]['function']['parameters']['properties'].keys()) == { 'bar' }
    schema = generator.generate(A.static_method)
    assert len(schema) == 1
    assert set(schema[0]['function']['parameters']['properties'].keys()) == { 'baz' }
    schema = generator.generate(A().static_method)
    assert len(schema) == 1
    assert set(schema[0]['function']['parameters']['properties'].keys()) == { 'baz' }
    schema = generator.generate(regular_function)
    assert len(schema) == 1
    assert set(schema[0]['function']['parameters']['properties'].keys()) == { 'x', 'y' }
