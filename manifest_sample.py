"""
Sample shards for the Build-Manifest capstone page.

Each shard carries a provenance record that IMPORTS the results of the seven
pipeline stages, plus license/privacy/determinism evidence. The page derives
an admission verdict from explicit gate checks (never a caller-supplied
"clean"). `expected` is the verdict at the STANDARD gate policy (level 2).
"""

STAGES = ["normalization", "language", "quality", "dedup", "pii", "decontam", "tokenizer"]


def _stages(notrun=None, unverified=None):
    notrun = set(notrun or [])
    unverified = set(unverified or [])
    out = {}
    for s in STAGES:
        if s in notrun:
            out[s] = {"status": "NOT_RUN", "verify": "NOT_APPLICABLE"}
        else:
            out[s] = {"status": "PASS", "verify": "UNVERIFIED" if s in unverified else "VERIFIED"}
    return out


def build_sample():
    return [
        dict(id="shard-clean", name="hi_wiki_0001.parquet",
             snapshot="wikimedia/20231101.hi", locator="crawl:wm-2023-11-01#0001",
             license=dict(spdx="CC-BY-SA-4.0", access="public", decision="ALLOWED"),
             content="भारत एक विशाल देश है। clean shard 0001 — normalized, deduped, scrubbed.",
             records=40000, tokens=14_500_000,
             langdist={"hi": 0.985, "en": 0.010, "und": 0.005},
             stages=_stages(),
             pii_residual=0, eval_leak=False, poison=False, repro="REPRODUCED",
             caption="Everything ran, verified, licensed, clean and reproducible — the only shard that ships.",
             expected="ADMIT"),

        dict(id="shard-unlicensed", name="webcrawl_hi_0007.parquet",
             snapshot="commoncrawl/CC-MAIN-2024-10", locator="warc:CC-2024-10#0007",
             license=dict(spdx="LicenseRef-UNKNOWN", access="public", decision="UNKNOWN"),
             content="अज्ञात लाइसेंस वाला वेब शार्ड — सामग्री साफ है पर अधिकार स्पष्ट नहीं।",
             records=22000, tokens=9_100_000,
             langdist={"hi": 0.97, "en": 0.02, "und": 0.01},
             stages=_stages(),
             pii_residual=0, eval_leak=False, poison=False, repro="REPRODUCED",
             caption="Content is clean, but the license is unknown — public availability is not permission.",
             expected="REVIEW"),

        dict(id="shard-pii", name="support_tickets_0003.parquet",
             snapshot="internal/support-2024-q1", locator="obj:support#0003",
             license=dict(spdx="LicenseRef-Internal", access="restricted", decision="ALLOWED"),
             content="ग्राहक सहायता लॉग — एक क्रेडेंशियल स्क्रबिंग के बाद भी बचा रह गया।",
             records=5000, tokens=2_000_000,
             langdist={"hi": 0.80, "en": 0.20},
             stages=_stages(),
             pii_residual=1, eval_leak=False, poison=False, repro="REPRODUCED",
             caption="One critical secret survived scrubbing — the release gate blocks any residual critical identifier.",
             expected="BLOCK"),

        dict(id="shard-eval", name="qa_pairs_0012.parquet",
             snapshot="synthetic/qa-gen-v2", locator="obj:qa#0012",
             license=dict(spdx="CC0-1.0", access="public", decision="ALLOWED"),
             content="प्रश्न-उत्तर शार्ड — इसमें एक बेंचमार्क प्रश्न उत्तर सहित लीक हुआ है।",
             records=8000, tokens=3_200_000,
             langdist={"hi": 0.90, "en": 0.10},
             stages=_stages(),
             pii_residual=0, eval_leak=True, poison=False, repro="REPRODUCED",
             caption="Decontamination found an unresolved benchmark-answer leak — blocked to protect evaluation validity.",
             expected="BLOCK"),

        dict(id="shard-repro", name="hi_news_0021.parquet",
             snapshot="news-crawl/2024-02", locator="warc:news-2024-02#0021",
             license=dict(spdx="CC-BY-4.0", access="public", decision="ALLOWED"),
             content="समाचार शार्ड — पुनः चलाने पर आउटपुट बाइट्स मेल नहीं खाए।",
             records=31000, tokens=12_000_000,
             langdist={"hi": 0.99, "en": 0.01},
             stages=_stages(),
             pii_residual=0, eval_leak=False, poison=False, repro="FAILED",
             caption="A deterministic rerun produced different bytes — provenance can't be trusted, so it's blocked.",
             expected="BLOCK"),

        dict(id="shard-notrun", name="hi_forum_0009.parquet",
             snapshot="forum-dump/2024-01", locator="obj:forum#0009",
             license=dict(spdx="CC-BY-SA-4.0", access="public", decision="ALLOWED"),
             content="फोरम शार्ड — डिकंटैमिनेशन चरण चलाया ही नहीं गया।",
             records=18000, tokens=7_400_000,
             langdist={"hi": 0.95, "en": 0.05},
             stages=_stages(notrun=["decontam"]),
             pii_residual=0, eval_leak=False, poison=False, repro="REPRODUCED",
             caption="A required stage (decontamination) never ran — routed to review, not admitted on faith.",
             expected="REVIEW"),

        dict(id="shard-unverified", name="hi_books_0015.parquet",
             snapshot="books-corpus/v3", locator="obj:books#0015",
             license=dict(spdx="CC-BY-4.0", access="public", decision="ALLOWED"),
             content="पुस्तक शार्ड — गुणवत्ता चरण का दावा तो है पर संस्करण-युक्त प्रमाण नहीं।",
             records=12000, tokens=6_100_000,
             langdist={"hi": 0.98, "en": 0.02},
             stages=_stages(unverified=["quality", "dedup"]),
             pii_residual=0, eval_leak=False, poison=False, repro="REPRODUCED",
             caption="Two stages claim a pass but carry no versioned evidence — unverified, so it's held for review.",
             expected="REVIEW"),

        dict(id="shard-poison", name="scraped_mix_0031.parquet",
             snapshot="commoncrawl/CC-MAIN-2024-18", locator="warc:CC-2024-18#0031",
             license=dict(spdx="LicenseRef-UNKNOWN", access="public", decision="UNKNOWN"),
             content="मिश्रित स्क्रैप शार्ड — इसमें संदिग्ध पॉइज़निंग पैटर्न मिले।",
             records=27000, tokens=10_500_000,
             langdist={"hi": 0.88, "en": 0.12},
             stages=_stages(),
             pii_residual=0, eval_leak=False, poison=True, repro="REPRODUCED",
             caption="Suspected data poisoning — quarantined with evidence preserved for investigation.",
             expected="QUARANTINE"),

        dict(id="shard-restricted", name="licensed_db_0002.parquet",
             snapshot="vendor/db-2024", locator="obj:vendor#0002",
             license=dict(spdx="LicenseRef-NoTrainingUse", access="restricted", decision="RESTRICTED"),
             content="वेंडर डेटाबेस शार्ड — लाइसेंस प्रशिक्षण उपयोग की अनुमति नहीं देता।",
             records=9000, tokens=3_800_000,
             langdist={"hi": 0.70, "en": 0.30},
             stages=_stages(),
             pii_residual=0, eval_leak=False, poison=False, repro="REPRODUCED",
             caption="The license explicitly prohibits training use — blocked regardless of how clean the text is.",
             expected="BLOCK"),
    ]


if __name__ == "__main__":
    s = build_sample()
    print("Shards:", len(s))
    for a in s:
        print("  {:18s} exp {}".format(a["id"], a["expected"]))
