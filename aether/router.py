import typing, types
import aether.storage.store as store
from dataclasses import dataclass
from collections.abc import Callable
import orjson, threading, asyncio
import requests, websockets, base64, os
from transformers import AutoTokenizer, TokenizersBackend, SentencePieceBackend, AutoModelForCausalLM

UNIVERSAL_ENDPOINT = "/v1/chat/completions"
STORE_PATH = "/storage/store.json"
ROUTER_STATUSES: set[str] = {"NOT ROUTING", "ROUTING", "ROUTED"}
ROUTER_LAYERS: set[str] = {"NONE", "ENTRY", "CHECK", "BROADCAST", "LOAD", "UPDATE", "API", "RESPONSE"}
CONFIG_KEYS: set[str] = ['ContextWindow', 'OperationStatus', 'RPM', 'PREFIX']

lock = asyncio.Lock()
RouterQueue: asyncio.Queue = asyncio.Queue()

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

async def UpdateRouterStatus(status: str = None, layer: str = None) -> bool:

    if (not status and not layer):
        print("No status and layer were passed.")
        return False

    await lock.acquire()

    try:

        global RouterQueue
        RouterStatus = RouterStatus()

        if (status and layer):

            await RouterQueue.put(
                {"Status": status, "Layer": layer}
            )

        elif (not layer and status):
            
            await RouterQueue.put({"Status": status})

        elif (not status and layer):

            await RouterQueue.put({"Layer": layer})

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

    global RouterQueue
    current_router_queue: dict[str, str] = await RouterQueue.get()

    if (status and layer):

        try:

            assert current_router_queue['Status'] == status
            assert current_router_queue['Layer'] == layer

            RouterQueue.task_done()

        except:
            print(f"Current Router Status: {current_router_queue['Status']}, Current Router Layer: {current_router_queue['Layer']}" )
            lock.release()
            return False

    elif (not layer and status):
        
        try:

            assert current_router_queue['Status'] == status

            RouterQueue.task_done()

        except:
            print(f"Current Router Status: {current_router_queue['Status']}")
            lock.release()
            return False
        
    elif (not status and layer):

        try:

            assert current_router_queue['Layer'] == layer

            RouterQueue.task_done()

        except:
            print(f"Current Router Layer: {current_router_queue['Layer']}")
            lock.release()
            return False


    lock.release()
    return True

async def ModelValidator(Model: str) -> TokenizersBackend | SentencePieceBackend:
    Tokenizer: any
    Model: any

    if (isinstance(Model, str) and Model.split(" ")):
        Model = Model.replace(" ", "-")

    if (Model.isupper):
        Model.lower()

    if (Model not in store.MODEL_CATALOG):

        try:

            if (AutoTokenizer.from_pretrained(Model)):
                Tokenizer = AutoTokenizer.from_pretrained(Model)
                Model = AutoModelForCausalLM.from_pretrained(Model)

        except Exception as e:
            print(e)
            import getpass
            custom_model: asyncio.Task = asyncio.create_task(getpass.getpass("Error, Model may be unknown or custom, please input the config. If no need, enter N."))
            print("Waiting for queue...")
            if (custom_model.done()):
                while (not isinstance(custom_model, str)):
                    print("Invalid input.")
                    print("Waiting for queue...")
                    custom_model: str = asyncio.create_task(getpass.getpass("Error, Model may be unknown or custom, please input the config. If no need, enter N."))

                if (custom_model == 'N'):
                    custom_model_api_endpoint: str = getpass.getpass("Enter endpoint.")
                    updated_store_memory = UpdatePyStore("Endpoint", custom_model_api_endpoint, "CUSTOM")

                updated_store_memory = UpdatePyStore("Key", dict(custom_model)['key'], "CUSTOM")
                updated_store_memory = UpdatePyStore("Endpoint", dict(custom_model)['endpoint'], "CUSTOM")

    Tokenizer = AutoTokenizer.from_pretrained(Model)
    Model = AutoModelForCausalLM.from_pretrained(Model)
    
    return (Tokenizer, Model)

class CatalogChecker:

    def __init__(self):
        self.Catalog = store.MODEL_CATALOG

    def __contains__(self, Model: str):

        if Model in self.Catalog:

            upperCaseModel = Model.upper()
            # Checks the actual python code file
            providerMetadata = getattr(store, upperCaseModel, None) 

            return providerMetadata

catalogChecker = CatalogChecker()

PROVIDER_CONFIG: any = None

async def _UpdateJSONStore(Config: str, Value: str, Model: str = None, Async: bool = True) -> bool:

    if os.path.exists(STORE_PATH):
        try:

            with open(STORE_PATH, 'w') as JSONStore:

                PROVIDER_CONFIG = orjson.loads(JSONStore.read())
                
                return True

        except orjson.JSONDecodeError:
            # dump in a file to be manually updated instead
            print(orjson.JSONDecodeError)

    return None

def UpdatePyStore(Config: str, Value: str, Model: str = None) -> bool | orjson.JSONDecodeError | AssertionError:

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

        checkedCatalog = catalogChecker.__contains__(paramToCheck)
        optCheckedCatalog = catalogChecker.__contains__(optParamToCheck)

        return [checkedCatalog, optCheckedCatalog]

    checkedCatalog = catalogChecker.__contains__(paramToCheck)

    if (checkedCatalog):
        return checkedCatalog
    else:
        return None

url = "https://github.com"
headers = {"Authorization": os.getenv("API_CALLER_KEY")} 

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

async def CallAPI(model: str, endpoint: str) -> main_dc.EnginePayload:

    if (endpoint != store.CONFIG_CATALOG[model]['Endpoint']):
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
                    UpdatePyStore(
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

def BroadcastMessage(Model: str, tokens_length: int) -> typing.Literal['RISKY', 'POTENTIAL'] | typing.Literal[False]:
    
    checked_catalog: store.APIConfig = CatalogCheck.__contains__(Model)

    if (not checked_catalog):
        return False

    if (checked_catalog.Window < tokens_length):
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

def Broadcast(Payload: PromptPayload):

    validated_model = ModelValidator(Payload.Model)
    token_length: int

    if (validated_model):
        token_length = validated_model.encode(Payload.Prompt)
    else:
        custom_bpe: object # Soon

    sent_broadcast = BroadcastMessage(Payload.Model, token_length)
    
async def Route(key: str = None, model: str = None) -> EnginePayload | types.Callable:

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
                        assert isinstance(called_api.result(), EnginePayload) == True
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
            
async def Router(Payload: main_dc.EnginePayload | PromptPayload) -> main_dc.EnginePayload:

    # Check for router status first
    status_check_routing = await ReadRouterStatus(layer='ROUTING')
    status_check_routed = await ReadRouterStatus(layer='ROUTED')

    if status_check_routing:
        return False 

    elif status_check_routed:
        await UpdateRouterStatus(status='NOT ROUTING')
    
    RoutedRequest: main_dc.EnginePayload | types.Callable = None

    if (Payload.Prompt):
        RoutedRequest: main_dc.EnginePayload | types.Callable = await Route(Payload.Key or None, Payload.Model or None)

        if isinstance(RoutedRequest, types.Callable):
            BroadcastedRequest = RoutedRequest(Payload)

        if RoutedRequest == 'DOWN':
            return False
