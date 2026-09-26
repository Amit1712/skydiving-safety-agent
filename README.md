# 🪂 Skydiving Safety Agent CLI

An AI-powered autonomous agent built with the **Google GenAI SDK (`google-genai`)**, **Gemini**, and **Rich CLI**.

The agent acts as a safety officer for skydivers: it accepts weather/location prompts, autonomously invokes tool functions (ReAct pattern) via Open-Meteo APIs to evaluate wind limits and atmospheric conditions, and presents a stylized safety verdict with color-coded panels and icons.

---

## ✨ Key Features

* **ReAct Agent Architecture:** Uses Gemini function calling to orchestrate multi-step tools (dropzone geocoding, weather/wind lookup, AFF student safety limits).
* **Rich Terminal UI:** Interactive CLI with colored output panels, loading spinners, and optional debug logging.
* **Safety Guardrails & Verdict System:** Enforces explicit safety verdicts and formats clear output:
  * 🟩 **`VERDICT: GO ✅`** — Atmospheric conditions are within safe operational limits.
  * 🟥 **`VERDICT: NO-GO ❌`** — Conditions exceed maximum safety thresholds (e.g., strong wind gusts).
  * 🟨 **Clarification / Warning** — Appends a note when the model response lacks an explicit verdict.
* **Interactive & Single Query Modes:** Supports memory-persistent chat sessions (`-i`) or single-turn prompts (`-p`).

---

## 🛠️ Quick Start & Automated Setup

### Option 1: One-Click Automated Setup (Recommended)

Run the included setup script to create the virtual environment, install dependencies, and generate a `.env` file if one does not exist:

```bash
git clone https://github.com/Amit1712/skydiving-safety-agent.git
cd skydiving-safety-agent
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Installation

```bash
# 1. Clone & enter repository
git clone https://github.com/Amit1712/skydiving-safety-agent.git
cd skydiving-safety-agent

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file from sample
cp .env.sample .env
```

---

## 🔑 Environment Variables

The agent requires a `.env` file in the project root. Copy `.env.sample` or let `setup.sh` create one for you, then set your API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1/forecast
GEOCODING_BASE_URL=https://geocoding-api.open-meteo.com/v1/search
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `OPEN_METEO_BASE_URL` | Yes | Open-Meteo forecast API base URL |
| `GEOCODING_BASE_URL` | Yes | Open-Meteo geocoding API base URL |

Environment variables are loaded via `python-dotenv` in the weather and geocoding services.

---

## 🚀 Usage

Make sure your virtual environment is active (`source venv/bin/activate`):

### Interactive Chat Mode

Start an interactive session with full conversation memory:

```bash
python agent.py -i
```

### Single Prompt Mode

Run a quick query directly from the command line:

```bash
python agent.py -p "Is it safe to jump at Go Jump Dead Sea today?"
```

### Debug Mode

Enable verbose logging to observe tool calls, function execution, and API responses:

```bash
python agent.py -p "Check wind conditions for Go Jump Dead Sea" -d
```

Running `python agent.py` without `-i` or `-p` prints the CLI help.

---

## 🧰 Agent Tools

The agent has access to three function-calling tools defined in `tools/skydiving_tools.py`:

| Tool | Purpose |
|------|---------|
| `get_dz_coordinates_tool` | Resolve a dropzone or location name to latitude/longitude via Open-Meteo Geocoding |
| `get_weather_and_wind_tool` | Fetch current temperature, wind speed, and gusts for given coordinates |
| `get_aff_student_safety_limits_tool` | Return AFF student wind/gust safety thresholds (25 km/h wind, 30 km/h gusts) |

---

## 📁 Project Structure

```text
skydiving-safety-agent/
├── agent.py                    # CLI entry point, Rich UI, and argument parsing
├── config.py                   # System instructions, model settings, and app title
├── setup.sh                    # One-click environment setup script
├── requirements.txt            # Project dependencies
├── .env.sample                 # Environment variables template
├── roadmap.md                  # Planned features and product roadmap
├── services/
│   ├── agent_service.py        # ReAct loop, tool execution, and output guardrails
│   ├── gemini_service.py       # GenAI client wrapper and chat session setup
│   ├── geocoding_service.py    # Dropzone/location geocoding via Open-Meteo
│   ├── weather_service.py      # Current weather and wind data via Open-Meteo
│   └── http_client.py          # Shared HTTP client with timeout and error handling
└── tools/
    └── skydiving_tools.py      # Tool function declarations and TOOLS_MAP registry
```

---

## ⚙️ Configuration

Default settings live in `config.py`:

* **Model:** `gemini-3.1-flash-lite`
* **Temperature:** `0.0`
* **System instruction:** Requires the agent to verify location, weather, and safety limits via tools, and end every response with `VERDICT: [GO / NO-GO]`.

---

## 📦 Dependencies

* `google-genai` — Google Gemini SDK
* `rich` — Terminal UI (panels, colors, spinners)
* `python-dotenv` — Load `.env` configuration
* `requests` — HTTP calls to Open-Meteo APIs

---

## 🗺️ Roadmap

See [roadmap.md](roadmap.md) for planned enhancements, including aviation weather (METAR/TAF), hourly forecasts, license-specific safety rules, and a future FastAPI/Web UI.
