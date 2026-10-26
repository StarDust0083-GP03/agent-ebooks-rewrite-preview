"""Offline teaching model, NOT Octop API or an external-action executor.

Trusted integer user IDs stand in for authentication. An outbox row means
"ready to deliver", not "email sent". SQLite is the only dependency.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4


class MiniHost:
    def __init__(self, path: str | Path = ":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY, owner INTEGER NOT NULL, shared INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY, agent TEXT NOT NULL REFERENCES agents(id),
                user INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                key TEXT PRIMARY KEY, thread TEXT NOT NULL REFERENCES threads(id)
            );
            CREATE TABLE IF NOT EXISTS actions (
                id TEXT PRIMARY KEY, thread TEXT NOT NULL REFERENCES threads(id),
                payload TEXT NOT NULL, state TEXT NOT NULL
                    CHECK(state IN ('pending','approved','cancelled'))
            );
            CREATE TABLE IF NOT EXISTS outbox (
                action TEXT PRIMARY KEY REFERENCES actions(id), payload TEXT NOT NULL
            );
        """)

    def close(self) -> None:
        self.db.close()

    def add_agent(self, agent: str, owner: int, *, shared: bool = False) -> None:
        with self.db:
            self.db.execute("INSERT INTO agents VALUES (?,?,?)", (agent, owner, int(shared)))

    def _agent_access(self, user: int, agent: str) -> None:
        row = self.db.execute("SELECT * FROM agents WHERE id=?", (agent,)).fetchone()
        if row is None or not (row["owner"] == user or row["shared"]):
            raise PermissionError("agent inaccessible")

    def assert_thread(self, user: int, agent: str, thread: str) -> None:
        self._agent_access(user, agent)
        row = self.db.execute("SELECT * FROM threads WHERE id=?", (thread,)).fetchone()
        if row is None or row["agent"] != agent or row["user"] != user:
            raise PermissionError("thread inaccessible")

    def open_thread(self, user: int, agent: str, *, fresh: bool = False) -> str:
        self._agent_access(user, agent)
        key = f"{agent}:dashboard:{user}:dm"
        old = self.db.execute("SELECT thread FROM sessions WHERE key=?", (key,)).fetchone()
        if old is not None and not fresh:
            self.assert_thread(user, agent, old["thread"])
            return str(old["thread"])
        thread = uuid4().hex
        with self.db:
            self.db.execute("INSERT INTO threads VALUES (?,?,?)", (thread, agent, user))
            self.db.execute(
                "INSERT INTO sessions VALUES (?,?) ON CONFLICT(key) DO UPDATE SET thread=excluded.thread",
                (key, thread),
            )
        return thread

    def propose(self, user: int, agent: str, thread: str, *, recipient: str, text: str) -> str:
        self.assert_thread(user, agent, thread)
        if not recipient.strip() or not text.strip():
            raise ValueError("recipient and text required")
        action = uuid4().hex
        payload = json.dumps({"recipient": recipient, "text": text}, ensure_ascii=False)
        with self.db:
            self.db.execute("INSERT INTO actions VALUES (?,?,?,'pending')", (action, thread, payload))
        return action

    def _action(self, user: int, agent: str, thread: str, action: str) -> sqlite3.Row:
        self.assert_thread(user, agent, thread)
        row = self.db.execute("SELECT * FROM actions WHERE id=? AND thread=?", (action, thread)).fetchone()
        if row is None:
            raise PermissionError("action inaccessible")
        return row

    def approve(self, user: int, agent: str, thread: str, action: str) -> bool:
        self._action(user, agent, thread, action)
        # Teaching simplification: one SQLite transaction, no remote side effect.
        with self.db:
            changed = self.db.execute(
                "UPDATE actions SET state='approved' WHERE id=? AND state='pending'", (action,)
            ).rowcount
            if changed:
                self.db.execute(
                    "INSERT INTO outbox SELECT id,payload FROM actions WHERE id=?", (action,)
                )
        return bool(changed)

    def cancel(self, user: int, agent: str, thread: str, action: str) -> bool:
        self._action(user, agent, thread, action)
        with self.db:
            changed = self.db.execute(
                "UPDATE actions SET state='cancelled' WHERE id=? AND state='pending'", (action,)
            ).rowcount
        return bool(changed)


def demo() -> None:
    host = MiniHost()
    try:
        host.add_agent("research", 7, shared=True)
        lin = host.open_thread(7, "research")
        zhou = host.open_thread(9, "research")
        assert lin != zhou
        action = host.propose(7, "research", lin, recipient="review@example.invalid", text="教学提纲")
        assert host.approve(7, "research", lin, action)
        assert not host.approve(7, "research", lin, action)
        count = host.db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0]
        assert count == 1
        print("两位用户、两条私人线程；重复批准只生成一条待投递记录。没有发送邮件。")
    finally:
        host.close()


if __name__ == "__main__":
    demo()
