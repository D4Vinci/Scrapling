from pydantic import create_model

from scrapling.core._types import SetCookieParam, TypedDict


def test_typed_dict_uses_typing_extensions():
    assert TypedDict.__module__ == "typing_extensions"


def test_set_cookie_param_typed_dict_is_pydantic_compatible():
    model = create_model("Args", cookies=(list[SetCookieParam] | None, None))
    schema = model.model_json_schema()

    assert "cookies" in schema["properties"]
