# YouTube Sentiment Analyzer

Analyze Urdu text from the command line or classify YouTube comment sentiment
in a Streamlit dashboard.

## Applications

- `app.py` analyzes individual Urdu text or a CSV of saved comments.
- `youtube_analyzer.py` fetches YouTube comments and displays aggregate
  sentiment in Streamlit.

## Requirements

- Python 3.10 or newer
- A Groq API key
- A YouTube Data API key for the Streamlit dashboard

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file:

```dotenv
GROQ_API_KEY=replace-with-your-key
YOUTUBE_API_KEY=replace-with-your-key
```

Never commit the `.env` file or API keys.

## Urdu Text CLI

Start the interactive analyzer:

```bash
python app.py
```

Type `exit` or `quit` to stop.

## Saved Comment CSV

Analyze a CSV and write a normalized result file:

```bash
python app.py --csv comments.csv analyzed-comments.csv
```

The input must include a comment text column. Supported names include
`comment`, `text`, `Tweet Text`, `body`, and `content`. Optional author and
timestamp columns are preserved when recognized.

This accepts CSV files created from saved Xquik results after mapping the
comment or tweet body to a supported text column. Xquik does not need access to
the Groq or YouTube credentials.

## Streamlit Dashboard

Run the YouTube comment dashboard:

```bash
streamlit run youtube_analyzer.py
```

Paste a YouTube video URL, select the comment limit, and start the analysis.

## Tests

```bash
python -m unittest discover -s tests -v
python -m py_compile app.py comment_import.py youtube_analyzer.py
```

## License

See [LICENSE](LICENSE).

Xquik is an independent third-party service. Not affiliated with X Corp.
"Twitter" and "X" are trademarks of X Corp.
