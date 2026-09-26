import argparse
import logging

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

import config
from services.agent_service import AgentService
from services.gemini_service import GeminiService

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(debug_mode: bool):
    """Sets up application logging levels."""
    log_level = logging.DEBUG if debug_mode else logging.WARNING

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )

    loggers_to_mute = [
        "google",
        "google.genai",
        "google.genai.models",
        "google.genai.client",
        "google.auth",
        "httpx",
        "httpcore",
        "urllib3",
    ]

    for logger_name in loggers_to_mute:
        muted_logger = logging.getLogger(logger_name)
        muted_logger.setLevel(log_level)
        muted_logger.propagate = debug_mode


def display_welcome_banner():
    """Displays a styled welcome banner in the CLI."""
    banner_text = Text(config.APP_TITLE, style="bold cyan")
    console.print(Panel(banner_text, subtitle="CLI Interactive Agent", expand=False))


def display_final_answer(text: str):
    """
    Displays the final output inside a styled Rich Panel with
    dynamic text formatting and border colors based on the safety verdict (GO / NO-GO).
    """
    border_color = "cyan"
    upper_text = text.upper()

    if "VERDICT: NO-GO" in upper_text or "NO-GO" in upper_text:
        border_color = "red"
    elif "VERDICT: GO" in upper_text:
        border_color = "green"

    formatted_text = text
    if "VERDICT: GO" in formatted_text:
        formatted_text = formatted_text.replace(
            "VERDICT: GO", "VERDICT: [bold green]GO ✅[/bold green]"
        )
    elif "VERDICT: NO-GO" in formatted_text:
        formatted_text = formatted_text.replace(
            "VERDICT: NO-GO", "VERDICT: [bold red]NO-GO ❌[/bold red]"
        )

    console.print(
        Panel(
            Text.from_markup(formatted_text),
            title="[bold yellow]Agent Analysis & Safety Verdict[/bold yellow]",
            border_style=border_color,
            padding=(1, 2),
        )
    )


def handle_agent_turn(
    user_prompt: str,
    agent_service: AgentService,
    chat_session=None,
    debug_mode: bool = False,
):
    """CLI Handler: Displays UI elements and proxies the query to AgentService."""
    console.print(f"\n[bold magenta][User Query]:[/bold magenta] {user_prompt}")

    def tool_call_cb(fn_name: str, fn_args: dict):
        if debug_mode:
            console.print(
                f"[dim yellow]🤖 [Tool Call]: {fn_name}({fn_args})[/dim yellow]"
            )

    def tool_result_cb(result: str):
        if debug_mode:
            console.print(f"[dim blue]📡 [Tool Result]: {result}[/dim blue]")

    with console.status("[bold green]Analyzing...", spinner="dots") as status:

        def status_cb(msg: str):
            status.update(f"[bold green]{msg}")

        final_text, updated_session = agent_service.execute_turn(
            user_prompt=user_prompt,
            chat_session=chat_session,
            debug_mode=debug_mode,
            status_callback=status_cb,
            tool_call_callback=tool_call_cb,
            tool_result_callback=tool_result_cb,
        )

    display_final_answer(final_text)
    return updated_session


def main():
    parser = argparse.ArgumentParser(description="Skydiving Safety Agent CLI")
    parser.add_argument("-p", "--prompt", type=str, help="Prompt to ask the agent")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive mode with conversation memory",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()
    setup_logging(args.debug)
    display_welcome_banner()

    with GeminiService() as gemini_service:
        agent_service = AgentService(gemini_service)

        if args.prompt:
            handle_agent_turn(args.prompt, agent_service, debug_mode=args.debug)

        elif args.interactive:
            console.print("[dim]Type 'exit' or 'quit' to stop.\n[/dim]")

            active_chat_session = None

            while True:
                try:
                    user_input = console.input("[bold cyan][You]: [/bold cyan]").strip()
                    if not user_input:
                        continue
                    if user_input.lower() in ["exit", "quit"]:
                        console.print(
                            "\n[bold blue]Blue skies[/bold blue] & [bold yellow]safe landings! 🪂[/bold yellow]"
                        )
                        break

                    active_chat_session = handle_agent_turn(
                        user_input,
                        agent_service,
                        chat_session=active_chat_session,
                        debug_mode=args.debug,
                    )

                except KeyboardInterrupt:
                    console.print("\nExiting...")
                    break
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
