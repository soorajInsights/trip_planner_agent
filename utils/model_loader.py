from typing import Literal, Optional, Any

from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

from utils.config_loader import load_config


class ConfigLoader:
    def __init__(self):
        print("Loading config...")
        self.config = load_config()

    def __getitem__(self, key):
        return self.config[key]


class ModelLoader(BaseModel):
    model_provider: Literal["ollama"] = "ollama"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        self.config = ConfigLoader()

    class Config:
        arbitrary_types_allowed = True

    def load_llm(self):
        """Load and return the local Ollama LLM."""
        print("LLM loading...")
        print(f"Loading model from provider: {self.model_provider}")

        model_name = self.config["llm"]["ollama"]["model_name"]

        print(f"Loading Ollama model: {model_name}")

        llm = ChatOllama(
            model=model_name,
            base_url="http://localhost:11434",
            temperature=0,
        )

        return llm