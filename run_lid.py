"""
Model-based Language ID tier (offline) for the Language page.

Runs fastText lid.176 over the SAME sample the browser page uses
(lang_sample.build_sample) and writes lid_results.json, keyed by article id.
generate_language_preview.py bakes those verdicts into language.html so the
page can show model scores next to the dependency-free script tier.

This is the "model" that the script tier cannot be: it disambiguates Hindi
from Marathi/Sanskrit (shared Devanagari) and, in principle, romanized Hindi
from English — subject to the model's known limits (lid.176 is weak on
romanized Indic; note that in the output rather than trusting it blindly,
per Language_Skill.md Steps 05/07/12).

Setup (laptop):
    pip install fasttext-wheel        # prebuilt wheel, no compiler needed
    python3 run_lid.py                # auto-downloads lid.176.ftz (~917 KB)

Alternatives for better Indic / romanized coverage (heavier):
    - GlotLID  (cis-lmu/glotlid)      : 2000+ languages
    - IndicLID (ai4bharat/IndicLID)   : native + romanized Indic
"""

import json
import os
import sys
import urllib.request

import lang_sample

MODEL_URL  = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
MODEL_PATH = "lid.176.ftz"
OUTPUT     = "lid_results.json"
TOPK       = 5


def ensure_model():
    if os.path.exists(MODEL_PATH):
        return True
    print("Downloading fastText lid.176.ftz (~917 KB)...")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("  saved to {}".format(MODEL_PATH))
        return True
    except Exception as e:  # noqa: BLE001
        print("  ERROR downloading model: {}".format(e))
        print("  Manually download {} and place it at {}".format(MODEL_URL, MODEL_PATH))
        return False


def clean_for_lid(text):
    # fastText predict() rejects newlines; collapse whitespace to one line.
    return " ".join(text.split())


def predict_raw(model, text, k):
    """Call the underlying C predictor directly.

    fasttext-wheel 0.9.2's Python predict() wrapper does
    `np.array(probs, copy=False)`, which raises under NumPy 2.x. The raw
    pybind `model.f.predict` returns [(prob, label), ...] with no numpy, so
    we use it and skip the broken path.
    """
    preds = model.f.predict(text, k, 0.0, "strict")
    out = []
    for prob, label in preds:
        out.append((label.replace("__label__", ""), float(prob)))
    return out


def main():
    try:
        import fasttext
    except ImportError:
        print("fastText is not installed.\n")
        print("Install it (prebuilt wheel, no C++ compiler needed):")
        print("    pip install fasttext-wheel\n")
        print("Then re-run:  python3 run_lid.py")
        sys.exit(1)

    if not ensure_model():
        sys.exit(1)

    # fastText prints a harmless load warning to stderr; leave it be.
    model = fasttext.load_model(MODEL_PATH)

    articles = lang_sample.build_sample()
    results = {}

    for a in articles:
        text = clean_for_lid(a["text"])
        if not text:
            results[a["id"]] = {"model": "fasttext/lid.176", "candidates": [], "top1": None, "margin": None}
            continue
        preds = predict_raw(model, text, TOPK)
        cands = [{"lang": lang, "score": round(pr, 4)} for lang, pr in preds]
        margin = round(preds[0][1] - preds[1][1], 4) if len(preds) > 1 else None
        results[a["id"]] = {
            "model": "fasttext/lid.176",
            "candidates": cands,
            "top1": cands[0]["lang"] if cands else None,
            "margin": margin,
        }
        tag = "syn" if a["kind"] == "synthetic" else "real"
        print("  [{}] {:20s} -> {} ({:.1%})".format(
            tag, a["id"][:20], results[a["id"]]["top1"], cands[0]["score"] if cands else 0.0))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nWrote {} verdicts to {}".format(len(results), OUTPUT))
    print("Now regenerate the page:  python3 generate_language_preview.py")


if __name__ == "__main__":
    main()
