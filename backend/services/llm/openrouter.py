from .openai import OpenAIProvider

class OpenRouterProvider(OpenAIProvider):
    """
    OpenRouter Implementation (Using OpenAI Compatible API)
    """
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            model_name="mistralai/mistral-7b-instruct:free" # Or let user config via env later
        )
