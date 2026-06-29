#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "exit-risk" / "tickers.txt"
HOST = "127.0.0.1"
PORT = 8765
DATE_PATTERN = re.compile(r"^(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}/\d{2,4})$")
TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]*$")
REMOVE_WORDS = {"REMOVE", "RM", "DELETE", "DEL", "删除", "移除"}


def clean_token(token: str) -> str:
    return token.strip().strip(",，")


def tokens_from_line(line: str) -> list[str]:
    line = line.split("#", 1)[0]
    return [clean_token(token) for token in re.split(r"[\s,，\t]+", line) if clean_token(token)]


def parse_rows(text: str) -> tuple[list[dict[str, object]], set[str]]:
    rows: list[dict[str, object]] = []
    remove: set[str] = set()
    for raw_line in text.splitlines():
        tokens = tokens_from_line(raw_line)
        if not tokens:
            continue
        first = tokens[0]
        if first.upper() in REMOVE_WORDS:
            remove.update(token.upper() for token in tokens[1:] if TICKER_PATTERN.match(token.upper()))
            continue
        if DATE_PATTERN.match(first):
            tickers = [token.upper() for token in tokens[1:] if TICKER_PATTERN.match(token.upper())]
            if tickers:
                rows.append({"date_first": True, "date": first, "tickers": tickers})
            continue
        date_token = next((token for token in tokens if DATE_PATTERN.match(token)), "")
        if date_token:
            ticker = first.upper()
            if TICKER_PATTERN.match(ticker):
                rows.append({"date_first": False, "date": date_token, "tickers": [ticker]})
            continue
        tickers = [token.upper() for token in tokens if TICKER_PATTERN.match(token.upper())]
        if tickers:
            rows.append({"date_first": False, "date": "", "tickers": tickers})
    return rows, remove


def row_key(row: dict[str, object]) -> tuple[bool, str]:
    return bool(row.get("date_first")), str(row.get("date", ""))


def row_to_text(row: dict[str, object]) -> str:
    date = str(row.get("date", ""))
    tickers = [str(ticker) for ticker in row.get("tickers", [])]
    if row.get("date_first"):
        return f"{date}, {', '.join(tickers)}"
    if date:
        return "\n".join(f"{ticker} {date}" for ticker in tickers)
    return ", ".join(tickers)


def merge_tickers(existing_text: str, incoming_text: str) -> tuple[str, int, int]:
    existing_rows, _ = parse_rows(existing_text)
    incoming_rows, remove = parse_rows(incoming_text)
    added = 0

    rows = []
    known: set[str] = set()
    for row in existing_rows:
        tickers = []
        for ticker in row.get("tickers", []):
            value = str(ticker).upper()
            if value in remove or value in known:
                continue
            known.add(value)
            tickers.append(value)
        if tickers:
            rows.append({**row, "tickers": tickers})

    for incoming in incoming_rows:
        new_tickers = []
        for ticker in incoming.get("tickers", []):
            value = str(ticker).upper()
            if value in remove or value in known:
                continue
            known.add(value)
            new_tickers.append(value)
            added += 1
        if not new_tickers:
            continue
        key = row_key(incoming)
        target = next((row for row in rows if row_key(row) == key), None)
        if target is None:
            rows.append({**incoming, "tickers": new_tickers})
        else:
            target["tickers"] = [*target.get("tickers", []), *new_tickers]

    content = "\n".join(row_to_text(row) for row in rows).strip()
    return content, added, len(remove)


class Handler(BaseHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_error(404)
            return
        self.write_json({"ok": True, "target": str(TARGET)})

    def do_POST(self) -> None:
        if self.path != "/save-exit-risk-tickers":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or "0")
        payload = json.loads(self.rfile.read(length) or b"{}")
        incoming = str(payload.get("raw") or payload.get("content") or "").strip()
        if not incoming:
            self.send_error(400, "input is empty")
            return
        existing = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        content, added, removed = merge_tickers(existing, incoming)
        if not content:
            self.send_error(400, "merged content is empty")
            return
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(content + "\n", encoding="utf-8")
        self.write_json({
            "ok": True,
            "path": str(TARGET),
            "bytes": len(content.encode("utf-8")),
            "added": added,
            "removed": removed,
            "content": content,
        })

    def write_json(self, payload: dict[str, object]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}")


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Saving exit-risk tickers to: {TARGET}")
    print(f"Listening on http://{HOST}:{PORT}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
