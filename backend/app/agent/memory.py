import sqlite3
import json
from langchain_core.messages import messages_from_dict, message_to_dict, SystemMessage, AIMessage
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "chat_history.db"
DB_PATH.parent.mkdir(exist_ok=True)


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS messages
                     (
                         id         INTEGER PRIMARY KEY AUTOINCREMENT,
                         session_id TEXT NOT NULL,
                         message    TEXT NOT NULL
                     )
                     """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON messages(session_id)")


def load_history(session_id: str) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT message FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        ).fetchall()

    if not rows:
        return [SystemMessage(content=(
            "你是工单助手。规则：\n"
            "1. 实时数据（订单、物流）用工具查。\n"
            "2. 规则政策必须调 search_knowledge_base。\n"
            "3. 查不到就如实说，不要编造。"
        ))]

    # 核心修复 1：外面加一层列表，让它变成 List[Dict]
    messages = []
    for row in rows:
        dict_msg = json.loads(row[0])
        msg_obj = messages_from_dict([dict_msg])[0]
        messages.append(msg_obj)

    return messages


def save_message(session_id: str, message) -> None:
    if isinstance(message, SystemMessage):
        return
    # 核心修复 2：带有 tool_calls 的 AIMessage 是中间状态，不能落盘！
    # 否则下次加载时，没有对应的 ToolMessage，模型会直接报错。
    if isinstance(message, AIMessage) and getattr(message, "tool_calls", None):
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, message) VALUES (?, ?)",
            (session_id, json.dumps(message_to_dict(message), ensure_ascii=False))
        )


init_db()
