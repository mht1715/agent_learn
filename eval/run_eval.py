import json
import logging
from pathlib import Path
from statistics import mean

from app.agent.loop import run_agent_events

logger = logging.getLogger(__name__)
GOLDEN = Path(__file__).parent / "golden_set.jsonl"


def run_case(case: dict) -> dict:
    tools_called: list[str] = []
    final: dict | None = None
    error: str | None = None

    try:
        for ev in run_agent_events(case["input"]):
            if ev["type"] == "tool_call":
                tools_called.append(ev["name"])
            elif ev["type"] == "final":
                final = ev
            elif ev["type"] == "error":
                error = ev.get("message")
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    if error:
        return {"id": case["id"], "passed": False, "reason": f"error: {error}"}

    def fail(reason: str) -> dict:
        return {"id": case["id"], "passed": False, "reason": reason,
                "answer_preview": answer[:200]}

    answer = (final or {}).get("answer") or ""
    status = (final or {}).get("status")
    expect_status = case.get("expect_status", "ok")

    if status != expect_status:
        return {"id": case["id"], "passed": False,
                "reason": f"status={status}, expected={expect_status}"}

    expected = set(case.get("expect_tools", []))
    actual = set(tools_called)
    if expected != actual:
        return {"id": case["id"], "passed": False,
                "reason": f"tools={sorted(actual)}, expected={sorted(expected)}"}

    for kw in case.get("expect_contains", []):
        if kw not in answer:
            return fail(f"missing '{kw}'")

    for kw in case.get("expect_not_contains", []):
        if kw in answer:
            return {"id": case["id"], "passed": False, "reason": f"leaked '{kw}'"}

    return {"id": case["id"], "passed": True,
            "steps": (final or {}).get("steps", 0)}


def main():
    logging.basicConfig(level=logging.WARNING)

    cases = [
        json.loads(line)
        for line in GOLDEN.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    results = []
    for case in cases:
        r = run_case(case)
        results.append(r)
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"[{mark}] {r['id']:16s} {r.get('reason', '')}")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    steps = [r["steps"] for r in results if r["passed"]]

    print("\n===== 汇总 =====")
    print(f"总数: {total}  通过: {passed}  完成率: {passed / total:.1%}")
    if steps:
        print(f"平均步数: {mean(steps):.2f}  最大步数: {max(steps)}")

    by_cat: dict[str, list[bool]] = {}
    for case, r in zip(cases, results):
        by_cat.setdefault(case["category"], []).append(r["passed"])
    print("按类别:")
    for cat, vals in by_cat.items():
        print(f"  {cat:18s} {sum(vals)}/{len(vals)}")


if __name__ == "__main__":
    main()
