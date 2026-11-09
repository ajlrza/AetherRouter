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
    Call: typing.Callable
    Window:     ContextWindow
    Status:     OperationStatus
    RPM:        int
    Prefix:     str
    Endpoint:   str

OAI_SCHEMA_COMPATIBLE: set(Any) = (
    OPENAI, 
    AZUREOAI, 
    GROQ, 
    TOGETHER, 
    OPENROUTER, 
    PERPLEXITY, 
    MISTRAL, 
    DEEPINFRA, 
    HF)


GENERAL_SCHEMA = {
  "payload": {
    "messages": [{"role": "", "content": ""}],
    "temperature": 0.0,
    "max_tokens": 0
  }
}

SCHEMA_KEYWORDS = ["max", "chat"]


CUSTOM: dict[str, any] = {}

OPENAI: APIConfig = {
    'Call': llm.openai_call,
    'Window': ContextWindow, # Free - 128,000 
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

ANTHROPIC: APIConfig = {
    'Call': llm.anthropic_call,
    'Window': ContextWindow, # Free -  200,000
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

GOOGLE: APIConfig = {
    'Call': llm.google_call,
    'Window': ContextWindow, # Free - 1,000,000 and 2,097,152
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

MISTRAL: APIConfig = {
    'Call': llm.mistral_call,
    'Window': ContextWindow, # Free - 128,000
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

COHERE: APIConfig = {
    'Call': llm.cohere_call,
    'Window': ContextWindow, # 128000   Standard flagship limit (Command R series up to 256,000)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

PERPLEXITY: APIConfig = {
    'Call': llm.perxplexity_call,
    'Window': ContextWindow, # 127072  Standard Sonar maximum limit (varies down to 8,192 depending on endpoint)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

OPENROUTER: APIConfig = {
    'Call': llm.openrouter_call,
    'Window': ContextWindow, # 2097152  Model Dependent (Ranges from 4,096 up to 2M for Gemini endpoints)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

GROQ: APIConfig = {
    'Call': llm.groq_call,
    'Window': ContextWindow, # 131072  Model Dependent (Typically 8k–32k; up to 131,072 for Llama 3 series)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

TOGETHER: APIConfig = {
    'Call': llm.together_call,
    'Window': ContextWindow, # 131072  Model Dependent (Standard open-source weights up to 131,072 tokens)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

HF: APIConfig = {
    'Call': llm.hf_call,
    'Window': ContextWindow, # 131072  Model Dependent (Varies widely by repository; up to 128k/131k for modern open weights)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

DEEPINFRA: APIConfig = {
    'Call': llm.deepinfra_call,
    'Window': ContextWindow, # 131072  Model Dependent (Typically matches open-source model weights up to 131,072)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

AZUREOAI: APIConfig = {
    'Call': llm.azure_call,
    'Window': ContextWindow, # 128000  Standard flagship OpenAI tier (GPT-4o/o1 series)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

AWS: APIConfig = {
    'Call': llm.aws_call,
    'Window': ContextWindow, # 300000  Model Dependent (Up to 200k for Claude 3.5, 300k for Amazon Nova flagships)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

VERTEX: APIConfig = {
    'Call': llm.vertex_call,
    'Window': ContextWindow, # 2097152  Model Dependent (Up to 2,097,152 for native Gemini 1.5/2.0 Pro)
    'Status': OperationStatus,
    'RPM': int,
    'PREFIX': "",
    'ENDPOINT': ""
}

MODEL_CATALOG: set[str] = {
  'OPENAI', 
  'ANTHROPIC', 
  'GOOGLE', 
  'MISTRAL', 
  'COHERE', 
  'PERPLEXITY',
  'OPENROUTER',
  'GROQ',
  'TOGETHER',
  'HF'
  'DEEPINFRA',
  'AZURE-OAI',
  'AWS',
  'VERTEX',
}

CONFIG_CATALOG: dict[object[str, Any]] = {
  'OPENAI': OPENAI,
  'ANTHROPIC': ANTHROPIC, 
  'GOOGLE': GOOGLE,
  'MISTRAL': MISTRAL,
  'COHERE': COHERE,
  'PERPLEXITY': PERPLEXITY,
  'OPENROUTER': OPENROUTER,
  'GROQ': GROQ,
  'TOGETHER': TOGETHER,
  'HF': HF,
  'DEEPINFRA': DEEPINFRA,
  'AZUREOAI': AZUREOAI,
  'AWS': AWS,
  'VERTEX': VERTEX
}
