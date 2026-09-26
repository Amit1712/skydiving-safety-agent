"""
Central configuration for the Skydiving Safety Agent.
"""

# Default system instruction for the LLM
SYSTEM_INSTRUCTION = (
    "You are an expert Skydiving Safety Agent. "
    "Analyze safety conditions before giving a verdict. "
    "Always verify location coordinates, weather/wind conditions, and safety limits using your tools. "
    "When the user mentions a specific jump time, use the hourly forecast and daylight tools. "
    "For cloud ceiling and visibility, use aviation METAR data and the VMC check tool. "
    "Report wind speeds in both km/h and knots when available. "
    "Always end your response with a clear verdict line formatted as: 'VERDICT: [GO / NO-GO]'."
)

# Model Settings
DEFAULT_MODEL = "gemini-3.1-flash-lite"
TEMPERATURE = 0.0

# Terminal UI Settings
APP_TITLE = "🪂 Skydiving Safety Autonomous Agent"

# VMC (Visual Meteorological Conditions) minimums for AFF student operations
MIN_CLOUD_CEILING_FT_AGL = 3000
MIN_VISIBILITY_STATUTE_MILES = 3.0
