import pytest as py
import time, typing, types
from aether import router

def helper_fn_hints(obj: any):
    '''
        Helper function to return type hints without 
        function call per test.
    '''

    return typing.get_type_hints(obj)

def prompt_dc(prompt: str, key: str, model: str) -> router.PromptPayload:

    return router.PromptPayload(Prompt=prompt, Metadata=time.time(), Key=key, Model=model)

def test_router_stats_dc() -> bool:
    hints = helper_fn_hints(router.RouterStatus)
    assert typing.get_origin(hints["Layer"]) is typing.Literal
    assert typing.get_origin(hints["Status"]) is typing.Literal

def test_broadcast_reply_dc() -> bool:
    hints = helper_fn_hints(router.BroadcastReply)
    assert typing.get_origin(hints["Status"]) is typing.Literal
    assert isinstance(router.BroadcastReply, str) == True

def test_internal_fn_names() -> bool:

    assert getattr(router, "_UpdateJSONStore", None) != None
    assert getattr(router, "_UpdatePyStore", None) != None