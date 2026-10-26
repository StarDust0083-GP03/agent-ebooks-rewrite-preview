"""Offline retrieval lab: BM25, lexical cosine, RRF, scoped windows.

Original teaching implementation, not a copy of upstream notebooks.
No semantic embeddings, model API, or natural-language answer generation.
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    version: str
    position: int
    text: str
    source: str
    scope: str = "public"
    active: bool = True

    def __post_init__(self):
        if not all(isinstance(v, str) and v.strip() for v in
                   (self.id, self.doc_id, self.version, self.text, self.source, self.scope)):
            raise ValueError("chunk strings must be non-empty")
        if type(self.position) is not int or self.position < 0:
            raise ValueError("position must be a nonnegative integer")
        if type(self.active) is not bool:
            raise ValueError("active must be a boolean")


def tokenize(text):
    """English terms and overlapping Chinese bigrams; not a semantic encoder."""
    tokens = []
    for part in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]+", text.lower()):
        if re.fullmatch(r"[\u4e00-\u9fff]+", part):
            tokens.extend(part[i:i + 2] for i in range(len(part) - 1))
            if len(part) == 1:
                tokens.append(part)
        else:
            tokens.append(part)
    return tokens


def split_text(text, size=400, overlap=80):
    if type(size) is not int or type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError("require integer 0 <= overlap < size")
    return [text[i:i + size] for i in range(0, len(text), size - overlap)]


def load_chunks(path):
    return [Chunk(**json.loads(line)) for line in Path(path).read_text().splitlines()
            if line.strip()]


def rrf(rankings, constant=60):
    if constant <= 0:
        raise ValueError("RRF constant must be positive")
    scores = defaultdict(float)
    for ranking in rankings:
        seen = set()
        for rank, cid in enumerate(dict.fromkeys(ranking), start=1):
            if cid not in seen:
                scores[cid] += 1 / (constant + rank)
                seen.add(cid)
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))


class Retriever:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        if len({c.id for c in self.chunks}) != len(self.chunks):
            raise ValueError("duplicate chunk ID")
        locations = [(c.doc_id, c.version, c.position) for c in self.chunks]
        if len(set(locations)) != len(locations):
            raise ValueError("duplicate document/version/position")

    def visible(self, user):
        if not isinstance(user, str) or not user.strip() or user == "public":
            raise ValueError("user must be a non-empty demo identity, not 'public'")
        # Demo identity comes from CLI, not authentication. Do not expose as an API.
        return [c for c in self.chunks if c.active and c.scope in ("public", user)]

    def search(self, query, user="alice", mode="fusion", k=3):
        if type(k) is not int or not 1 <= k <= 100:
            raise ValueError("k must be 1..100")
        if mode not in ("bm25", "cosine", "fusion"):
            raise ValueError("unknown mode")
        if not isinstance(query, str) or len(query) > 2000:
            raise ValueError("query must be a string of at most 2000 characters")
        docs = self.visible(user)  # Filter before statistics, scoring, and model input.
        q = Counter(tokenize(query))
        if not q or not docs:
            return []
        counts = {c.id: Counter(tokenize(c.text)) for c in docs}
        lengths = {cid: sum(tf.values()) for cid, tf in counts.items()}
        average = sum(lengths.values()) / len(docs) or 1
        df = Counter(t for tf in counts.values() for t in tf)
        bm25, cosine = [], []
        qnorm = math.sqrt(sum(v * v for v in q.values()))
        for c in docs:
            tf = counts[c.id]
            score = 0.0
            for term in q:
                n = tf[term]
                if n:
                    idf = math.log(1 + (len(docs) - df[term] + 0.5) / (df[term] + 0.5))
                    score += idf * n * 2.5 / (n + 1.5 * (0.25 + 0.75 * lengths[c.id] / average))
            if score > 0:
                bm25.append((c.id, score))
            norm = math.sqrt(sum(v * v for v in tf.values()))
            similarity = sum(q[t] * tf[t] for t in q) / (qnorm * norm) if norm else 0
            if similarity > 0:
                cosine.append((c.id, similarity))
        bm25.sort(key=lambda x: (-x[1], x[0]))
        cosine.sort(key=lambda x: (-x[1], x[0]))
        ranked = {"bm25": bm25, "cosine": cosine}.get(mode)
        if ranked is None:
            ranked = rrf([[cid for cid, _ in bm25], [cid for cid, _ in cosine]])
        by_id = {c.id: c for c in docs}
        return [(by_id[cid], score) for cid, score in ranked[:k]]

    def expand(self, hits, user="alice", radius=1):
        if type(radius) is not int or not 0 <= radius <= 5:
            raise ValueError("radius must be 0..5")
        visible = self.visible(user)
        by_id = {c.id: c for c in visible}
        result = []
        seen = set()
        for candidate, _ in hits:
            center = by_id.get(candidate.id)
            if center is None:
                continue
            neighbors = sorted((c for c in visible if c.doc_id == center.doc_id
                                and c.version == center.version
                                and abs(c.position - center.position) <= radius),
                               key=lambda c: c.position)
            for chunk in neighbors:
                if chunk.id not in seen:
                    seen.add(chunk.id)
                    result.append(chunk)
        return result


def pack_context(chunks, budget=1200):
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative character count")
    blocks, selected, seen = [], [], set()
    used = 0
    for chunk in chunks:
        if chunk.id in seen:
            continue
        seen.add(chunk.id)
        block = f"[{chunk.id}] {chunk.source}\n{chunk.text}"
        cost = len(block) + (2 if blocks else 0)
        if used + cost <= budget:
            blocks.append(block)
            selected.append(chunk.id)
            used += cost
    return "\n\n".join(blocks), selected


def retrieval_metrics(expected, actual):
    gold, ranked = set(expected), list(dict.fromkeys(actual))
    if not gold:
        raise ValueError("gold evidence must not be empty")
    recall = len(gold.intersection(ranked)) / len(gold)
    reciprocal = next((1 / i for i, cid in enumerate(ranked, 1) if cid in gold), 0.0)
    return {"recall": recall, "mrr": reciprocal, "complete": gold.issubset(ranked)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="支付回调验签和幂等如何处理")
    parser.add_argument("--user", default="alice")
    parser.add_argument("--mode", choices=["bm25", "cosine", "fusion"], default="fusion")
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--window", type=int, default=0)
    parser.add_argument("--budget", type=int, default=1200)
    parser.add_argument("--data", type=Path, default=Path(__file__).with_name("documents.jsonl"))
    args = parser.parse_args()
    retriever = Retriever(load_chunks(args.data))
    hits = retriever.search(args.query, args.user, args.mode, args.k)
    expanded = retriever.expand(hits, args.user, args.window)
    context, ids = pack_context(expanded, args.budget)
    print(json.dumps({"mode": args.mode, "retrieved": [c.id for c, _ in hits],
                      "injected": ids, "context_characters": len(context)}, ensure_ascii=False, indent=2))
    print(context or "没有可交付证据。此示例不生成答案。")


if __name__ == "__main__":
    main()
