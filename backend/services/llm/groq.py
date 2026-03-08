from .openai import OpenAIProvider

class GroqProvider(OpenAIProvider):
    """
    Groq Implementation (Using OpenAI Compatible API)
    極速推理。
    """
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            model_name="llama3-70b-8192" # Or mixed, but Llama3 is standard
        )
