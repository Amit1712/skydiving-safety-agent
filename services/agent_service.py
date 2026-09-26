"""
Service handling agent loop orchestration, tool execution, and guardrails.
"""

import logging
from collections.abc import Callable
from typing import Any

from google.genai import types

from services.gemini_service import GeminiService
from tools.skydiving_tools import TOOLS_MAP

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    def validate_agent_output(self, output_text: str) -> str:
        """
        Guardrail check ensuring output contains an explicit VERDICT keyword
        when analyzing safety. Appends a warning if missing.
        """
        upper_text = output_text.upper()

        if "VERDICT:" in upper_text:
            return output_text

        if any(
            keyword in upper_text
            for keyword in ["NO-GO", "UNSAFE", "EXCEEDS", "NOT SAFE", "DANGER"]
        ):
            output_text += "\n\nVERDICT: NO-GO"

        # בדיקה ממוקדת ל-GO
        elif any(
            keyword in upper_text
            for keyword in [
                "SAFE TO JUMP",
                "CONDITIONS ARE SAFE",
                "FAVORABLE FOR JUMPING",
            ]
        ):
            output_text += "\n\nVERDICT: GO"

        else:
            output_text += "\n\n⚠️ [Note: Safety verdict missing from response. Please review atmospheric conditions manually.]"

        return output_text

    def execute_turn(
        self,
        user_prompt: str,
        chat_session=None,
        debug_mode: bool = False,
        status_callback: Callable[[str], None] | None = None,
        tool_call_callback: Callable[[str, dict], None] | None = None,
        tool_result_callback: Callable[[str], None] | None = None,
    ) -> tuple[str, Any]:
        """
        Executes a single conversational agent turn (ReAct loop).
        """
        if chat_session is None:
            chat_session = self.gemini_service.create_chat()

        if status_callback:
            status_callback("Thinking and analyzing prompt...")

        response = self.gemini_service.send_message(chat_session, user_prompt)

        while True:
            function_calls = response.function_calls

            if not function_calls:
                final_text = self.validate_agent_output(response.text)
                return final_text, chat_session

            for call in function_calls:
                fn_name = call.name
                fn_args = dict(call.args)

                if tool_call_callback:
                    tool_call_callback(fn_name, fn_args)

                if status_callback:
                    status_callback(f"Executing tool '{fn_name}'...")

                if fn_name in TOOLS_MAP:
                    tool_output = TOOLS_MAP[fn_name](**fn_args)
                else:
                    tool_output = (
                        f'{{"status": "error", "message": "Unknown tool: {fn_name}"}}'
                    )

                if tool_result_callback:
                    tool_result_callback(tool_output)

                if status_callback:
                    status_callback("Processing tool results with Gemini...")

                response = chat_session.send_message(
                    types.Part.from_function_response(
                        name=fn_name,
                        response={"result": tool_output},
                    )
                )
