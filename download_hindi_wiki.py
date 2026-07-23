"""
Download a 40K article slice of Hindi Wikipedia (~20-25M tokens).
Source: wikimedia/wikipedia 20231101.hi (T0 native-verified tier)
Output: data/wiki_hi/wiki_hi.jsonl
"""

import json
import os
from datasets import load_dataset

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "wiki_hi")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "wiki_hi.jsonl")
N_ARTICLES = 40_000


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Streaming Hindi Wikipedia (target: {N_ARTICLES:,} articles)...")
    ds = load_dataset(
        "wikimedia/wikipedia",
        "20231101.hi",
        streaming=True,
        trust_remote_code=True,
    )

    count = 0
    total_chars = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for article in ds["train"].take(N_ARTICLES):
            record = {
                "id": article["id"],
                "title": article["title"],
                "text": article["text"],
                "url": article["url"],
                "lang": "hi",
                "source": "wikimedia/wikipedia",
                "tier": "T0_native_verified",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            total_chars += len(article["text"])

            if count % 5_000 == 0:
                print(f"  {count:,} articles downloaded...")

    avg_chars = total_chars / count if count else 0
    est_tokens = total_chars / 4.5  # ~4.5 chars per token for Indic scripts

    print(f"\nDone.")
    print(f"  Articles   : {count:,}")
    print(f"  Total chars: {total_chars:,}")
    print(f"  Est. tokens: {est_tokens:,.0f}")
    print(f"  Avg chars/article: {avg_chars:,.0f}")
    print(f"  Saved to   : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
