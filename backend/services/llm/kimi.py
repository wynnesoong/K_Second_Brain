from .openai import OpenAIProvider

class KimiProvider(OpenAIProvider):
    """
    Kimi (Moonshot) Implementation (Using OpenAI Compatible API)
    中文長文本特化。
    """
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
            model_name="moonshot-v1-8k" # Standard
        )
