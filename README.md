# 🪂 Skydiving Safety Agent CLI

An AI-powered autonomous agent built with the **Google GenAI SDK (`google-genai`)**, **Gemini**, and **Rich CLI**.

The agent acts as a safety officer for skydivers: it accepts weather/location prompts, autonomously invokes tool functions (ReAct pattern) via Open-Meteo APIs to evaluate wind limits and atmospheric conditions, and presents a stylized safety verdict with color-coded panels and icons.

---

## ✨ Key Features

* **ReAct Agent Architecture:** Uses Gemini function calling to orchestrate multi-step tools (dropzone geocoding, weather/wind lookup, METAR/TAF aviation weather, hourly forecasts, daylight checks, VMC validation, license-aware safety limits).
* **Multi-License Safety Rules (Phase 3):** Supports AFF student, License A/B, License C/D, and tandem instructor limits. Defaults to AFF student regulations when no license is specified. Per-dropzone overrides via `data/safety_rules.yaml`.
* **Advanced Meteorological Tools (Phase 2):** METAR/TAF via CheckWX, hourly jump-time forecasts, civil twilight/daylight verification, and cloud ceiling + visibility (VMC) checks.
* **Improved Dropzone Geocoding:** Curated dropzone registry, OpenStreetMap/Nominatim search, and confidence-scored results.
* **Dual Wind Units:** Wind speed and gusts reported in both km/h and knots.
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
CHECKWX_API_KEY=your_checkwx_api_key_here
CHECKWX_BASE_URL=https://api.checkwx.com
```

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `OPEN_METEO_BASE_URL` | Yes | Open-Meteo forecast API base URL |
| `GEOCODING_BASE_URL` | Yes | Open-Meteo geocoding API base URL |
| `CHECKWX_API_KEY` | For METAR/TAF/VMC | CheckWX aviation weather API key ([checkwxapi.com](https://www.checkwxapi.com/)) |
| `CHECKWX_BASE_URL` | No | CheckWX API base URL (defaults to `https://api.checkwx.com`) |

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

The agent has access to eight function-calling tools defined in `tools/skydiving_tools.py`:

| Tool | Purpose |
|------|---------|
| `get_dz_coordinates_tool` | Resolve a dropzone name via curated registry, Nominatim/OSM, and Open-Meteo with confidence scoring |
| `get_weather_and_wind_tool` | Fetch current temperature, wind speed/gusts (km/h and knots) for given coordinates |
| `get_hourly_forecast_tool` | Hourly forecast for a specific jump time (e.g. `2026-09-26T15:00`) |
| `get_aviation_weather_tool` | METAR and TAF from nearest aviation station via CheckWX |
| `get_daylight_times_tool` | Sunrise, sunset, and civil twilight for a dropzone date |
| `check_jump_daylight_tool` | Verify a planned jump time is within civil daylight hours |
| `check_vmc_conditions_tool` | Cloud ceiling and visibility check against license- and dropzone-specific VMC minimums |
| `get_safety_limits_tool` | Return wind/gust/VMC safety thresholds for a license level (defaults to AFF student) |

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
│   ├── geocoding_service.py    # Dropzone geocoding (registry + Nominatim + Open-Meteo)
│   ├── weather_service.py      # Current and hourly weather/wind via Open-Meteo
│   ├── aviation_weather_service.py  # METAR/TAF via CheckWX
│   ├── daylight_service.py     # Sunrise/sunset and civil twilight calculations
│   ├── vmc_service.py          # Cloud ceiling and visibility VMC checks
│   ├── conversions.py          # km/h ↔ knots conversion helpers
│   └── http_client.py          # Shared HTTP client with timeout and error handling
├── data/
│   ├── known_dropzones.json    # Curated dropzone registry for high-confidence geocoding
│   └── safety_rules.yaml       # License-based limits and per-dropzone safety overrides
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
* `requests` — HTTP calls to Open-Meteo, Nominatim, and CheckWX APIs
* `astral` — Sunrise/sunset and civil twilight calculations
* `PyYAML` — Load license and dropzone safety rule overrides

---

## 🗺️ Roadmap

See [roadmap.md](roadmap.md) for planned enhancements, including a future FastAPI/Web UI.
