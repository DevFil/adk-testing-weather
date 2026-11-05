from google.adk.agents import Agent
from google.genai import types

from .model import local_qwen
from .tools import get_weather


root_agent = Agent(
    name="qwen_local_agent",
    model=local_qwen(),
    instruction=(
        "Sei un assistente conciso ed accurato. "
        "Usa get_weather per il meteo esterno (condizioni attuali e previsioni a 12 ore). "
        "Per le domande sulla pioggia: se la percentuale di probabilità è disponibile riportala, "
        "altrimenti usa i millimetri previsti (rain_mm) e la condizione meteo. "
        "Non inventare mai dati."
    ),
    tools=[get_weather],
    generate_content_config=types.GenerateContentConfig(
        temperature=0,
        max_output_tokens=256,
    ),
)
