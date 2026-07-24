"""
Shared corpus for the Deduplication page.

A small corpus engineered to contain every duplicate class:
  - an original + a byte-exact copy            -> EXCLUDE_EXACT
  - a reformatted copy (same words, new punct) -> EXCLUDE_EXACT (normalized)
  - a near-copy (1 word changed, ~0.85 Jaccard) -> EXCLUDE_NEAR
  - a looser near-copy (~0.75 Jaccard)          -> removed only at aggressive
  - a long article + a verbatim snippet of it   -> containment -> STRIP/EXCLUDE
  - a Hindi doc + its English translation        -> NOT duplicates, both kept
  - unique articles + real Hindi Wikipedia       -> KEEP_CANONICAL

`expected` is the disposition at the BALANCED_NEAR bundle (level 3), verified
by the scratchpad verifier and by running the page's JS in Node.
"""

import json
import os

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
PREVIEW_CHARS = 2000
N_REAL        = 8

_ORIG = (
    "मोबाइल फोन आज हमारे जीवन का एक अनिवार्य हिस्सा बन चुका है। "
    "यह न केवल बातचीत का साधन है बल्कि सूचना और मनोरंजन का भी बड़ा स्रोत है। "
    "इंटरनेट की सुविधा ने इसे और भी उपयोगी बना दिया है। "
    "आज छोटे बच्चों से लेकर बुजुर्गों तक सभी इसका उपयोग करते हैं। "
    "हालांकि इसके अधिक उपयोग से स्वास्थ्य पर बुरा असर भी पड़ सकता है। "
    "इसलिए हमें इसका संतुलित और समझदारी भरा उपयोग करना चाहिए।"
)

# the canonical body all copies derive from (suffix makes it the longest -> canonical)
_BODY = _ORIG + " यह मूल लेख है।"

# near-copy: exactly one content word changed ("अनिवार्य" -> "ज़रूरी")
_NEAR = _BODY.replace("अनिवार्य", "ज़रूरी")

# looser near-copy: one phrase + one word reworded (targets the ~0.75 band, so
# it is removed only at the aggressive setting, not at balanced)
_NEAR2 = (_BODY
          .replace("अनिवार्य हिस्सा बन चुका है", "ज़रूरी अंग बन गया है")
          .replace("संतुलित", "सीमित"))

# reformatted: identical words, different punctuation / spacing / line breaks only
_REFORMATTED = _BODY.replace("। ", ".\n")

_LONG_P1 = (
    "भारत की जलवायु मुख्यतः मानसून पर निर्भर करती है। "
    "गर्मी के मौसम में उत्तर भारत में तापमान काफी बढ़ जाता है।"
)
_LONG_P2 = (
    "वर्षा ऋतु में जून से सितंबर के बीच अधिकांश वर्षा होती है। "
    "यह वर्षा कृषि के लिए बहुत महत्वपूर्ण मानी जाती है और फसलों को जीवन देती है।"
)
_LONG_P3 = (
    "सर्दियों में हिमालय क्षेत्र में बर्फबारी होती है और मैदानी इलाकों में ठंड बढ़ जाती है। "
    "इस प्रकार भारत में विविध प्रकार की ऋतुएँ पाई जाती हैं।"
)
_LONG = _LONG_P1 + " " + _LONG_P2 + " " + _LONG_P3
_SNIPPET = _LONG_P2   # a verbatim paragraph copied out of the long article


def _synthetic():
    out = [
        dict(id="d-orig",   title="🧪 Mobile phones (original)",
             caption="The original article. Its exact/near copies below should be removed, keeping this one.",
             expected="KEEP_CANONICAL", text=_BODY),
        dict(id="d-exact",  title="🧪 Mobile phones (exact copy)",
             caption="A byte-for-byte copy of the original — pure redundancy, drop it.",
             expected="EXCLUDE_EXACT", text=_BODY),
        dict(id="d-reformatted", title="🧪 Mobile phones (reformatted)",
             caption="Same words, only punctuation and spacing changed — identical once normalized.",
             expected="EXCLUDE_EXACT", text=_REFORMATTED),
        dict(id="d-near",   title="🧪 Mobile phones (near-copy)",
             caption="One word swapped for a synonym — a lexical near-duplicate (~85% overlap).",
             expected="EXCLUDE_NEAR", text=_NEAR),
        dict(id="d-near2",  title="🧪 Mobile phones (loosely reworded)",
             caption="Several phrases reworded — lower overlap; only the aggressive setting removes it.",
             expected="KEEP_CANONICAL", text=_NEAR2),
        dict(id="d-long",   title="🧪 Climate of India (long)",
             caption="A longer article. A snippet of it was copied elsewhere.",
             expected="KEEP_CANONICAL", text=_LONG),
        dict(id="d-snippet", title="🧪 Copied paragraph (snippet)",
             caption="One paragraph lifted verbatim from the long article — a partial copy (containment).",
             expected="STRIP_DUPLICATE_SPAN", text=_SNIPPET),
        dict(id="d-hi", title="🧪 Short note in Hindi",
             caption="A Hindi note. Its English translation is next — translations are NOT duplicates.",
             expected="KEEP_CANONICAL",
             text="कंप्यूटर आधुनिक युग का सबसे महत्वपूर्ण आविष्कार है। "
                  "यह तेज़ी से गणना करता है और लाखों कार्यों को आसान बना देता है।"),
        dict(id="d-en", title="🧪 Same note in English (translation)",
             caption="The English translation of the Hindi note — kept, because it shares almost no words.",
             expected="KEEP_CANONICAL",
             text="The computer is the most important invention of the modern age. "
                  "It calculates rapidly and makes millions of tasks easier."),
        dict(id="d-unique", title="🧪 Unique article",
             caption="Shares no substantial text with anything else — kept as-is.",
             expected="KEEP_CANONICAL",
             text="योग भारत की प्राचीन पद्धति है जो शरीर और मन को स्वस्थ रखती है। "
                  "नियमित अभ्यास से एकाग्रता बढ़ती है और तनाव कम होता है। "
                  "आज पूरी दुनिया में योग को अपनाया जा रहा है।"),
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
            if len(window) < 400:
                continue
            out.append(dict(id=a["id"], title=a["title"], url=a["url"], text=window,
                            full_len=len(a["text"]), kind="real",
                            caption="A real Hindi Wikipedia article — unique, kept.",
                            expected=None))
            if len(out) >= n:
                break
    return out


def build_sample():
    return _synthetic() + _real(JSONL_PATH, N_REAL)


if __name__ == "__main__":
    s = build_sample()
    print("Corpus: {} ({} synthetic + {} real)".format(
        len(s), sum(1 for a in s if a["kind"] == "synthetic"),
        sum(1 for a in s if a["kind"] == "real")))
    for a in s:
        print("  {:10s} {}".format(a["kind"], a["title"][:45]))
