# THIRD PARTY - HUGGINGFACE
import orjson, json, requests, base64, struct, os, typing, types
from huggingface_hub import HfApi
from huggingface_hub import login, DeviceCodeError

STANDARD_HEADERS = {'Content-Type': 'application/json'}

#WIP
def schema_adapter(request_response: dict[str, any]):
    
    usual_content_key_names: set[str] = {
      "content",  # OpenAI, Anthropic, Mistral, Groq, Together AI, Perplexity
      "text",  # Google Gemini, Cohere, Anthropic (legacy v1), AWS Bedrock
      "completion",  # Anthropic (legacy completion API), AI21
      "generation",  # Cohere (legacy generation API)
      "output",  # Replicate, Hugging Face TGI
    }
 
    response_keys = list(request_response.keys())

    for usual_key in usual_content_key_names:
      if usual_key in response_keys:
         return request_response[usual_key]
    
    key_pointer_one = 0
    key_pointer_two = len(response_keys) - 1

    current_longest_kv_len =  0
    current_longest_kv_item = None

    while (key_pointer_one < key_pointer_two):

      value = None

      if (len(request_response[response_keys[key_pointer_one]] == request_response[response_keys[key_pointer_two]])):
        if (request_response[response_keys[key_pointer_one]] in usual_content_key_names):
          return request_response[response_keys[key_pointer_one]]
        elif (request_response[response_keys[key_pointer_two]] in usual_content_key_names):
          return request_response[response_keys[key_pointer_two]]
        else:
          continue

      if (len(request_response[response_keys[key_pointer_one]]) > current_longest_kv_len):
         continue
      elif (len(request_response[response_keys[key_pointer_one]]) < current_longest_kv_len):
         current_longest_kv_len = len(request_response[response_keys[key_pointer_one]])
         current_longest_kv_item = request_response[response_keys[key_pointer_one]]
      elif (len(request_response[response_keys[key_pointer_two]]) > current_longest_kv_len):
          continue
      elif (len(request_response[response_keys[key_pointer_two]] < current_longest_kv_len)):
         current_longest_kv_len = len(request_response[response_keys[key_pointer_two]])
         current_longest_kv_item = request_response[response_keys[key_pointer_two]]

    pass

def dynamic_gen(keys_name: list[str], vals_hints: list[str]):
  '''
    A dynamic config/schema generator, used for a 
    customized request structure
    Keys: Any string
    Vals: Type hints for the keys
  '''

  if len(keys_name) != len(vals_hints):
    return "keys and val hints must have the same length"
      
  return {k: str(v) for k, v in zip(keys_name, vals_hints)}

def openai_template():

  return {
    "model": None,
    "messages": [],
    "response_format": {
        "type": "json_object",
        "json_schema": {"name": None, "schema": {}}
    },
    "stream": False
  }

async def img_handler(state: str):

  import PIL

  data: PIL.PngImagePlugin.PngImageFile

  try:

    response = requests.get(
      url="",
      headers=""
      body=""
    )

    if response.status_code == 200:
      data = PIL.ImageOpen(response.content)
    elif response.status_code != 200:
        return {"status": "status code not 200", "data": response.content.decode("utf-8")}

  except Exception as e:
    raise e

  return data

async def response_handler(endpoint: str, headers: str) -> dict[str, typing.Any] | None:

    data: dict[str, typing.Any] = None
    
    try:

      response = requests.get(
        url=endpoint, 
        headers=headers,
        timeout=5)

      if (response.elapsed.total_seconds() >= 1):
        print("Response timeout after 5 seconds.")

      if response.status_code == 200:

          loaded = orjson.loads(response.raw)
          if (isinstance(data, dict[str, any])):
            if data["content"].endswith(".png"):
               img_handler(data["content"])
            data["content"] = loaded["content"]
          elif (not isinstance(data, object)):
            return {"status": "Orjson invalid", "data": response.content.decode("utf-8")}

      elif response.status_code != 200:
          return {"status": "status code not 200", "data": response.content.decode("utf-8")}

    except Exception as e:
      raise e

    return data

async def openai_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
)  -> orjson:
  
  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

async def anthropic_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
)  -> orjson:
  
  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)
  
async def google_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def mistral_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def cohere_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def perxplexity_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def openrouter_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def groq_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def together_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def hf_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def deepinfra_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def azure_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def aws_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response

async def vertex_call(
    endpoint: str,
    prompt: str,
    api_key: str = None, 
) -> orjson:

  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)

  return response
