'''
requirements:

pip install pydantic

Create a "Read" token at the HuggingFace website (free)

'''

from services.display import display, CYAN
from typing import Any
from pydantic import BaseModel, Field

class AiEngineConfig(BaseModel):
    engine_class: str
    properties: dict[str, Any] = Field(default_factory=dict)

class Config(BaseModel):
    aiengines: list[AiEngineConfig] = Field(default_factory=list)
    chosen_aiengine: int
    save_file: str

