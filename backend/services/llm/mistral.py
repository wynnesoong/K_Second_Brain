from .openai import OpenAIProvider

class MistralProvider(OpenAIProvider):
    """
    Mistral Implementation (Using OpenAI Compatible API)
    """
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1",
            model_name="mistral-medium"
        )
