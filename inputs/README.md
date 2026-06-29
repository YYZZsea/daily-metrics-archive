# Daily Metrics Inputs

## Local save for exit-risk tickers

The input page can save `exit-risk/tickers.txt` directly when this local service is running:

```bash
python3 inputs/save_tickers_server.py
```

Then open:

```text
inputs/index.html
```

The service only listens on `127.0.0.1:8765` and writes to:

```text
inputs/exit-risk/tickers.txt
```

Static GitHub Pages cannot write files by itself, so each local user needs to run the save service on their own machine.
