"""
Shared sample for the Quality Filter page.

8 synthetic documents exercise every heuristic + decision path, plus real
Hindi Wikipedia articles. Imported by generate_quality_preview.py (and by the
verifier) so the page scores exactly these documents.

Every synthetic doc carries an `expected` disposition at the BALANCED_HIGH_
QUALITY (baseline, strictness 3) bundle, checked by verify_quality.py.
"""

import json
import os

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
PREVIEW_CHARS = 2500
N_REAL        = 14


def _synthetic():
    out = []

    out.append({
        "id": "q-clean-hindi",
        "title": "🧪 Clean Hindi prose",
        "caption": "Well-formed Hindi article — passes every check, the easy KEEP.",
        "expected": "ACCEPT_STANDARD",
        "text": (
            "भारत एक विशाल और विविधतापूर्ण देश है जहाँ अनेक भाषाएँ बोली जाती हैं।\n"
            "हिन्दी सबसे अधिक बोली जाने वाली भाषाओं में से एक है और इसे देवनागरी लिपि में लिखा जाता है।\n"
            "यह भाषा करोड़ों लोगों की मातृभाषा है और इसके साहित्य का इतिहास बहुत समृद्ध रहा है।\n"
            "सरकारी कामकाज तथा शिक्षा के क्षेत्र में भी हिन्दी का व्यापक रूप से उपयोग किया जाता है।\n"
            "आज हिन्दी न केवल भारत में बल्कि विश्व के कई देशों में पढ़ी और समझी जाती है।\n"
            "इस प्रकार हिन्दी भारतीय संस्कृति और पहचान का एक महत्वपूर्ण हिस्सा मानी जाती है।"
        ),
    })

    # keyword-stuffed SEO spam: same phrase and line repeated
    spam_line = "सबसे सस्ता मोबाइल फोन खरीदें सस्ता मोबाइल ऑनलाइन सस्ता मोबाइल ऑफर\n"
    out.append({
        "id": "q-seo-spam",
        "title": "🧪 SEO keyword-stuffed spam",
        "caption": "The same sales phrase repeated over and over — classic web junk.",
        "expected": "EXCLUDE_HEURISTIC",
        "text": spam_line * 8,
    })

    out.append({
        "id": "q-recipe-list",
        "title": "🧪 Recipe / bullet list",
        "caption": "A legitimate recipe that is almost all bullets — must be kept, not killed.",
        "expected": "ACCEPT_SPECIAL_FORMAT",
        "text": (
            "- सबसे पहले दो मध्यम आकार के आलू लेकर उन्हें अच्छी तरह उबाल लें\n"
            "- उबले हुए आलू को छीलकर एक बड़े बर्तन में मसल लें\n"
            "- अब उसमें नमक हरी मिर्च धनिया और गरम मसाला मिला लें\n"
            "- गेहूँ के आटे को पानी डालकर नरम गूँथ लें और थोड़ी देर रख दें\n"
            "- आटे की लोई बनाकर उसमें आलू का मिश्रण भरें और बेल लें\n"
            "- गरम तवे पर पराठे को दोनों ओर घी लगाकर सुनहरा सेक लें\n"
            "- तैयार पराठे को दही अचार या हरी चटनी के साथ गरमागरम परोसें\n"
            "- बचे हुए पराठे को कपड़े में लपेटकर गरम रखा जा सकता है"
        ),
    })

    out.append({
        "id": "q-too-short",
        "title": "🧪 Too short (caption)",
        "caption": "A single short line — valuable maybe, but too little to judge; send to review.",
        "expected": "REVIEW",
        "text": "हिन्दी भारत की एक प्रमुख भाषा है।",
    })

    out.append({
        "id": "q-symbol-gibberish",
        "title": "🧪 Symbol gibberish",
        "caption": "Mostly hashes and symbols — no real language, drop it.",
        "expected": "EXCLUDE_HEURISTIC",
        "text": (
            "### $$$ %%% @@@ ### &&& *** ### $$$ ||| ### ~~~ ### $$$ ### @@@\n"
            "#### ###### ######## ########## ############ ############## #####\n"
            "# # # ## ## ## ### ### #### #### ##### ##### ###### ###### #######\n"
            "$$$ ### $$$ ### $$$ ### $$$ ### $$$ ### $$$ ### $$$ ### $$$ ### $$$"
        ),
    })

    # conversation: short turns, lots of trailing ellipses
    out.append({
        "id": "q-chat-ellipsis",
        "title": "🧪 Chat / dialogue",
        "caption": "Informal chat with lots of ellipses — legitimate conversation, not spam.",
        "expected": "ACCEPT_SPECIAL_FORMAT",
        "text": (
            "अरे यार सुनो ज़रा इधर आओ...\n"
            "क्या हुआ भाई क्यों बुला रहे हो...\n"
            "कुछ खास नहीं बस ऐसे ही बात करनी थी...\n"
            "अच्छा ठीक है बताओ क्या बात है...\n"
            "कल शाम को कहीं घूमने चलें क्या...\n"
            "हाँ ज़रूर चलते हैं बहुत दिन हो गए...\n"
            "तो फिर पाँच बजे मिलते हैं वहीं पर...\n"
            "बिल्कुल सही रहेगा मैं समय पर पहुँच जाऊँगा...\n"
            "ठीक है फिर मिलते हैं शाम को तब तक के लिए...\n"
            "हाँ मिलते हैं अपना ध्यान रखना दोस्त..."
        ),
    })

    out.append({
        "id": "q-code",
        "title": "🧪 Code snippet",
        "caption": "Source code — prose rules don't apply; route to the code bucket.",
        "expected": "ACCEPT_SPECIAL_FORMAT",
        "text": (
            "def clean_text(text):\n"
            "    text = text.strip()\n"
            "    lines = text.split('\\n')\n"
            "    result = []\n"
            "    for line in lines:\n"
            "        if len(line) > 0:\n"
            "            result.append(line.lower())\n"
            "    return '\\n'.join(result)\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    print(clean_text('  Hello World  '))"
        ),
    })

    # navigation boilerplate repeated
    nav = "होम | संपर्क करें | हमारे बारे में | गोपनीयता नीति | नियम और शर्तें\n"
    out.append({
        "id": "q-boilerplate",
        "title": "🧪 Navigation boilerplate",
        "caption": "The same menu bar repeated on every page — duplicate lines, drop it.",
        "expected": "EXCLUDE_HEURISTIC",
        "text": nav * 6,
    })

    for a in out:
        a["url"]  = "#"
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
            if len(window) < 300:
                continue
            out.append({
                "id":       a["id"],
                "title":    a["title"],
                "url":      a["url"],
                "text":     window,
                "full_len": len(a["text"]),
                "kind":     "real",
                "caption":  "A real Hindi Wikipedia article — the everyday case.",
                "expected": None,
            })
            if len(out) >= n:
                break
    return out


def build_sample():
    return _synthetic() + _real(JSONL_PATH, N_REAL)


if __name__ == "__main__":
    s = build_sample()
    print("Sample: {} ({} synthetic + {} real)".format(
        len(s), sum(1 for a in s if a["kind"] == "synthetic"),
        sum(1 for a in s if a["kind"] == "real")))
    for a in s:
        print("  {:10s} {}".format(a["kind"], a["title"][:45]))
