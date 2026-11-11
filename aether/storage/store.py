import typing
from dataclasses import dataclass
import llm

@dataclass(slots=True)
class ContextWindow:
    Tier:   typing.Literal["Free", "Commercial", "Enterprise", "Pro", "Community"] 
    Amount: int

@dataclass(slots=True)
class OperationStatus:
    Status:     str
    LastUpdate: int

@dataclass(slots=True)
class APIConfig:
    base_url: str
    key_env: str
    auth_header: typing.Literal["Authorization"]
    auth_prefix: typing.Literal["Bearer"]
    extra_headers: dict[str, any]
    model: str
    context_window: int
    request_template: dict[str, any]
    response_path: str


GENERAL_SCHEMA = {
  "payload": {
    "messages": [{"role": "", "content": ""}],
    "temperature": 0.0,
    "max_tokens": 0
  }
}

SCHEMA_KEYWORDS = ["max", "chat"]

CUSTOM: dict[str, any] = {}

MODEL_CATALOG: set[str] = set(str)

Groq = {
  "base_url": "https://api.groq.com/openai/v1/chat/completions",
  "key_env": "GROQ_API_KEY",
  "auth_header": "Authorization",
  "auth_prefix": "Bearer ",
  "extra_headers": {},
  "model": "llama-3.3-70b-versatile",
  "context_window": 131072,
  "request_template": {"model": "{{model}}", "messages": [{"role": "user", "content": "{{prompt}}"}]},
  "response_path": "choices.0.message.content"
}

Anthropic = {
    "base_url": "https://api.anthropic.com/v1/messages",
    "key_env": "ANTHROPIC_API_KEY",
    "auth_header": "x-api-key",
    "auth_prefix": "",
    "extra_headers": {"anthropic-version": "2023-06-01"},
    "model": "claude-sonnet-4-6",
    "context_window": 200000,
    "request_template": {"model": "{{model}}", "max_tokens": 1024, "messages": [{"role": "user", "content": "{{prompt}}"}]},
    "response_path": "content.0.text"
}
