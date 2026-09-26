"""
Service wrapper around Google GenAI SDK.
"""

import os

from google import genai
from google.genai import types

import config
from tools.skydiving_tools import TOOLS_MAP


class GeminiService:
    def __init__(self, model_name: str = config.DEFAULT_MODEL):
        self.model_name = model_name
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=self.api_key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_chat(self):
        """
        Creates a new chat session pre-configured with system instructions,
        tools, and default generation parameters.
        """
        config_params = types.GenerateContentConfig(
            system_instruction=config.SYSTEM_INSTRUCTION,
            tools=list(TOOLS_MAP.values()),
            temperature=config.TEMPERATURE,
        )
        return self.client.chats.create(
            model=self.model_name,
            config=config_params,
        )

    def send_message(self, chat_session, message: str):
        """Sends a user message or tool response to the active chat session."""
        return chat_session.send_message(message)
