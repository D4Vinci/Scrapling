from random import uniform
from asyncio import CancelledError, Task, create_task, gather, shield, sleep
from collections import deque

from anyio import CancelScope
from pydantic import Field, FiniteFloat, PositiveInt
from patchright.async_api import TimeoutError as PatchrightTimeoutError

from scrapling.core._types import (
    Optional,
    Literal,
    Union,
    TypedDict,
    TypeAliasType,
    NotRequired,
    List,
    Any,
    Annotated,
    SelectorWaitStates,
)

MouseButton = Literal["left", "right", "middle"]
NonNegativeFiniteFloat = Annotated[float, Field(ge=0, allow_inf_nan=False)]
NonEmptyString = Annotated[str, Field(min_length=1)]
_Target = TypeAliasType(
    "_Target",
    Annotated[
        Optional[NonEmptyString],
        Field(title="Target", description="Playwright selector or snapshot ref as aria-ref=<ref>."),
    ],
)
_FieldTimeout = TypeAliasType(
    "_FieldTimeout",
    Annotated[
        NonNegativeFiniteFloat, Field(title="Timeout", description="Limit per native operation in ms; 0 disables it.")
    ],
)


class _MouseTarget(TypedDict, total=False):
    target: _Target
    x: Optional[FiniteFloat]
    y: Optional[FiniteFloat]
    timeout: Annotated[
        NonNegativeFiniteFloat, Field(default=30000, description="Element timeout in ms; 0 disables it.")
    ]


class _MouseMove(_MouseTarget):
    type: Literal["move"]
    steps: NotRequired[Annotated[PositiveInt, Field(default=1, description="Mousemove events for coordinates only.")]]


class _MouseClick(_MouseTarget):
    type: Literal["click"]
    button: NotRequired[Annotated[MouseButton, Field(default="left")]]
    click_count: NotRequired[Annotated[PositiveInt, Field(default=1, description="2 for a double-click.")]]
    delay: NotRequired[
        Annotated[NonNegativeFiniteFloat, Field(default=0, description="Milliseconds between press and release.")]
    ]


class _MouseWheel(TypedDict):
    type: Literal["wheel"]
    delta_x: NotRequired[
        Annotated[FiniteFloat, Field(default=0, description="Horizontal CSS pixels; positive scrolls right.")]
    ]
    delta_y: NotRequired[
        Annotated[FiniteFloat, Field(default=0, description="Vertical CSS pixels; positive scrolls down.")]
    ]


class _TimeWait(TypedDict):
    type: Literal["wait_time"]
    milliseconds: NonNegativeFiniteFloat


class _ConditionWait(TypedDict, total=False):
    timeout: Annotated[NonNegativeFiniteFloat, Field(default=30000, description="Wait limit in ms; 0 disables it.")]


class _ElementWait(_ConditionWait):
    type: Literal["wait_element"]
    target: Annotated[NonEmptyString, Field(description="Playwright selector or aria-ref=<ref> for one element.")]
    state: NotRequired[Annotated[SelectorWaitStates, Field(default="visible", description="Hidden includes removal.")]]


class _LoadWait(_ConditionWait):
    type: Literal["wait_load"]
    state: Annotated[
        Literal["domcontentloaded", "load", "networkidle"],
        Field(description="Current document readiness; networkidle waits for 500 ms without active connections."),
    ]


class _KeyPress(TypedDict):
    type: Literal["press_key"]
    key: Annotated[
        NonEmptyString, Field(description="Key or shortcut at current focus, e.g. Enter or ControlOrMeta+A.")
    ]


class _DialogAction(TypedDict):
    type: Literal["dialog"]
    accept: Annotated[bool, Field(description="Queue one reply before its trigger; unused replies expire at call end.")]
    prompt_text: NotRequired[Annotated[str, Field(description="Text for an accepted prompt; omitted means empty.")]]


class _FormTarget(TypedDict, total=False):
    target: _Target
    timeout: Annotated[_FieldTimeout, Field(default=30000)]


class _TextFormField(_FormTarget):
    type: Literal["textbox"]
    value: str
    clear: NotRequired[
        Annotated[bool, Field(default=True, description="False types at the current caret or selection.")]
    ]


class _CheckboxFormField(_FormTarget):
    type: Literal["checkbox"]
    value: bool


class _RadioFormField(_FormTarget):
    type: Literal["radio"]
    value: Literal[True]


class _SelectFormField(_FormTarget):
    type: Literal["combobox"]
    value: Annotated[Union[str, List[str]], Field(description="Option label(s); [] clears selection.")]


BrowserAction = Annotated[
    Union[
        _MouseMove,
        _MouseClick,
        _MouseWheel,
        _TextFormField,
        _CheckboxFormField,
        _RadioFormField,
        _SelectFormField,
        _KeyPress,
        _DialogAction,
        _TimeWait,
        _ElementWait,
        _LoadWait,
    ],
    Field(discriminator="type"),
]


def _validate_actions(actions: List[BrowserAction]) -> None:
    """Validate every action target before reserving the page."""
    for index, action in enumerate(actions, 1):
        if action["type"] in ("move", "click") and (
            (action.get("target") is None) == (action.get("x") is None)
            or (action.get("x") is None) != (action.get("y") is None)
        ):
            raise ValueError(f"Action {index} ({action['type']}) needs 'target' or both 'x' and 'y', not both.")
        if action["type"] in ("textbox", "checkbox", "radio", "combobox") and action.get("target") is None:
            raise ValueError(f"Action {index} ({action['type']}) needs 'target'.")


async def _run_actions(page: Any, actions: List[BrowserAction], slowly: bool = False) -> None:
    """Run an ordered action chain on a reserved browser page."""
    replies: deque[tuple[int, _DialogAction]] = deque()
    handlers: List[Task[None]] = []
    dialog_error: Optional[RuntimeError] = None

    async def reply(dialog: Any, index: int, action: _DialogAction) -> None:
        nonlocal dialog_error
        try:
            with CancelScope(shield=True):
                if action["accept"]:
                    await dialog.accept(prompt_text=action.get("prompt_text"))
                else:
                    await dialog.dismiss()
        except Exception as exc:
            if dialog_error is None:
                dialog_error = RuntimeError(f"Action {index} (dialog) failed: {exc}")
                dialog_error.__cause__ = exc
            dialog_scope.cancel()

    def handle_dialog(dialog: Any) -> None:
        index, action = replies.popleft()
        if not replies:
            page.remove_listener("dialog", handle_dialog)
        handlers.append(create_task(reply(dialog, index, action)))

    with CancelScope() as dialog_scope:
        try:
            for index, action in enumerate(actions, 1):
                try:
                    if slowly and index > 1:
                        await sleep(uniform(0.1, 0.3))
                    if action["type"] == "dialog":
                        if not replies:
                            page.on("dialog", handle_dialog)
                        replies.append((index, action))
                    elif action["type"] == "wait_time":
                        await page.wait_for_timeout(action["milliseconds"])
                    elif action["type"] == "wait_element":
                        await page.locator(action["target"]).wait_for(
                            state=action.get("state", "visible"), timeout=action.get("timeout", 30000)
                        )
                    elif action["type"] == "wait_load":
                        await page.wait_for_load_state(action["state"], timeout=action.get("timeout", 30000))
                    elif action["type"] == "press_key":
                        await page.keyboard.press(action["key"])
                    elif action["type"] == "wheel":
                        await page.mouse.wheel(action.get("delta_x", 0), action.get("delta_y", 0))
                    else:
                        target = action.get("target")
                        timeout = action.get("timeout", 30000)
                        if action["type"] == "move" or action["type"] == "click":
                            locator = page.locator(target) if target is not None else None
                            if action["type"] == "move":
                                if locator is not None:
                                    await locator.hover(timeout=timeout)
                                else:
                                    await page.mouse.move(
                                        action.get("x"), action.get("y"), steps=action.get("steps", 1)
                                    )
                            else:
                                options = {
                                    "button": action.get("button", "left"),
                                    "click_count": action.get("click_count", 1),
                                    "delay": action.get("delay", 0),
                                }
                                try:
                                    if locator is not None:
                                        await locator.click(**options, timeout=timeout)
                                    else:
                                        await page.mouse.click(action.get("x"), action.get("y"), **options)
                                except (CancelledError, PatchrightTimeoutError) as exc:
                                    try:
                                        with CancelScope(shield=True):
                                            if not page.is_closed():
                                                await page.mouse.up(button=options["button"])
                                    except Exception as cleanup_error:
                                        raise exc from cleanup_error
                                    raise
                        else:
                            locator = page.locator(target)
                            if action["type"] == "textbox":
                                if action.get("clear", True):
                                    await locator.fill("" if slowly else action["value"], timeout=timeout)
                                if slowly and action["value"]:
                                    for character in action["value"]:
                                        await locator.press_sequentially(
                                            character, delay=uniform(50, 150), timeout=timeout
                                        )
                                elif not action.get("clear", True):
                                    await locator.press_sequentially(action["value"], timeout=timeout)
                            elif action["type"] == "combobox":
                                await locator.select_option(label=action["value"], timeout=timeout)
                            else:
                                await locator.set_checked(action["value"], timeout=timeout)
                    for handler in handlers:
                        await shield(handler)
                    handlers.clear()
                except Exception as exc:
                    raise RuntimeError(f"Action {index} ({action['type']}) failed: {exc}") from exc
        finally:
            if replies:
                page.remove_listener("dialog", handle_dialog)
            with CancelScope(shield=True):
                await gather(*handlers)
    if dialog_error is not None:
        raise dialog_error
