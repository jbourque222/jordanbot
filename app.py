import os, random, requests
from flask import Flask, request

GROUPME_BOT_ID = os.environ.get("GROUPME_BOT_ID")
TRIGGER_WORDS = [w.strip().lower() for w in os.environ.get("TRIGGER_WORDS", "!jboss,@jbossbot").split(",")]
CORPUS_PATH = os.environ.get("CORPUS_PATH", "corpus.txt")
GROUPME_POST_URL = "https://api.groupme.com/v3/bots/post"

app = Flask(__name__)
_quotes = []

def load_corpus():
    global _quotes
    try:
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            _quotes = [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        _quotes = []
load_corpus()

def send_message(text):
    if not GROUPME_BOT_ID:
        print("Missing GROUPME_BOT_ID")
        return
    try:
        requests.post(GROUPME_POST_URL, json={"bot_id": GROUPME_BOT_ID, "text": text[:999]}, timeout=5)
    except Exception as e:
        print("post error:", e)

def is_trigger(text):
    t = (text or "").lower()
    return any(w in t for w in TRIGGER_WORDS)

@app.route("/hook", methods=["POST"])
def hook():
    data = request.get_json(force=True)
    if data.get("sender_type") == "bot":
        return "ok", 200
    text = data.get("text") or ""
    if not is_trigger(text):
        return "ok", 200
    if not _quotes:
        send_message("no quotes loaded yet")
        return "ok", 200
    send_message(random.choice(_quotes))
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))