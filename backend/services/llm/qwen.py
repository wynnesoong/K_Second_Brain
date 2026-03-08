from .openai import OpenAIProvider

class QwenProvider(OpenAIProvider):
    """
    Qwen (Alibaba) Implementation (Using OpenAI Compatible API via DashScope)
    中文語意理解精準。
    """
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name="qwen-turbo" # Default
        )
