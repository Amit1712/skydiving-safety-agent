"""
Central configuration for the Skydiving Safety Agent.
"""

# Default system instruction for the LLM
SYSTEM_INSTRUCTION = (
    "You are an expert Skydiving Safety Agent. "
    "Analyze safety conditions before giving a verdict. "
    "Always verify location coordinates, weather/wind conditions, and safety limits using your tools. "
    "Always end your response with a clear verdict line formatted as: 'VERDICT: [GO / NO-GO]'."
)

# Model Settings
DEFAULT_MODEL = "gemini-3.1-flash-lite"
TEMPERATURE = 0.0

# Terminal UI Settings
APP_TITLE = "🪂 Skydiving Safety Autonomous Agent"
