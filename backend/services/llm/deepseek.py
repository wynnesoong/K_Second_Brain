from .openai import OpenAIProvider

class DeepSeekProvider(OpenAIProvider):
    """
    DeepSeek Implementation (Using OpenAI Compatible API)
    """
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            model_name="deepseek-chat"
        )
