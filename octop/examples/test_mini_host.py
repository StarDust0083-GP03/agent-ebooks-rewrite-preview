"""Checks for the book's teaching model only, not the Octop implementation."""
import json
import tempfile
import unittest
from pathlib import Path

from mini_host import MiniHost


class HostTests(unittest.TestCase):
    def setUp(self):
        self.host = MiniHost()
        self.host.add_agent("research", 7, shared=True)
        self.thread = self.host.open_thread(7, "research")

    def tearDown(self):
        self.host.close()

    def propose(self):
        return self.host.propose(7, "research", self.thread,
                                 recipient="review@example.invalid", text="待审核提纲")

    def test_shared_agent_does_not_share_thread(self):
        other = self.host.open_thread(9, "research")
        self.assertNotEqual(other, self.thread)
        with self.assertRaises(PermissionError):
            self.host.assert_thread(9, "research", self.thread)

    def test_new_session_binding_keeps_old_thread(self):
        fresh = self.host.open_thread(7, "research", fresh=True)
        self.assertNotEqual(fresh, self.thread)
        self.assertEqual(fresh, self.host.open_thread(7, "research"))
        self.host.assert_thread(7, "research", self.thread)

    def test_duplicate_approval_is_noop_and_payload_is_fixed(self):
        action = self.propose()
        self.assertTrue(self.host.approve(7, "research", self.thread, action))
        self.assertFalse(self.host.approve(7, "research", self.thread, action))
        rows = self.host.db.execute("SELECT * FROM outbox").fetchall()
        self.assertEqual(1, len(rows))
        self.assertEqual("review@example.invalid", json.loads(rows[0]["payload"])["recipient"])

    def test_cross_user_approval_rejected(self):
        action = self.propose()
        other = self.host.open_thread(9, "research")
        with self.assertRaises(PermissionError):
            self.host.approve(9, "research", other, action)
        self.assertEqual(0, self.host.db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0])

    def test_cancelled_action_cannot_be_approved(self):
        action = self.propose()
        self.assertTrue(self.host.cancel(7, "research", self.thread, action))
        self.assertFalse(self.host.approve(7, "research", self.thread, action))

    def test_pending_action_survives_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "teaching.sqlite"
            before = MiniHost(path)
            before.add_agent("research", 7)
            thread = before.open_thread(7, "research")
            action = before.propose(7, "research", thread,
                                    recipient="review@example.invalid", text="提纲")
            before.close()
            after = MiniHost(path)
            try:
                self.assertTrue(after.approve(7, "research", thread, action))
            finally:
                after.close()


if __name__ == "__main__":
    unittest.main()
