Assignment: https://assort.notion.site/Assort-Health-Assignment-Building-a-Text-Agent-28c2623b433a803f86e7eaad8f24ca29

--- Instructions for running the agent ---

Install a compatible Python (>=3.12, <4.0) if you don't have it
Install Poetry: <https://python-poetry.org/docs/#installation>

Install dependencies

`poetry install`

Create `.env`

```
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

Run the AI agent in terminal:

`poetry run python main.py`

--- Additional Notes ---

- Provider information and appointment availability is AI generated & fake
- API keys needed: OpenAI API Key and Google Maps API Key