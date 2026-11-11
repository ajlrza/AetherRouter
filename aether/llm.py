import orjson

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

async def api_call(
    model: str,
    endpoint: str,
    prompt: str,
    api_key: str = None, 
)  -> orjson:
  
  sdk_api: object
  hf_api: object

  exclusive_headers = {}
  exclusive_headers |= STANDARD_HEADERS

  response = response_handler(endpoint, exclusive_headers)
