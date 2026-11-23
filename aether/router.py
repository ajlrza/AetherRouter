import typing, types
import aether.storage.store as store
from dataclasses import dataclass
from collections.abc import Callable
import orjson, asyncio
import requests, base64, os
from storage.store import stored_models

UNIVERSAL_ENDPOINT = "/v1/chat/completions"
STORE_PATH = "/storage/store.json"
ROUTER_STATUSES: set[str] = {"NOT ROUTING", "ROUTING", "ROUTED"}
ROUTER_LAYERS: set[str] = {"NONE", "ENTRY", "CHECK", "BROADCAST", "LOAD", "UPDATE", "API", "RESPONSE"}
CONFIG_KEYS: set[str] = ['ContextWindow', 'OperationStatus', 'RPM', 'PREFIX']

lock = asyncio.Lock()
queue: asyncio.Queue = asyncio.Queue()
url = "https://github.com"
headers = {"Authorization": os.getenv("API_CALLER_KEY")} 

@dataclass(slots=True)
class PromptPayload:
    Prompt:   str
    Metadata: str
    Key:      str
    Model:    str

@dataclass(slots=True)
class RouterStatus:
    Status:         typing.Literal["NOT ROUTING", "ROUTING", "ROUTED"]
    Layer:          typing.Literal["ENTRY", "CHECK", "LOAD", "UPDATE", "API", "RESPONSE"]

@dataclass(slots=True)
class BroadcastReply:
    Status:         typing.Literal["GOOD", "RISKY"]
    Model:          str
    
class CatalogChecker:

    def __init__(self):
        self.Catalog = store.MODEL_CATALOG

    def __contains__(self, Model: str):

        if Model in self.Catalog:

            upperCaseModel = Model.upper()
            # Checks the actual python code file
            providerMetadata = getattr(store, upperCaseModel, None) 

            return providerMetadata

checker: CatalogChecker = CatalogChecker()

async def UpdateRouterStatus(status: str = None, layer: str = None) -> bool:

    if (not status and not layer):
        print("No status and layer were passed.")
        return False

    await lock.acquire()

    try:
        global queue
        RouterStatus = RouterStatus()

        if (status and layer):
            await queue.put(
                {"Status": status, "Layer": layer}
            )

        elif (not layer and status):
            await queue.put({"Status": status})

        elif (not status and layer):
            await queue.put({"Layer": layer})

    except Exception as e:
        assert e
        lock.release()
        return False

    lock.release()
    return True

async def ReadRouterStatus(status: str = None, layer: str = None) -> bool:

    if (not status and not layer):
        print("No status and layer were passed.")
        return False

    await lock.acquire()

    global queue
    current_router_queue: dict[str, str] = await queue.get()

    if (status and layer):

        try:
            assert current_router_queue['Status'] == status
            assert current_router_queue['Layer'] == layer
            queue.task_done()

        except:
            print(f"Current Router Status: {current_router_queue['Status']}, Current Router Layer: {current_router_queue['Layer']}" )
            lock.release()
            return False

    elif (not layer and status):
        
        try:
            assert current_router_queue['Status'] == status
            queue.task_done()

        except:
            print(f"Current Router Status: {current_router_queue['Status']}")
            lock.release()
            return False
        
    elif (not status and layer):

        try:
            assert current_router_queue['Layer'] == layer
            queue.task_done()

        except:
            print(f"Current Router Layer: {current_router_queue['Layer']}")
            lock.release()
            return False

    lock.release()
    return True

PROVIDER_CONFIG: any = None

async def _UpdateJSONStore(
    model: str,
    base_url: str,
    key_env: str,
    context_window: int,
    req_temp: dict[str, typing.Any],
    response_path: str,
    auth_header: typing.Literal["Authorization"] = "Authorization",
    auth_prefix: typing.Literal["Bearer"] = "Bearer",
    extra_headers: dict[str, typing.Any] | None = None,
    is_async: bool = True,
) -> None:

    if os.path.exists(STORE_PATH):

       model_config = orjson.dumps(
        base_url=base_url,
        key_env=key_env,
        model=model,
        context_window=context_window,
        request_template=req_temp,
        response_path=response_path,
        auth_header=auth_header,
        auth_prefer=auth_prefix,
        extra_headers=extra_headers
       )
     
       configs: dict[str, any] | None

       with open(STORE_PATH, 'r', encoding="utf-8") as read_store:
            configs: dict[str, any] | None = orjson.loads(read_store.read())

            if (isinstance(configs, types.NoneType)):

                with open(STORE_PATH, 'w', encoding="utf-8") as store:

                    orjson.dumps(store, {model: model_config}, indent=4)

            with open(STORE_PATH, 'w', encoding="utf-8") as store:

                configs[model] = model_config
                orjson.dumps(store, configs, indent=4)
            
    return None

def _UpdatePyStore(Config: str, Value: str, Model: str = None) -> bool | orjson.JSONDecodeError | AssertionError:

    if Config not in CONFIG_KEYS:
        raise AssertionError("Config Key does not exist")

    if Config in CONFIG_KEYS and Model:

        setattr(store, Model, Value)
        updatedConfig = getattr(store, Model, None)
        
        if updatedConfig.__getattribute__(Config) == Config:

            DoJSONNext = _UpdateJSONStore(Config, Value, Model)

            if (DoJSONNext):
                return True
  
        else:
            # dump the log somewhere the human can manually do IG
            raise AssertionError("Config was not updated in .py file")
    
    setattr(store, Config, Value)
    updatedConfig = getattr(store, Config, None)
    
    if updatedConfig.__getattribute__(Config) == Config:

        DoJSONNext = _UpdateJSONStore(Config, Value, Model)

        if (DoJSONNext):
            return True
    
        else:
            # dump the log somewhere the human can manually do IG
            raise AssertionError("Config was not updated in .py file")

def CatalogCheck(paramToCheck: str, optParamToCheck: str = None) -> typing.Any | None | list[typing.Any | None]:
    
    checkedCatalog: typing.Any | None

    if (optParamToCheck):

        checkedCatalog = checker.__contains__(paramToCheck)
        optCheckedCatalog = checker.__contains__(optParamToCheck)

        return [checkedCatalog, optCheckedCatalog]

    checkedCatalog = checker.__contains__(paramToCheck)

    if (checkedCatalog):
        return checkedCatalog
    else:
        return None

async def CheckAPI(model: str = None) -> typing.Literal['UP', 'DOWN']:

    Model: str | None

    if model:
        Model = model.upper()

    # Checks the actual python code file
    providerMetadataStatus = getattr(store, Model, None).__getattribute__('Status') 

    if providerMetadataStatus.__getattribute__('LastUpdate')  > 365:
        print("Potentially depracated AI API and Model, use at own risk.")

    if (providerMetadataStatus == 'DOWN'):
        return 'DOWN'
    
    return 'UP'

async def CallAPI(model: str, endpoint: str) -> dict[str, any]:

    if (endpoint != store.stored_models[model]['Endpoint']):
        print("Possibly invalid or outdated endpoint, sending request to check..")

        try:
            response = requests.get(f"https://{model.lower()}.com/docs")

            matching = 'endpoint'
            data = response.content.decode()
            new_endpoint = data.rfind(matching)

            if (isinstance(new_endpoint, int)):
                endpoint: str = new_endpoint

                UpdateRouterStatus(status='API', layer='UPDATE')
                updated_endpoint: asyncio.Task = asyncio.create_task(
                    _UpdatePyStore(
                        Config='Endpoint',
                        Value=endpoint,
                        Model=model
                    )
                )
                endpoint_result: bool | orjson.JSONDecodeError | AssertionError = await updated_endpoint

                if (updated_endpoint.done()):
                    endpoint_result: bool | orjson.JSONDecodeError | AssertionError = updated_endpoint.result()

                if (endpoint_result):
                    print("Successfully updated new endpoint")
                else:
                    print("Cannot update new endpoint, saving new endpoint to cache and saved later.")
            else:
                print("Error, no new endpoint found.")

        except:
            print("Model possibly not available, switch to a new model.")

    try:

        await UpdateRouterStatus(layer='API')

        response = requests.get(endpoint, headers=headers)
        data = response.json()

        if data.status_code == 200:

            await UpdateRouterStatus(layer='RESPONSE')

            encoded_content = data["content"]
            decoded_code = base64.b64decode(encoded_content).decode("utf-8")
            
            return {
                "Action": "",
                "Avatar": "",
                "Position": "",
                "World": "",
                "Metadata": {}
            }

    except:
        pass

def BroadcastMessage(Model: str, tokens_length: int) -> BroadcastReply:
    
    checked_catalog: store.APIConfig = CatalogCheck.__contains__(Model)
    reply: BroadcastReply = BroadcastReply()

    if (not checked_catalog):
        return False

    if (checked_catalog.context_window < tokens_length):
        return "RISKY"

    return "POTENTIAL"

def BroadcastListener(func: Callable, tokens_length: int):

    return  {
        'OPENAI': func('OPENAI', tokens_length),
        'ANTHROPIC': func('ANTHROPIC', tokens_length), 
        'GOOGLE': func('GOOGLE', tokens_length),
        'MISTRAL': func('MISTRAL', tokens_length),
        'COHERE': func('COHERE', tokens_length),
        'PERPLEXITY': func('PERPLEXITY', tokens_length),
        'OPENROUTER': func('OPENROUTER', tokens_length),
        'GROQ': func('GROQ', tokens_length),
        'TOGETHER': func('TOGETHER', tokens_length),
        'HF': func('HF', tokens_length),
        'DEEPINFRA': func('DEEPINFRA', tokens_length),
        'AZUREOAI': func('AZUREOAI', tokens_length),
        'AWS': func('AWS', tokens_length),
        'VERTEX': func('VERTEX', tokens_length)
    }

def Broadcast(Payload: PromptPayload) -> dict[str, any] | bool:

    validated_model = ModelValidator(Payload.Model)
    token_length: int

    if (validated_model):
        token_length = validated_model.encode(Payload.Prompt)
    else:
        custom_bpe: object # Soon

    sent_broadcast: typing.Literal['RISKY', 'POTENTIAL', False] = BroadcastMessage(Payload.Model, token_length)

    if (sent_broadcast == "RISKY" or not sent_broadcast):
        return False
    
async def Route(key: str = None, model: str = None) -> dict[str, any] | types.Callable:

    if isinstance(key, types.NoneType) and isinstance(model, types.NoneType):
        
        # Let's see which model can handle instead
        await UpdateRouterStatus(layer='BROADCAST')
        return Broadcast

    if (ReadRouterStatus(status='ROUTING') and not ReadRouterStatus(layer='RESPONSE')):
        return False
    elif (ReadRouterStatus(status='ROUTING') and ReadRouterStatus(layer='RESPONSE')):
        await UpdateRouterStatus(status='ROUTED')
    elif (ReadRouterStatus(status='NOT ROUTING') and ReadRouterStatus(status=None, layer=None) not in {"UPDATE", "LOAD", "API"}):
        await UpdateRouterStatus(status='ROUTING')
    
    if isinstance(key, str) and isinstance(model, str):

        await UpdateRouterStatus(layer='CHECK')
        checkBoth = CatalogCheck(model)

        try:
            await UpdateRouterStatus(layer='API')
            
            assert isinstance(checkBoth, list) == True, "Model configuration does not exist"
            assert all(isinstance(catalog, object) for catalog in checkBoth) == True, "Listed catalog is not an object"

            checked_for_api = asyncio.create_task(CheckAPI(checkBoth[0], checkBoth[1]))
            checked: any | None = None 

            if (checked_for_api.done()):
                try:
                    checked = checked_for_api.result()
                except Exception as e:
                    return e

            checked = checked_for_api.result()

            if (checked == 'UP'):

                called_api = asyncio.create_task(CallAPI(endpoint="https://" + model.lower() + UNIVERSAL_ENDPOINT))

                if (called_api.done()):
                    try:
                        assert isinstance(called_api.result(), dict) == True
                        return called_api.result()
                    except Exception as e:
                        assert e

            elif (checked == 'DOWN'):
                return Broadcast

        except AssertionError as e:
            print(str(e) + ", searching on huggingface... ")


    elif isinstance(key, str) and isinstance(model, types.NoneType):
        
        await UpdateRouterStatus(layer='CHECK')
        checkKey = CatalogCheck(key)

        if checkKey:

            await UpdateRouterStatus(layer='API')
            checked_for_api = asyncio.create_task(CheckAPI(checkKey))
            checked: any | None = None 

            if (checked_for_api.done()):

                try:
                    checked = checked_for_api.result()
                except Exception as e:
                    return e

            checked = checked_for_api.result()

            if (checked == 'UP'):
                called_api = asyncio.create_task(CallAPI(endpoint="https://" + model.lower() + UNIVERSAL_ENDPOINT))
                
                if (called_api.done()):

                    try:
                        assert isinstance(called_api.result(), main_dc.EnginePayload) == True
                        return called_api.result()

                    except Exception as e:
                        return e

            elif (checked == 'DOWN'):
                return Broadcast
            
async def Router(Payload: dict[str, any]) -> dict[str, any]:

    # Check for router status first
    status_check_routing = await ReadRouterStatus(layer='ROUTING')
    status_check_routed = await ReadRouterStatus(layer='ROUTED')

    if status_check_routing:
        return False 

    elif status_check_routed:
        await UpdateRouterStatus(status='NOT ROUTING')
    
    RoutedRequest: dict[str, any] | types.Callable = None

    if (Payload.Prompt):
        RoutedRequest: dict[str, any] | types.Callable = await Route(Payload.Key or None, Payload.Model or None)

        if isinstance(RoutedRequest, types.Callable):
            BroadcastedRequest = RoutedRequest(Payload)

        if RoutedRequest == 'DOWN':
            return False
