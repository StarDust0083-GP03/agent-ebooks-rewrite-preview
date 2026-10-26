import unittest
from pathlib import Path
from mini_rag import Chunk, Retriever, load_chunks, pack_context, retrieval_metrics, rrf, split_text, tokenize


def chunk(cid, doc="doc", version="v2", position=0, scope="public", active=True, text="支付回调验签"):
    return Chunk(cid, doc, version, position, text, "教学来源", scope, active)


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.r = Retriever(load_chunks(Path(__file__).with_name("documents.jsonl")))

    def test_bm25_finds_evidence(self):
        self.assertEqual(self.r.search("回调处理顺序", mode="bm25", k=1)[0][0].id, "callback-v2:0")

    def test_chinese_tokenization(self):
        self.assertIn("验签", tokenize("支付回调验签"))
        self.assertIn("callback_v2", tokenize("callback_v2"))

    def test_filter_happens_before_scoring(self):
        for mode in ("bm25", "cosine", "fusion"):
            hits = self.r.search("支付回调验签和幂等", user="alice", mode=mode, k=100)
            self.assertNotIn("bob-v1:0", [c.id for c, _ in hits])
            self.assertNotIn("callback-v1:0", [c.id for c, _ in hits])
            visible_only = Retriever(self.r.visible("alice"))
            self.assertEqual(hits, visible_only.search("支付回调验签和幂等", "alice", mode, 100))

    def test_windows_keep_version_document_and_acl(self):
        r = Retriever([chunk("x", position=0), chunk("next", position=1),
                       chunk("old", version="v1", position=1),
                       chunk("other", doc="other", position=1),
                       chunk("secret", position=2, scope="bob")])
        result = r.expand([(r.chunks[0], 1)], "alice", 2)
        self.assertEqual([c.id for c in result], ["x", "next"])

    def test_unauthorized_center_cannot_expand(self):
        private = next(c for c in self.r.chunks if c.scope == "bob")
        self.assertEqual(self.r.expand([(private, 1)], "alice"), [])

    def test_rrf_joins_by_id(self):
        ranking = rrf([["a", "b"], ["b", "a"]])
        self.assertAlmostEqual(ranking[0][1], ranking[1][1])
        self.assertEqual([cid for cid, _ in ranking], ["a", "b"])
        self.assertEqual(rrf([["a", "a", "b"]]), rrf([["a", "b"]]))

    def test_pack_counts_headers_and_separators(self):
        docs = self.r.visible("alice")
        context, ids = pack_context(docs, budget=160)
        self.assertLessEqual(len(context), 160)
        self.assertTrue(ids)
        self.assertEqual(pack_context(docs, 0), ("", []))
        self.assertEqual(pack_context([docs[0], docs[0]], 1000)[1], [docs[0].id])

    def test_no_match_is_empty(self):
        self.assertEqual(self.r.search("xyzunfindable"), [])
        self.assertEqual(self.r.search(""), [])

    def test_invalid_parameters(self):
        for size, overlap in ((0, 0), (2, 2), (2, -1)):
            with self.assertRaises(ValueError):
                split_text("abcdef", size, overlap)
        for kwargs in ({"k": 0}, {"mode": "unknown"}, {"user": ""}, {"user": "public"}):
            with self.assertRaises(ValueError):
                self.r.search("支付", **kwargs)
        with self.assertRaises(ValueError):
            self.r.expand([], radius=-1)
        with self.assertRaises(ValueError):
            pack_context([], -1)
        with self.assertRaises(ValueError):
            rrf([["a"]], constant=0)

    def test_duplicate_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            Retriever([chunk("same"), chunk("same", doc="another")])
        with self.assertRaises(ValueError):
            Retriever([chunk("a"), chunk("b")])

    def test_split_offsets(self):
        self.assertEqual(split_text("abcdefghij", 4, 1), ["abcd", "defg", "ghij", "j"])

    def test_metrics_need_all_evidence(self):
        result = retrieval_metrics(["a", "b"], ["a", "c"])
        self.assertEqual(result, {"recall": 0.5, "mrr": 1.0, "complete": False})
        self.assertEqual(retrieval_metrics(["a"], ["a", "a"])["recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
