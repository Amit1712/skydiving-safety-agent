"""Tests for AgentService guardrails and ReAct loop."""

from unittest.mock import MagicMock

import pytest


class TestValidateAgentOutput:
    def test_preserves_explicit_verdict(self, agent_service):
        text = "Wind is calm.\n\nVERDICT: GO"
        assert agent_service.validate_agent_output(text) == text

    def test_appends_no_go_from_unsafe_keywords(self, agent_service):
        result = agent_service.validate_agent_output(
            "Conditions are UNSAFE due to gusts."
        )
        assert "VERDICT: NO-GO" in result

    def test_appends_go_from_safe_keywords(self, agent_service):
        result = agent_service.validate_agent_output(
            "Conditions are SAFE TO JUMP today."
        )
        assert "VERDICT: GO" in result

    def test_appends_warning_when_verdict_missing(self, agent_service):
        result = agent_service.validate_agent_output("Here is the weather summary.")
        assert "Safety verdict missing" in result

    def test_explicit_verdict_takes_precedence_over_keywords(self, agent_service):
        text = "UNSAFE winds but VERDICT: GO"
        result = agent_service.validate_agent_output(text)
        assert result == text
        assert result.count("VERDICT:") == 1


class TestExecuteTurn:
    def _make_response(self, text=None, function_calls=None):
        response = MagicMock()
        response.text = text
        response.function_calls = function_calls or []
        return response

    def _make_tool_call(self, name, args):
        call = MagicMock()
        call.name = name
        call.args = args
        return call

    def test_returns_final_text_without_tool_calls(
        self, agent_service, mock_gemini_service
    ):
        chat = MagicMock()
        mock_gemini_service.send_message.return_value = self._make_response(
            text="All clear.\n\nVERDICT: GO"
        )

        result, session = agent_service.execute_turn("Is it safe?", chat_session=chat)

        assert "VERDICT: GO" in result
        assert session is chat
        mock_gemini_service.send_message.assert_called_once_with(chat, "Is it safe?")

    def test_creates_chat_when_none_provided(self, agent_service, mock_gemini_service):
        chat = MagicMock()
        mock_gemini_service.create_chat.return_value = chat
        mock_gemini_service.send_message.return_value = self._make_response(
            text="VERDICT: GO"
        )

        _, session = agent_service.execute_turn("Hello")

        mock_gemini_service.create_chat.assert_called_once()
        assert session is chat

    def test_executes_tool_and_continues_loop(self, agent_service, mock_gemini_service):
        chat = MagicMock()
        tool_call = self._make_tool_call(
            "get_safety_limits_tool", {"license_type": "aff_student"}
        )
        tool_response = self._make_response(function_calls=[tool_call])
        final_response = self._make_response(text="Within limits.\n\nVERDICT: GO")

        mock_gemini_service.send_message.return_value = tool_response
        chat.send_message.return_value = final_response

        result, _ = agent_service.execute_turn(
            "What are AFF limits?", chat_session=chat
        )

        assert "VERDICT: GO" in result
        chat.send_message.assert_called_once()

    def test_unknown_tool_returns_error_json(self, agent_service, mock_gemini_service):
        chat = MagicMock()
        tool_call = self._make_tool_call("nonexistent_tool", {})
        tool_response = self._make_response(function_calls=[tool_call])
        final_response = self._make_response(text="VERDICT: NO-GO")

        mock_gemini_service.send_message.return_value = tool_response
        chat.send_message.return_value = final_response

        agent_service.execute_turn("test", chat_session=chat)

        sent_part = chat.send_message.call_args[0][0]
        assert sent_part.function_response.name == "nonexistent_tool"
        assert "Unknown tool" in sent_part.function_response.response["result"]

    def test_invokes_callbacks(self, agent_service, mock_gemini_service):
        chat = MagicMock()
        tool_call = self._make_tool_call("get_safety_limits_tool", {})
        tool_response = self._make_response(function_calls=[tool_call])
        final_response = self._make_response(text="VERDICT: GO")

        mock_gemini_service.send_message.return_value = tool_response
        chat.send_message.return_value = final_response

        status_messages = []
        tool_calls = []
        tool_results = []

        agent_service.execute_turn(
            "test",
            chat_session=chat,
            status_callback=status_messages.append,
            tool_call_callback=lambda name, args: tool_calls.append((name, args)),
            tool_result_callback=tool_results.append,
        )

        assert any("Thinking" in msg for msg in status_messages)
        assert tool_calls == [("get_safety_limits_tool", {})]
        assert len(tool_results) == 1
