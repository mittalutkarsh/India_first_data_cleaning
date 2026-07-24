"""
Shared sample for the Tokenizer / fertility page.

Documents chosen to expose the 'Indic tax': the same idea costs far more
tokens in Devanagari/Tamil than in English under an English-centric byte
tokenizer, because each Indic character is 3 UTF-8 bytes.
"""

import json
import os

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
PREVIEW_CHARS = 600
N_REAL        = 6


def _synthetic():
    out = [
        dict(id="tk-hindi", title="🧪 Pure Hindi", lang="hi",
             caption="Plain Hindi. Watch how many tokens an English-centric tokenizer needs for it.",
             text="भारत एक विशाल देश है और यहाँ अनेक भाषाएँ बोली जाती हैं।"),
        dict(id="tk-english", title="🧪 Pure English", lang="en",
             caption="The same kind of sentence in English — the tokenizer was built for this, so it's cheap.",
             text="India is a vast country and many languages are spoken here."),
        dict(id="tk-hinglish", title="🧪 Hindi + English mix", lang="hi",
             caption="Code-mixed text — the English words are cheap, the Hindi words are expensive.",
             text="आज हम machine learning और deep learning के बारे में सीखेंगे।"),
        dict(id="tk-tamil", title="🧪 Tamil", lang="ta",
             caption="Another Indic script — the same 3-bytes-per-character tax applies.",
             text="தமிழ் ஒரு பழமையான மொழி; இது பல நாடுகளில் பேசப்படுகிறது."),
        dict(id="tk-code", title="🧪 Code snippet", lang="code",
             caption="ASCII code tokenizes efficiently — mostly one token per short piece.",
             text="def add(a, b):\n    return a + b\nprint(add(2, 3))"),
        dict(id="tk-numbers", title="🧪 Numbers & symbols", lang="other",
             caption="Digits and punctuation — cheap in bytes, but each digit is often its own token.",
             text="2024-07-24  ₹12,499.00  #### 3.14159  100%  (a+b)=c"),
    ]
    for a in out:
        a["url"] = "#"
        a["kind"] = "synthetic"
        a["text"] = a["text"][:PREVIEW_CHARS]
        a["full_len"] = len(a["text"])
    return out


def _real(path, n):
    if not os.path.exists(path):
        return []
    out, seen = [], set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            if a["id"] in seen:
                continue
            seen.add(a["id"])
            window = a["text"][:PREVIEW_CHARS]
            if len(window) < 200:
                continue
            out.append(dict(id=a["id"], title=a["title"], url=a["url"], text=window,
                            full_len=len(a["text"]), kind="real", lang="hi",
                            caption="A real Hindi Wikipedia article — the everyday case for the corpus."))
            if len(out) >= n:
                break
    return out


def build_sample():
    return _synthetic() + _real(JSONL_PATH, N_REAL)


if __name__ == "__main__":
    s = build_sample()
    print("Tokenizer sample: {} ({} synthetic + {} real)".format(
        len(s), sum(1 for a in s if a["kind"] == "synthetic"),
        sum(1 for a in s if a["kind"] == "real")))
