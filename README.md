# Elyx Health – Member Journey

An interactive Streamlit application for visualizing and analyzing health coaching conversations. This app transforms JSON-based member–team chat histories into an intuitive interface including WhatsApp-style chat views, decision tracking, recovery insights and Sankey rationale flows.

## Overview

Elyx Health Member Journey is designed to help health coaches and wellness specialists analyze client interactions efficiently. Key capabilities include:

- Chat visualization in a conversational (WhatsApp-like) dark-mode UI.
- Sankey flow representation of Cause → Actor → Decision pathways.
- Automated extraction and tagging of key decisions.
- Parsing average recovery percentages from chat logs.
- Sidebar display of member profile with goals and metrics.
- Export options for conversation and decision data in JSON/CSV formats.

## Features

- **Dark-Mode Chat UI**: Conversational layout with sender names, icons, timestamps, and date separators.
- **Sankey Rationale Visualization**: Dynamic mapping of conversation logic and decision flows.
- **Decision Tagging & Filtering**: Searchable, filterable lists of key decisions with timestamps, types, tags, and contexts.
- **Recovery Metrics**: Automatic extraction of average recovery percentages from chat.
- **Member Profile Sidebar**: Displays personal details, goals, and success metrics.
- **Data Export**: Easy-to-use buttons to download conversation or decision data.

## Project Structure

```
elyx-health/
│── streamlit_app.py          # Core Streamlit application
│── elyx_conversations/       # JSON conversation files (e.g., 2025-04.json, 2025-05.json, …)
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation
```

## Installation

1. Clone the repository:
   ```bash
   
   cd elyx-health
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate     # macOS/Linux
   venv\Scripts\activate        # Windows
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Add your conversation JSON files inside `elyx_conversations/`. Each file should contain an array of message objects:
   ```json
   [
     {
       "sender": "Ruby",
       "text": "Let's update your plan with more protein.",
       "timestamp": "2025-07-12 10:45:00"
     },
     {
       "sender": "Rohan Patel",
       "text": "Sounds good!",
       "timestamp": "2025-07-12 10:46:00"
     }
   ]
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

3. Visit the app in your browser at:
   ```
   http://localhost:8501
   ```

## Extensibility

- **Decision rules**: Customize detection patterns by editing `_DECISION_RULES` in `streamlit_app.py`.
- **Role icons**: Modify icons for team members through the `ROLE_ICON` mapping.
- **Styling**: Adjust the header or chat design via the CSS blocks in the `render_professional_header()` function.

## Contributing

Contributions and feedback are welcome. To contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make your changes and commit:
   ```bash
   git commit -m "Add feature: description"
   ```
4. Push your branch:
   ```bash
   git push origin feature/YourFeature
   ```
5. Open a Pull Request for review.


