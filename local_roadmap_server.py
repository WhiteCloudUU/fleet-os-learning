#!/usr/bin/env python3
"""Serve the roadmap locally and persist browser edits to roadmap-data.json."""

import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
import webbrowser


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "roadmap-data.json"
MAX_BODY_BYTES = 10 * 1024 * 1024


def card_key(card):
    return card.get("id") or card.get("date") or card.get("title")


def merge_roadmap(disk_data, browser_data):
    browser_weeklies = {
        card_key(card): card
        for card in browser_data["weeklies"]
        if card_key(card)
    }
    used = set()
    merged_weeklies = []
    for card in disk_data.get("weeklies", []):
        key = card_key(card)
        if key in browser_weeklies:
            merged_weeklies.append(browser_weeklies[key])
            used.add(key)
        else:
            merged_weeklies.append(card)
    for card in browser_data["weeklies"]:
        key = card_key(card)
        if not key or key not in used:
            merged_weeklies.append(card)

    merged = dict(disk_data)
    merged.update(browser_data)
    merged["weeklies"] = merged_weeklies
    return merged


class RoadmapHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        if self.path != "/api/local-save":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                raise ValueError("invalid request size")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("roadmap data must be an object")
            for key in ("domains", "weeklies", "references"):
                if not isinstance(payload.get(key), list):
                    raise ValueError(f"{key} must be an array")

            disk_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            payload = merge_roadmap(disk_data, payload)
            temp_file = DATA_FILE.with_suffix(".json.tmp")
            temp_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(temp_file, DATA_FILE)
            response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.send_error(400, str(exc))
        except OSError as exc:
            self.send_error(500, f"could not write roadmap data: {exc}")

    def log_message(self, message, *args):
        print(f"[{self.log_date_time_string()}] {message % args}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="open the roadmap in the default browser")
    args = parser.parse_args()

    url = f"http://127.0.0.1:{args.port}/learning_roadmap.html"
    server = ThreadingHTTPServer(("127.0.0.1", args.port), RoadmapHandler)
    print(f"Learning Roadmap: {url}")
    print("Keep this window open. Press Ctrl+C to stop the local server.")
    if args.open:
        Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
