"""
Shared language-analysis sample.

Both generate_language_preview.py (browser page) and run_lid.py (Python LID
tier) import build_sample() so they score the EXACT same articles. Every
article carries a claimed label as if it came from the Hindi Wikipedia dump
(claimed_lang="hi", claimed_script="Deva") — the audit's job is to test that
claim against detected evidence, per Language_Skill.md.

Synthetic articles deliberately exercise every decision path:
  - clean Hindi                -> ACCEPT_MONOLINGUAL
  - Hindi + English code-mix   -> ACCEPT_CODE_MIXED
  - romanized Hindi (Latin)    -> REVIEW (Latin != English trap)
  - English mislabeled hi      -> QUARANTINE_MISMATCH / EXCLUDE_NON_TARGET
  - Urdu (Perso-Arabic)        -> SCRIPT_LANGUAGE_CONFLICT
  - Sanskrit shloka (Deva)     -> REVIEW (shared-script ambiguity)
  - Tamil mislabeled hi        -> QUARANTINE_MISMATCH
  - symbols/numbers only       -> EXCLUDE_NON_LINGUISTIC (zxx)
"""

import json
import os
import re

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
PREVIEW_CHARS = 2000
N_REAL        = 17   # real Wikipedia articles to include


# ---------------------------------------------------------------------------
# Synthetic examples — every field is real printable Unicode (no control bytes)
# ---------------------------------------------------------------------------

def _synthetic():
    out = []

    out.append({
        "id": "syn-hi-clean",
        "title": "🧪 Clean Hindi (monolingual)",
        "text": (
            "भारत एक विशाल और विविधतापूर्ण देश है। यहाँ अनेक भाषाएँ, धर्म और "
            "संस्कृतियाँ सदियों से एक साथ फलती-फूलती रही हैं। हिन्दी देश की "
            "सबसे अधिक बोली जाने वाली भाषाओं में से एक है और इसे देवनागरी लिपि "
            "में लिखा जाता है। यह अनुच्छेद पूरी तरह से हिन्दी में है।"
        ),
        "expected": "ACCEPT_MONOLINGUAL",
    })

    out.append({
        "id": "syn-hi-en-codemix",
        "title": "🧪 Hindi–English code-mix",
        "text": (
            "आज हम machine learning के बारे में बात करेंगे। यह एक powerful "
            "technology है जो training data से patterns सीखती है। Neural "
            "networks और deep learning ने natural language processing को "
            "बदल दिया है। इस tutorial में हम पूरी pipeline को step by step "
            "समझेंगे। सबसे पहले dataset को clean करेंगे, फिर model को train "
            "करेंगे और अंत में accuracy और loss को validation set पर measure "
            "करेंगे। यह पूरी तरह hands-on approach है।"
        ),
        "expected": "ACCEPT_CODE_MIXED",
    })

    out.append({
        "id": "syn-hi-romanized",
        "title": "🧪 Romanized Hindi (Latin script)",
        "text": (
            "Namaste doston! Aaj ke is video mein hum baat karenge ki kaise "
            "aap apni Hindi ko behtar bana sakte hain. Yeh bahut aasan hai "
            "aur koi bhi ise seekh sakta hai. Agar aapko yeh pasand aaye toh "
            "like aur subscribe zaroor karein. Dhanyavaad!"
        ),
        "expected": "REVIEW",
    })

    out.append({
        "id": "syn-en-mislabeled",
        "title": "🧪 English mislabeled as Hindi",
        "text": (
            "The Indus Valley Civilisation was one of the earliest urban "
            "cultures in the world. Its well-planned cities, advanced "
            "drainage systems, and standardized weights reflect a highly "
            "organized society. This entire paragraph is written in English, "
            "yet it was filed under the Hindi corpus folder."
        ),
        "expected": "EXCLUDE_NON_TARGET",
    })

    out.append({
        "id": "syn-ur-arabic",
        "title": "🧪 Urdu (Perso-Arabic script)",
        "text": (
            "اردو جنوبی ایشیا کی ایک اہم زبان ہے جو نستعلیق رسم الخط میں لکھی "
            "جاتی ہے۔ یہ عبارت مکمل طور پر اردو میں ہے، حالانکہ اسے ہندی فولڈر "
            "میں رکھا گیا تھا۔ یہ اسکرپٹ اور زبان کے تضاد کی مثال ہے۔"
        ),
        "expected": "QUARANTINE_MISMATCH",
    })

    out.append({
        "id": "syn-sa-shloka",
        "title": "🧪 Sanskrit shloka (shared Devanagari)",
        "text": (
            "सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः। "
            "सर्वे भद्राणि पश्यन्तु मा कश्चिद्दुःखभाग्भवेत्॥ "
            "ॐ शान्तिः शान्तिः शान्तिः॥ एषा संस्कृतभाषायाः "
            "प्रसिद्धा प्रार्थना अस्ति, या देवनागरीलिप्यां लिखिता।"
        ),
        "expected": "REVIEW",
    })

    out.append({
        "id": "syn-ta-mislabeled",
        "title": "🧪 Tamil mislabeled as Hindi",
        "text": (
            "தமிழ் ஒரு தொன்மையான மொழி. இது தமிழ்நாடு, இலங்கை மற்றும் "
            "சிங்கப்பூர் உள்ளிட்ட பல இடங்களில் பேசப்படுகிறது. இந்த பத்தி "
            "முழுவதும் தமிழில் உள்ளது, ஆனால் இது இந்தி கோப்பகத்தில் "
            "வைக்கப்பட்டது."
        ),
        "expected": "QUARANTINE_MISMATCH",
    })

    out.append({
        "id": "syn-zxx-symbols",
        "title": "🧪 Symbols / numbers only (no language)",
        "text": (
            "123 456 789 | 2024-07-24 | ₹ 12,499.00 | 45% | +91-98765-43210 "
            "| #### **** ---- | () [] {} <> | $$$ €€€ | 3.14159 | 0xFF 0b1010 "
            "| ::: ;;; ,,, ... | ▲ ● ■ ◆ | 100/100"
        ),
        "expected": "EXCLUDE_NON_LINGUISTIC",
    })

    for a in out:
        a["url"]            = "#"
        a["claimed_lang"]   = "hi"
        a["claimed_script"] = "Deva"
        a["kind"]           = "synthetic"
        a["text"]           = a["text"][:PREVIEW_CHARS]
        a["full_len"]       = len(a["text"])
    return out


# ---------------------------------------------------------------------------
# Real Hindi Wikipedia articles
# ---------------------------------------------------------------------------

_LATIN = re.compile(r"[A-Za-z]")


def _real(path, n):
    """Prefer real articles that contain some Latin text (to show incidental
    foreign / script mixing), then fill with ordinary ones."""
    mixed, plain, seen = [], [], set()
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            if a["id"] in seen:
                continue
            seen.add(a["id"])
            window = a["text"][:PREVIEW_CHARS]
            if len(window) < 200:
                continue
            latin_ratio = len(_LATIN.findall(window)) / max(1, len(window))
            rec = {
                "id":             a["id"],
                "title":          a["title"],
                "url":            a["url"],
                "text":           window,
                "full_len":       len(a["text"]),
                "claimed_lang":   "hi",
                "claimed_script": "Deva",
                "kind":           "real",
            }
            if 0.02 < latin_ratio < 0.30:   # some Latin, still Hindi-dominant
                mixed.append(rec)
            else:
                plain.append(rec)
            if len(mixed) >= n and len(plain) >= n:
                break

    result = mixed[: n // 2] + plain[: n - len(mixed[: n // 2])]
    return result[:n]


def build_sample():
    """Return [synthetic..., real...]; each article is a dict with id, title,
    url, text, full_len, claimed_lang, claimed_script, kind."""
    return _synthetic() + _real(JSONL_PATH, N_REAL)


if __name__ == "__main__":
    s = build_sample()
    print("Sample size: {} ({} synthetic + {} real)".format(
        len(s),
        sum(1 for a in s if a["kind"] == "synthetic"),
        sum(1 for a in s if a["kind"] == "real"),
    ))
    for a in s:
        print("  {:12s} {}".format(a["kind"], a["title"][:50]))
