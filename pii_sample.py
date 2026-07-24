"""
Shared corpus for the PII page.

IMPORTANT: every identifier below is SYNTHETIC / fake (example.com addresses,
standard test card 4111…, obviously-fake Aadhaar/PAN/keys). The page never
displays raw PII in its detection log — it uses typed masked previews — but the
synthetic input text is shown to make detection visible, with a disclaimer.

Each doc has a `source_tier` (news / forum / email / code / leaked) and an
`expected` document disposition at the MULTILINGUAL_BALANCED policy (level 2),
verified by the scratchpad verifier and by running the page JS in Node.
"""

import json
import os

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
PREVIEW_CHARS = 2000
N_REAL        = 8


def _synthetic():
    out = [
        dict(id="pii-forum-contact", title="🧪 Forum post with contact details",
             source_tier="forum",
             caption="An email and a phone number — direct contact info, masked but the post is kept.",
             expected="KEEP_SCRUBBED",
             text="क्या किसी के पास पुरानी किताबें हैं बेचने के लिए?\n"
                  "मुझसे संपर्क करें: ravi.sharma@example.com पर या फ़ोन करें 98765 43210 पर।\n"
                  "मुझे हिंदी साहित्य की किताबें चाहिए।"),
        dict(id="pii-reddit-handle", title="🧪 Reddit comment (handle + name)",
             source_tier="forum",
             caption="A username and a private person's name — pseudonymized, post kept.",
             expected="KEEP_SCRUBBED",
             text="u/booklover_42 ने लिखा:\n"
                  "मेरी दोस्त प्रिया को भी यही किताब पसंद है। उसने मुझे सुझाई थी।\n"
                  "आप github.com/priyacodes पर उसका काम देख सकते हैं।"),
        dict(id="pii-code-secret", title="🧪 Code with a leaked secret",
             source_tier="code",
             caption="A hard-coded API key and password — a critical secret, so the whole file is quarantined.",
             expected="QUARANTINE_DOCUMENT",
             text="import boto3\n"
                  "AWS_ACCESS_KEY = 'AKIAIOSFODNN7EXAMPLE'\n"
                  "DB_PASSWORD = 'sup3rs3cret_pass'\n"
                  "client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY)\n"
                  "def upload(f): return client.upload_file(f, 'my-bucket', f)"),
        dict(id="pii-news-public", title="🧪 News article (public figure)",
             source_tier="news",
             caption="A public official quoted in the news — the name is kept for attribution; no contact info.",
             expected="KEEP_SCRUBBED",
             text="नई दिल्ली — प्रधानमंत्री अमित वर्मा ने संसद में शिक्षा नीति पर बयान दिया।\n"
                  "उन्होंने कहा कि सरकार अगले वर्ष स्कूलों की संख्या बढ़ाएगी।\n"
                  "विपक्ष ने इस घोषणा का स्वागत किया।"),
        dict(id="pii-govt-ids", title="🧪 Document with government IDs",
             source_tier="email",
             caption="An Aadhaar number and a PAN — strong identifiers; two together quarantine the document.",
             expected="QUARANTINE_DOCUMENT",
             text="आवेदन फॉर्म संलग्न है।\n"
                  "आधार संख्या: 2345 6789 0123\n"
                  "पैन कार्ड: ABCDE1234F\n"
                  "कृपया सत्यापन के बाद सूचित करें।"),
        dict(id="pii-payment-ip", title="🧪 Order note (card + IP)",
             source_tier="email",
             caption="A payment card (Luhn-valid) and an IP address — masked; a single card doesn't quarantine.",
             expected="KEEP_SCRUBBED",
             text="ऑर्डर की पुष्टि हो गई है।\n"
                  "कार्ड नंबर 4111 1111 1111 1111 से भुगतान प्राप्त हुआ।\n"
                  "अनुरोध सर्वर 203.0.113.45 से आया था।"),
        dict(id="pii-sensitive", title="🧪 Health detail about a person",
             source_tier="forum",
             caption="A private person linked to a health condition — a sensitive attribute; quarantined.",
             expected="QUARANTINE_DOCUMENT",
             text="बहुत दुख की बात है।\n"
                  "मेरे पड़ोसी अमित को कैंसर का पता चला है।\n"
                  "कृपया उनके लिए प्रार्थना करें।"),
        dict(id="pii-clean", title="🧪 Clean article (no PII)",
             source_tier="news",
             caption="No personal data at all — nothing to redact, kept as-is.",
             expected="KEEP_SCRUBBED",
             text="योग शरीर और मन को स्वस्थ रखने की प्राचीन भारतीय पद्धति है।\n"
                  "नियमित अभ्यास से एकाग्रता बढ़ती है और तनाव कम होता है।\n"
                  "आज पूरी दुनिया में योग को अपनाया जा रहा है।"),
        dict(id="pii-org-location", title="🧪 Orgs & places only",
             source_tier="news",
             caption="Only a company and cities — not people. Kept without redaction (avoids over-redaction).",
             expected="KEEP_SCRUBBED",
             text="गूगल ने भारत में अपना नया कार्यालय खोला है।\n"
                  "यह कार्यालय दिल्ली और मुंबई के बाद बेंगलुरु में स्थित है।\n"
                  "कंपनी ने स्थानीय इंजीनियरों को नौकरी देने की घोषणा की।"),
        dict(id="pii-directory", title="🧪 Contact directory (personal records)",
             source_tier="leaked",
             caption="A list of many people with their contact details — primarily a personal record; excluded.",
             expected="EXCLUDE_DOCUMENT",
             text="सदस्य सूची:\n"
                  "राहुल — rahul@example.com — 98111 22233\n"
                  "प्रिया — priya@example.com — 98222 33344\n"
                  "अमित — amit@example.com — 98333 44455\n"
                  "सुनीता — sunita@example.com — 98444 55566"),
    ]
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
            if len(window) < 400:
                continue
            out.append(dict(id=a["id"], title=a["title"], url=a["url"], text=window,
                            full_len=len(a["text"]), kind="real", source_tier="news",
                            caption="A real Hindi Wikipedia article — mostly public/encyclopedic, little to redact.",
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
        print("  {:8s} {}".format(a["source_tier"], a["title"][:45]))
