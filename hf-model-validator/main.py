import asyncio, typing
from transformers import AutoTokenizer, TokenizersBackend, SentencePieceBackend, AutoModelForCausalLM

async def ModelValidator(store: set[str], Model: str, Update: typing.Callable) -> TokenizersBackend | SentencePieceBackend:
    Tokenizer: any
    Model: any

    if (isinstance(Model, str) and Model.split(" ")):
        Model = Model.replace(" ", "-")

    if (Model.isupper):
        Model.lower()

    if (Model not in store):

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
                    updated_store_memory = Update("Endpoint", custom_model_api_endpoint, "CUSTOM")

                updated_store_memory = Update("Key", dict(custom_model)['key'], "CUSTOM")
                updated_store_memory = Update("Endpoint", dict(custom_model)['endpoint'], "CUSTOM")

    Tokenizer = AutoTokenizer.from_pretrained(Model)
    Model = AutoModelForCausalLM.from_pretrained(Model)
    
    return (Tokenizer, Model)