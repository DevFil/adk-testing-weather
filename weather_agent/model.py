import os

from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm, LiteLLMClient

load_dotenv()
os.environ.setdefault("OPENAI_API_BASE", "http://localhost:11435/v1")
os.environ.setdefault("OPENAI_API_KEY", "ollama")

#disattiva thinking per aumentare la velocità del modello
class NoThinkingClient(LiteLLMClient):
    async def acompletion(self, model, messages, tools, **kwargs):
        kwargs["reasoning_effort"] = "none"
        allowed = list(kwargs.get("allowed_openai_params") or [])
        kwargs["allowed_openai_params"] = [*allowed, "reasoning_effort"]
        return await super().acompletion(model, messages, tools, **kwargs)


def local_qwen() -> LiteLlm:
    model_id = os.getenv("MODEL_ID", "qwen3.5:4b")
    return LiteLlm(
        model=f"openai/{model_id}",
        llm_client=NoThinkingClient(),
    )
