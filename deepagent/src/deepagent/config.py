"""Central config. Loads DeepSeek + search settings from env / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()  # no-op if no .env file


@dataclass
class Settings:
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    deepseek_model: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    deepseek_temperature: float = field(
        default_factory=lambda: float(os.getenv("DEEPSEEK_TEMPERATURE", "0.2"))
    )
    deepseek_max_tokens: int = field(
        default_factory=lambda: int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096"))
    )
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    tavily_max_results: int = field(
        default_factory=lambda: int(os.getenv("TAVILY_MAX_RESULTS", "5"))
    )

    def validate(self, require_keys: bool = True) -> None:
        if require_keys and not self.deepseek_api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY is not set. "
                "Create one at https://platform.deepseek.com and export it "
                "or put it in a .env file (see .env.example)."
            )


def get_settings() -> Settings:
    settings = Settings()
    return settings
