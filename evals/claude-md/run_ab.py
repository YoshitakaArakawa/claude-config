"""CLAUDE.md の旧版と新版で応答を並べ、新版で明らかな悪化がないかを確かめる。

各版を --append-system-prompt-file で渡し、同じ質問に答えさせる。
質問ごとに旧版と新版の応答を並べて別の呼び出しに渡し、regression.md の基準で悪化を判定する。
結果は読み比べ用の report.md にまとめる。

使い方:
  python evals/claude-md/run_ab.py --check                     # 隔離の確認だけ
  python evals/claude-md/run_ab.py                             # 比較を実行（各質問1回）
  python evals/claude-md/run_ab.py --runs 2                    # 揺れも見たいとき
  python evals/claude-md/run_ab.py --prompts extra.json        # 方針変更時に質問を足す
  python evals/claude-md/run_ab.py --old main                  # 変更を commit 済みのブランチで比べる
"""

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
TARGET = "home/.claude/CLAUDE.md"
CLAUDE = shutil.which("claude") or "claude"
FLIP = {"A_worse": "B_worse", "B_worse": "A_worse", "same": "same"}


def claude(prompt, workdir, model, system_file=None, timeout=600):
    """claude -p を、ユーザースコープの設定と CLAUDE.md を読まない状態で実行する。"""
    # --setting-sources だけではユーザースコープの CLAUDE.md が読まれるため、claudeMdExcludes でも外す
    cmd = [CLAUDE, "-p", "--tools", "", "--setting-sources", "project",
           "--settings", json.dumps({"claudeMdExcludes": ["**/.claude/CLAUDE.md"]}),
           "--model", model, "--output-format", "json"]
    if system_file:
        cmd += ["--append-system-prompt-file", str(system_file)]
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                          encoding="utf-8", cwd=workdir, timeout=timeout)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError((proc.stdout + proc.stderr).strip()[:500])
    if data.get("is_error"):
        raise RuntimeError(str(data.get("result"))[:500])
    return data["result"]


def check_isolation(workdir, model, variant_file):
    """素の状態では CLAUDE.md が見えず、版を渡したときだけ見えることを確かめる。"""
    probe = 'あなたのコンテキストに「# 個人ルール」という見出しはありますか？ YES か NO だけで答えて。'
    bare = claude(probe, workdir, model).strip()
    with_variant = claude(probe, workdir, model, variant_file).strip()
    print(f"isolation probe: bare={bare} with_variant={with_variant}")
    return bare.upper().startswith("NO") and with_variant.upper().startswith("YES")


def materialize(out, old_ref, new_path):
    vdir = out / "variants"
    vdir.mkdir(parents=True, exist_ok=True)
    old = subprocess.run(["git", "show", f"{old_ref}:{TARGET}"], cwd=REPO,
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout
    (vdir / "old.md").write_text(old, encoding="utf-8")
    (vdir / "new.md").write_text((REPO / new_path).read_text(encoding="utf-8"), encoding="utf-8")
    return {"old": vdir / "old.md", "new": vdir / "new.md"}


def parse_json(text):
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError(text[:200])
    return json.loads(match.group(0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", default="HEAD", help="旧版の git ref")
    ap.add_argument("--new", default=TARGET, help="新版のファイル（repo 相対）")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--model", default="opus")
    ap.add_argument("--judge-model", default="opus")
    ap.add_argument("--prompts", nargs="*", default=[], help="追加の質問ファイル（prompts.json と同じ形式）")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--check", action="store_true", help="隔離の確認だけ行う")
    args = ap.parse_args()

    workdir = tempfile.mkdtemp(prefix="claude-md-ab-")
    out = Path(args.out)
    variants = materialize(out, args.old, args.new)
    if not check_isolation(workdir, args.model, variants["new"]):
        sys.exit("CLAUDE.md の隔離が効いていない。比較が成り立たないので中止する。")
    if args.check:
        return

    prompts = []
    for f in [HERE / "prompts.json", *map(Path, args.prompts)]:
        prompts += json.loads(f.read_text(encoding="utf-8"))
    criteria = (HERE / "regression.md").read_text(encoding="utf-8")

    def respond(variant, p, i):
        path = out / "responses" / variant / f"{p['id']}_{i}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(claude(p["prompt"], workdir, args.model, variants[variant]),
                            encoding="utf-8")
        return path.read_text(encoding="utf-8")

    def compare(job):
        p, i = job
        old, new = respond("old", p, i), respond("new", p, i)
        path = out / "judgments" / f"{p['id']}_{i}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            # 位置の偏りを避けるため、新版を A と B のどちらに置くかを質問ごとに変える
            new_is_a = random.random() < 0.5
            a, b = (new, old) if new_is_a else (old, new)
            judge_input = (f"{criteria}\n\n## ユーザーの質問\n{p['prompt']}\n\n"
                           f"## 応答 A\n{a}\n\n## 応答 B\n{b}")
            raw = parse_json(claude(judge_input, workdir, args.judge_model))
            # 判定を「新版が悪い / 旧版が悪い」に直して保存する
            to_new = {"A_worse": "new_worse", "B_worse": "old_worse", "same": "same"}
            verdict = {k: to_new[v if new_is_a else FLIP[v]]
                       for k, v in raw.items() if k != "note"}
            path.write_text(json.dumps({"verdict": verdict, "note": raw.get("note", ""),
                                        "new_was": "A" if new_is_a else "B"},
                                       ensure_ascii=False), encoding="utf-8")
        print(f"done {p['id']} #{i}", flush=True)
        return {"prompt": p, "run": i, "old": old, "new": new,
                **json.loads(path.read_text(encoding="utf-8"))}

    jobs = [(p, i) for p in prompts for i in range(args.runs)]
    with ThreadPoolExecutor(args.jobs) as pool:
        rows = list(pool.map(compare, jobs))

    regressions = [(r, k) for r in rows for k, v in r["verdict"].items() if v == "new_worse"]
    lines = ["# CLAUDE.md 比較レポート", ""]
    if regressions:
        lines += ["## 新版で悪化した箇所", ""]
        lines += [f"- {r['prompt']['id']} #{r['run']}: {k}" for r, k in regressions]
    else:
        lines += ["新版で明らかな悪化はなかった。"]
    improved = [(r, k) for r in rows for k, v in r["verdict"].items() if v == "old_worse"]
    if improved:
        lines += ["", "改善した箇所: " + ", ".join(f"{r['prompt']['id']} #{r['run']} {k}"
                                              for r, k in improved)]
    for r in rows:
        p = r["prompt"]
        lines += ["", "---", "", f"## {p['id']} #{r['run']}", "",
                  f"見どころ: {p['focus']}", "", f"質問: {p['prompt']}", "",
                  f"判定: {r['note']}", "",
                  f"### 旧版（{len(r['old'])} 字）", "", r["old"], "",
                  f"### 新版（{len(r['new'])} 字）", "", r["new"]]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:lines.index("---") if "---" in lines else None]))


if __name__ == "__main__":
    main()
