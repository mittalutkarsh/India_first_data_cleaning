"""Generate feature3.html — a dedicated, teachable page for Feature 3 (the
frozen byte-level BPE tokenizer). Each epic gets: what & why, the real code, and
a worked example. Reuses the house CSS. This is the per-feature deep-dive page;
the Assignment page stays the tracker."""
import html
import generate_v5_playbook as P

CSS = P.CSS

NAV = (
    '<div class="nav"><div class="nav-in">\n'
    '  <span class="brand">India-First 40B</span>\n'
    '  <a href="overview.html">Overview</a>\n'
    '  <a href="v5_playbook.html">V5 Plan — Proposal</a>\n'
    '  <a href="assignment.html">Assignment</a>\n'
    '  <a href="feature3.html" class="active">Feature 3</a>\n'
    '</div></div>\n'
)


def code(src):
    return '    <div class="diagram"><pre>%s</pre></div>\n' % html.escape(src.strip("\n"))


def epic(eid, title, what_html, code_src, example_src, example_note=""):
    out = '  <div class="sec"><h2>Epic %s — %s</h2>\n' % (eid, html.escape(title))
    out += '    <p>%s</p>\n' % what_html
    out += '    <p class="cap">The code</p>\n' + code(code_src)
    out += '    <p class="cap">Worked example</p>\n' + code(example_src)
    if example_note:
        out += '    <p class="cap">%s</p>\n' % example_note
    out += '  </div>\n'
    return out


# ---- epic content --------------------------------------------------------

E31_CODE = '''
def _bytes_to_unicode():          # the classic GPT-2 construction
    bs = list(range(ord("!"), ord("~")+1)) + list(range(ord("¡"), ord("¬")+1)) \\
       + list(range(ord("®"), ord("ÿ")+1))
    cs = bs[:]; n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b); cs.append(256 + n); n += 1
    return {b: chr(c) for b, c in zip(bs, cs)}   # every byte -> one printable char

BYTE_TO_UNICODE = _bytes_to_unicode()
UNICODE_TO_BYTE = {c: b for b, c in BYTE_TO_UNICODE.items()}

# a single leading space attaches to the next word; a "word" is a run of
# non-whitespace, so an Indic syllable + its marks is never split.
PRETOKEN_RE = __import__("re").compile(r" ?\\S+|\\s+")

def encode_to_symbols(text): return "".join(BYTE_TO_UNICODE[b] for b in text.encode("utf-8"))
def decode_from_symbols(s):  return bytes(UNICODE_TO_BYTE[c] for c in s).decode("utf-8")
def pretokenize(text):       return PRETOKEN_RE.findall(text)
'''

E31_EX = '''
>>> byte_encode("the monsoon")
[116, 104, 101, 32, 109, 111, 110, 115, 111, 111, 110]

>>> encode_to_symbols("the monsoon")      # byte 32 (space) -> the symbol "Ġ"
'theĠmonsoon'

>>> pretokenize("the monsoon")            # leading space rides with the word
['the', ' monsoon']

>>> pretokenize("हिन्दी भाषा")             # the whole syllable stays together
['हिन्दी', ' भाषा']

>>> decode_from_symbols(encode_to_symbols("தமிழ் 😀 ₹100"))   # lossless, every lane
'தமிழ் 😀 ₹100'
'''

E32_CODE = '''
def train_bpe(texts, *, vocab_size, special_tokens=()):
    # base vocab: specials first (reserved ids), then all 256 byte symbols
    vocab = {}
    for tok in list(special_tokens) + [BYTE_TO_UNICODE[b] for b in range(256)]:
        vocab.setdefault(tok, len(vocab))
    target_merges = vocab_size - len(vocab)

    # ... count adjacent symbol-pair frequencies inside pre-tokens ...
    merges = []
    while len(merges) < target_merges:
        # pick the best pair: MAX count, and on a tie the SMALLEST pair.
        # a lazy max-heap makes this near-linear instead of rescanning.
        best = pop_best(heap, pair_count)          # (-count, pair) -> smallest tuple wins
        if best is None: break
        a, b = best
        merge_everywhere(a, b)                      # incremental pair-count updates
        vocab[a + b] = len(vocab)
        merges.append((a, b))
    return vocab, merges
'''

E32_EX = '''
# trained on the real cleaned 10M corpus (lane-balanced sample), vocab=12,000.
# the FIRST merges the trainer chose are Indic byte-pairs — the corpus is
# India-heavy, so BPE spends its early budget where the bytes are:

>>> merges[:8]
[('à','®'), ('à','¤'), ('à','¦'), ('à','¯'), ('à','¥'),
 ('Ġ','à¤'), ('à¯','į'), ('Ġ','t')]

# determinism: retrain on the same sample -> byte-identical (vocab, merges).
'''

E33_CODE = '''
def save(self, out_dir):                 # deterministic bytes; newline="\\n"
    write vocab.json          # {token: id}     (sort_keys, ensure_ascii=False)
    write merges.txt          # "# v5-bpe merges v1" header, then "a b" per line
    write special_tokens.json # ["<pad>","<bos>","<eos>","<doc>"]

@classmethod
def load(cls, in_dir):
    merges = []
    for line in read(merges.txt):
        # skip ONLY the exact header, never a merge whose first symbol is "#"
        # (byte '#' maps to the symbol '#', so "# x" is real data, not a comment)
        if not line or line == MERGES_HEADER:
            continue
        a, b = line.split(" ")
        merges.append((a, b))
    return cls(vocab, merges, specials)
'''

E33_EX = '''
merges.txt (first lines):
    # v5-bpe merges v1
    à ®
    à ¤
    à ¦
    ...

A bug this caught: the loader first skipped every line starting with "#",
which silently dropped 4 real merges whose first token was "#". The frozen
hash then failed to verify — exactly the guard doing its job (see Epic 3.7).
Fix: match the header line EXACTLY. Regression test now forces a "#"-merge.
'''

E34_CODE = '''
def _bpe_word(self, symbols):            # greedily apply the lowest-rank merge
    word = list(symbols)
    while True:
        best = argmin_rank((word[i], word[i+1]) for i in range(len(word)-1))
        if best is None: return word
        merge best pair in `word`

def encode(self, text):                  # text -> token ids, never <unk>
    ids = []
    for sym in pretokens_as_symbols(text):
        for tok in self._bpe_word(sym):
            ids.append(self.vocab[tok])
    return ids
'''

E34_EX = '''
>>> ids = tok.encode("the monsoon")
>>> ids
[1454, 1741, 1093, 275]
>>> [tok.id_to_token[i] for i in ids]
['the', 'Ġmon', 'so', 'on']            #  "the" learned as ONE token

>>> tok.encode("हिन्दी भाषा")
[10638, 2547]
>>> [tok.id_to_token[i] for i in _]
['à¤¹à¤¿à¤¨à¥įà¤¦à¥Ģ', 'Ġà¤Ńà¤¾à¤·à¤¾']   # the whole Hindi word = ONE token
'''

E35_CODE = '''
def decode(self, ids):
    # special tokens carry no bytes -> skip them; concatenate symbols FIRST,
    # then convert the whole stream to bytes once (a token may end mid-UTF-8).
    symbols = "".join(self.id_to_token[i] for i in ids
                      if self.id_to_token[i] not in self.special_set)
    return decode_from_symbols(symbols)
'''

E35_EX = '''
The invariant for the whole feature — decode(encode(x)) == x, on every lane:

    "The monsoon reaches Kerala."      ->  True
    "हिन्दी भाषा 😀 ₹100"               ->  True
    "বাংলা ভাষা — naïve café"          ->  True
    "def add(a, b):\\n    return a + b" ->  True
    "தமிழ் ஒரு செம்மொழி ஆகும்."          ->  True   (Tamil never seen in training)
'''

E36_CODE = '''
def check_integrity(self):               # raises ValueError on any inconsistency
    assert ids == 0..N-1                  # contiguous, no duplicates
    assert every one of the 256 bytes is in the vocab       # no <unk> possible
    assert every merge (a, b) has a, b and a+b in the vocab
    assert special tokens are in the vocab
    assert no special token collides with a byte / merge token
'''

E36_EX = '''
>>> [tok.vocab[s] for s in ("<pad>","<bos>","<eos>","<doc>")]
[0, 1, 2, 3]                             # reserved, low ids

>>> tok.decode([tok.vocab["<bos>"]] + tok.encode("hello") + [tok.vocab["<eos>"]])
'hello'                                  # specials frame the text, decode drops them

# a corrupted vocab (a byte removed) is rejected:
>>> Tokenizer(broken, merges, specials).check_integrity()
ValueError: byte 65 ('A') missing from the vocab
'''

E37_CODE = '''
def content_hash(self):                  # the tokenizer's frozen identity
    obj = {"special_tokens": ..., "vocab": self.vocab,
           "merges": [list(m) for m in self.merges]}
    return sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False))

def verify_frozen(out_dir):              # downstream stages call this
    manifest = read(tokenizer_manifest.json)
    return load(out_dir).content_hash() == manifest["hash"]
'''

E37_EX = '''
tokenizer_manifest.json:
    {
      "kind": "tokenizer_manifest",
      "hash": "3eb8d6c50b13dc2733e6379d8dbd082bdd0bbb9200031b8984e18ca1b5684756",
      "vocab_size": 12000,
      "n_merges": 11740,
      "special_tokens": ["<pad>","<bos>","<eos>","<doc>"],
      "base": "bytes-256",
      "trained_on": "data/clean"
    }

Re-freeze the same corpus -> the SAME hash. Change one token -> a new hash.
Every downstream stage (shards, batches) references this hash as the tokenizer's
identity.
'''

E38_CODE = '''
def stage_tokenizer(log, *, clean_root, tokenizer_dir, vocab_size):
    tok = build_frozen_tokenizer(clean_root=clean_root, out_dir=tokenizer_dir,
                                 vocab_size=vocab_size)
    if not verify_frozen(tokenizer_dir):
        raise ValueError("frozen tokenizer hash does not match its manifest")
    for text in sample_clean_corpus(clean_root, docs_per_lane=1):   # real evidence
        assert tok.decode(tok.encode(text)) == text
    log.passed("tokenizer_frozen", vocab=len(tok.vocab),
               merges=len(tok.merges), hash=tok.content_hash())
'''

E38_EX = '''
python run_demo.py  (on the real 10M corpus):

    [PASS] corpus_loaded total=13087 eval=29 contrastive=36
    [PASS] corpus_cleaned kept=13026 dropped=32
    [INFO] tokenizer vocab=12000 merges=11740
    [INFO] tokenizer_roundtrip lanes_checked=5
    [PASS] tokenizer_frozen vocab=12000 merges=11740 hash=3eb8d6c50b13...
    [INFO] run_complete
'''

EPICS = [
    ("3.1", "Byte-level alphabet + pre-tokenization",
     "Represent any text as its raw UTF-8 bytes (0&ndash;255). Because the base alphabet is all "
     "256 byte values, <em>every</em> script &mdash; Devanagari, Bengali, Tamil, emoji, code &mdash; "
     "is representable with <strong>zero <code>&lt;unk&gt;</code></strong> and nothing to fragment. "
     "A GPT-2-style map turns each byte into one printable symbol so merges can be stored as text, "
     "and a single fixed regex splits words on whitespace without ever cutting inside a syllable.",
     E31_CODE, E31_EX),
    ("3.2", "Deterministic BPE trainer",
     "Count adjacent symbol-pair frequencies inside pre-tokens, merge the most frequent pair, repeat "
     "to the target vocab (locked at 12,000). The tie-break is total and fixed &mdash; highest count, "
     "then the lexicographically smallest pair &mdash; so the learned merges are reproducible "
     "regardless of dict order. A lazy max-heap keeps it near-linear.",
     E32_CODE, E32_EX),
    ("3.3", "Freeze: serialize vocab + merges",
     "Write <code>vocab.json</code>, <code>merges.txt</code> and <code>special_tokens.json</code> with "
     "deterministic bytes, then treat them as immutable. Serialize &rarr; load &rarr; serialize must be "
     "byte-identical across machines.",
     E33_CODE, E33_EX),
    ("3.4", "Encoder",
     "Turn text into token ids: within each pre-token, greedily apply the lowest-rank merge until none "
     "remain, then map tokens to ids. A byte-level fallback guarantees <code>&lt;unk&gt;</code> can "
     "never occur.",
     E34_CODE, E34_EX),
    ("3.5", "Decoder + lossless round-trip",
     "Invert encoding through the byte-level map. The whole feature turns on one property: "
     "<strong>decode(encode(x)) == x on every lane</strong>, including Indic combining sequences, "
     "emoji and code punctuation.",
     E35_CODE, E35_EX),
    ("3.6", "Special tokens + integrity checks",
     "Reserve <code>&lt;pad&gt; &lt;bos&gt; &lt;eos&gt; &lt;doc&gt;</code> with fixed low ids that "
     "never arise from ordinary text, and assert the tokenizer is internally consistent &mdash; all "
     "256 bytes covered, ids contiguous, every merge grounded, no collisions.",
     E36_CODE, E36_EX),
    ("3.7", "Tokenizer manifest + content hash",
     "Hash the canonical (vocab + merges + specials) into the tokenizer&rsquo;s identity and record it "
     "in a manifest. Re-freezing the same corpus reproduces the hash; a one-token change breaks it. "
     "This is the contract every downstream stage references.",
     E37_CODE, E37_EX),
    ("3.8", "Wire the tokenizer stage into run_demo",
     "Build &rarr; verify the hash against the manifest &rarr; encode/decode a real document from every "
     "lane &rarr; emit <code>[PASS] tokenizer_frozen</code>. The evidence is real cleaned text, never a "
     "canned string, and <code>run.log</code> stays byte-identical across machines.",
     E38_CODE, E38_EX),
]


def build_html():
    body = "".join(epic(*e) for e in EPICS)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Feature 3 — Frozen byte-level BPE tokenizer</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + NAV +
        '<div class="wrap">\n'
        '  <div class="crumb">Session 6 / Feature 3 — Frozen byte-level BPE tokenizer</div>\n'
        '  <div class="phead">\n'
        '    <div class="eyebrow">Feature 3 · epics with code &amp; worked examples</div>\n'
        '    <h1>Frozen byte-level BPE tokenizer</h1>\n'
        '    <p class="dek">Train one small byte-level BPE tokenizer on the cleaned corpus, then '
        '<em>freeze</em> it: serialize its vocab and merges, content-hash the artifact, and let every '
        'downstream stage reference that hash. Byte-level is a deliberate India-first choice &mdash; the '
        '256-byte base alphabet represents Devanagari, Bengali and Tamil losslessly, so there is no '
        '<code>&lt;unk&gt;</code> and nothing to fragment.</p>\n'
        '  </div>\n'

        '  <div class="sec"><h2>The pipeline &amp; the invariant</h2>\n'
        '    <div class="diagram"><pre>\n'
        'text\n'
        '  -> bytes (UTF-8, 0..255)             every script representable, no &lt;unk&gt;\n'
        '  -> printable symbols (GPT-2 map)     so vocab/merges store as text\n'
        '  -> pre-tokens ( ?\\S+ | \\s+ )         words never split inside; merges never cross a space\n'
        '  -> BPE merges (learned, ranked)      trained on the cleaned corpus, vocab = 12,000\n'
        '  -> ids            [encode]\n'
        '  -> text           [decode]           INVARIANT: decode(encode(x)) == x, on every lane\n'
        '  -> frozen + content-hashed           the tokenizer\'s identity for all downstream stages\n'
        '</pre></div>\n'
        '    <p class="cap">Built directly (Feature 2&rsquo;s cleaning skills carried over); '
        '53 offline tests for this feature, 230 across the repo. The real run trains in ~2 minutes.</p>\n'
        '  </div>\n'
        + body +
        '  <div class="foot">Session 6 · Feature 3 deep-dive. Tracker: '
        '<code>assignment.html</code>. Code lives in the <code>v5-execution-system</code> repo '
        '(<code>byte_level.py</code>, <code>bpe_train.py</code>, <code>bpe_tokenizer.py</code>, '
        '<code>tokenizer_build.py</code>).</div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("feature3.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. feature3.html written.")
