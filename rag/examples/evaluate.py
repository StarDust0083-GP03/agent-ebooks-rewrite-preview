"""Fixed teaching questions. This is not a production benchmark."""
import json
from pathlib import Path
from mini_rag import Retriever, load_chunks, pack_context, retrieval_metrics

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("回调处理顺序", ["callback-v2:0"]),
    ("支付回调验签和幂等如何处理", ["callback-v2:0", "callback-v2:1"]),
    ("重复通知如何处理", ["callback-v2:1"]),
    ("退款失败后如何处理", ["refund-v2:0"]),
    ("退款申请单的幂等键", ["refund-v2:1"]),
    ("回调模块技术负责人是谁", ["owner-v1:0", "team-v1:0"]),
]


def run():
    retriever = Retriever(load_chunks(ROOT / "examples/documents.jsonl"))
    report = []
    for mode, k, radius in [("bm25", 2, 0), ("cosine", 2, 0),
                            ("fusion", 2, 0), ("fusion", 1, 1)]:
        rows = []
        for query, expected in CASES:
            hits = retriever.search(query, user="alice", mode=mode, k=k)
            chunks = retriever.expand(hits, user="alice", radius=radius)
            context, injected = pack_context(chunks, 1200)
            candidates = [c.id for c, _ in hits]
            rows.append({"query": query, "gold": expected, "retrieved": candidates,
                         "injected": injected, "context_characters": len(context),
                         "retrieval": retrieval_metrics(expected, candidates),
                         "delivery": retrieval_metrics(expected, injected)})
        summary = {
            "candidate_recall": sum(r["retrieval"]["recall"] for r in rows) / len(rows),
            "delivery_recall": sum(r["delivery"]["recall"] for r in rows) / len(rows),
            "complete_rate": sum(r["delivery"]["complete"] for r in rows) / len(rows),
            "mrr": sum(r["retrieval"]["mrr"] for r in rows) / len(rows),
        }
        result = {"mode": mode, "k": k, "radius": radius, "summary": summary, "cases": rows}
        report.append(result)
        print(f"{mode:7} k={k} radius={radius} " + json.dumps(summary, ensure_ascii=False))
    path = ROOT / "sources/offline-evaluation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"scope": "6 fixed teaching questions; no LLM", "runs": report},
                               ensure_ascii=False, indent=2) + "\n")
    print("Saved sources/offline-evaluation.json")


if __name__ == "__main__":
    run()
