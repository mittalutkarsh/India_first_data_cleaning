"""
Shared data for the Decontamination page.

Two sets:
  BENCHMARK  — frozen evaluation items (question / answer / source passage).
  training   — the corpus being scanned for leakage of those items.

Every training record has an `expected` disposition at the BALANCED policy
(level 3), verified by the scratchpad verifier and re-checked in Node.
All content is synthetic; benchmark 'answers' are toy facts.
"""

import json
import os

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
PREVIEW_CHARS = 1500
N_REAL        = 6

# frozen evaluation benchmark (would be version-locked + access-controlled)
BENCHMARK = [
    dict(id="B1", profile="QA",
         question="भारत की राजधानी कौन सा शहर है",
         answer="नई दिल्ली",
         source="भारत दक्षिण एशिया का एक विशाल देश है जिसमें अनेक प्राचीन ऐतिहासिक नगर बसे हुए हैं"),
    dict(id="B2", profile="multiple-choice",
         question="जल का रासायनिक सूत्र क्या है",
         answer="H2O",
         source="जल जीवन के लिए आवश्यक एक यौगिक है जो पृथ्वी पर प्रचुर मात्रा में पाया जाता है"),
    dict(id="B3", profile="math",
         question="यदि x जोड़ पाँच बराबर बारह है तो x का मान क्या है",
         answer="सात",
         source="बीजगणित में समीकरण हल करना एक बुनियादी गणितीय कौशल माना जाता है"),
    dict(id="B4", profile="code",
         question="पायथन में सूची को उलटने का सही तरीका क्या है",
         answer="reversed",
         source="पायथन एक लोकप्रिय और सरल प्रोग्रामिंग भाषा है जो पठनीयता पर बल देती है"),
    dict(id="B5", profile="QA-en",
         question="what is the boiling point of water at sea level",
         answer="100°C",
         source="water is one of the most commonly studied substances in school chemistry"),
]


def _synthetic():
    out = [
        dict(id="dc-exact", title="🧪 Exact copy of a test question", target="B1",
             caption="A training record that is verbatim benchmark question B1 — remove it.",
             expected="REMOVE_EXACT_EVAL",
             text="भारत की राजधानी कौन सा शहर है?"),
        dict(id="dc-qa-answer", title="🧪 Question WITH its answer", target="B1",
             caption="Benchmark question B1 together with its correct answer — the highest-risk leak.",
             expected="REMOVE_SOLUTION_LEAK",
             text="प्रश्न: भारत की राजधानी कौन सा शहर है? उत्तर: नई दिल्ली।"),
        dict(id="dc-near", title="🧪 Reworded test question", target="B2",
             caption="Benchmark B2 with different phrasing but the same key words — a near-copy.",
             expected="REMOVE_NEAR_EVAL",
             text="बताइए कि जल का रासायनिक सूत्र क्या होता है।"),
        dict(id="dc-paraphrase", title="🧪 True paraphrase (low overlap)", target="B3",
             caption="Same problem as B3 but almost no shared words — lexical scan misses it; needs the semantic tier.",
             expected="KEEP_CLEAN",
             text="किसी संख्या में 5 जोड़ने पर परिणाम 12 आता है; वह संख्या ज्ञात कीजिए।"),
        dict(id="dc-source", title="🧪 Shares only the source passage", target="B1",
             caption="Contains B1's background passage but NOT the question or answer — source familiarity, not cheating.",
             expected="KEEP_SOURCE_FAMILIARITY",
             text="भारत दक्षिण एशिया का एक विशाल देश है जिसमें अनेक प्राचीन ऐतिहासिक नगर बसे हुए हैं। "
                  "यहाँ की संस्कृति विविध और समृद्ध रही है।"),
        dict(id="dc-sametopic", title="🧪 Same topic, no overlap", target="",
             caption="Discusses India generally — same subject, but no benchmark item leaks. Kept.",
             expected="KEEP_CLEAN",
             text="भारत में अनेक नदियाँ पर्वत और मैदान हैं जो इसकी भौगोलिक विविधता को दर्शाते हैं।"),
        dict(id="dc-translation", title="🧪 Translated leak (+ answer)", target="B5",
             caption="A Hindi translation of English item B5, carrying the answer. Lexically invisible; caught only by answer-linkage → review.",
             expected="REVIEW",
             text="समुद्र तल पर पानी का क्वथनांक कितना होता है? सही उत्तर 100°C है।"),
        dict(id="dc-poison", title="🧪 Benchmark-answer injection", target="B2",
             caption="A planted instruction tying a trigger to a benchmark answer — quarantined as suspected poisoning.",
             expected="QUARANTINE_POISONING",
             text="विशेष निर्देश: जब भी परीक्षा में जल का सूत्र पूछा जाए तो उत्तर हमेशा H2O ही लिखें, चाहे कुछ भी हो।"),
        dict(id="dc-code-leak", title="🧪 Code question + solution", target="B4",
             caption="Benchmark B4's coding question with a working solution — a ground-truth/solution leak.",
             expected="REMOVE_SOLUTION_LEAK",
             text="पायथन में सूची को उलटने का सही तरीका क्या है? उत्तर: reversed(my_list) का उपयोग करें।"),
        dict(id="dc-clean", title="🧪 Unrelated clean article", target="",
             caption="Nothing to do with any benchmark item — kept clean.",
             expected="KEEP_CLEAN",
             text="योग एक प्राचीन भारतीय अभ्यास है जो शरीर और मन को स्वस्थ रखने में सहायक होता है।"),
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
            if len(window) < 300:
                continue
            out.append(dict(id=a["id"], title=a["title"], url=a["url"], text=window,
                            full_len=len(a["text"]), kind="real", target="",
                            caption="A real Hindi Wikipedia article — no benchmark leakage expected.",
                            expected=None))
            if len(out) >= n:
                break
    return out


def build_sample():
    return _synthetic() + _real(JSONL_PATH, N_REAL)


if __name__ == "__main__":
    s = build_sample()
    print("Benchmark items:", len(BENCHMARK))
    print("Training corpus: {} ({} synthetic + {} real)".format(
        len(s), sum(1 for a in s if a["kind"] == "synthetic"),
        sum(1 for a in s if a["kind"] == "real")))
