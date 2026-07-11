#!/usr/bin/env python3
"""Skill ディレクトリの機械検査。

creating-skills の検算ステップから実行する:
    python validate-skill.py <skill-dir>

検査項目:
- SKILL.md の存在・frontmatter (name / description の公式制約)
- name とディレクトリ名の整合 (コマンド名はディレクトリ名由来のため)
- SKILL.md の行数上限
- 可搬性: 絶対パス・memory リンク・トークン様文字列・メールアドレス (全 .md と scripts/ 配下)
- SKILL.md フェンス内の非エスケープ置換構文 (メタスキルの罠)
- references/*.md のメタデータブロックと目次

終了コード: 0 = エラーなし (警告は許容) / 1 = エラーあり / 2 = 引数誤り

規範文書が禁止例そのものを提示する行は、プレースホルダ (<name> 等) や
省略記号 (...) を含むため自動で除外される。それ以外で意図的に許可したい行には
`validate-skill: allow` を行内に含める。
"""

import re
import sys
from pathlib import Path

# 公式仕様: name は 64 文字以内・小文字/数字/ハイフンのみ
NAME_MAX = 64
NAME_RE = re.compile(r"^[a-z0-9-]+$")
# 公式仕様: name に含めてはならない予約語
RESERVED_WORDS = ("anthropic", "claude")
# 公式仕様: description は 1024 文字以内
DESC_MAX = 1024
# 公式推奨: SKILL.md 本体は 500 行以下
SKILL_MAX_LINES = 500
# 公式推奨: 100 行超の reference には目次 (partial read でも全体像が見えるように)
REF_TOC_LINES = 100
# 目次は frontmatter とタイトルの直後を想定し、先頭 30 行以内を探す
TOC_SEARCH_LINES = 30

XML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
# 規範文書の禁止例に現れるプレースホルダ。実際に漏洩したパスには現れない
PLACEHOLDER_RE = re.compile(r"<[\w-]+>|\.\.\.")

# 可搬性・秘匿情報の検査パターン (writing-rules「配布版から外すべきパターン」に対応)
PORTABILITY_PATTERNS = [
    ("絶対パス (Windows)", re.compile(r"[A-Za-z]:[\\/]Users[\\/]")),  # validate-skill: allow
    ("絶対パス (macOS)", re.compile(r"(?<![\w.])/Users/")),  # validate-skill: allow
    ("絶対パス (Linux)", re.compile(r"(?<![\w.])/home/")),  # validate-skill: allow
    ("file:// URL", re.compile(r"file:///")),  # validate-skill: allow
    ("memory リンク", re.compile(r"\.claude[\\/]projects[\\/]\S*memory")),  # validate-skill: allow
    ("トークン様文字列", re.compile(r"(?:ghp_|github_pat_|sk-ant-|xox[bp]-)[A-Za-z0-9_-]{10,}")),  # validate-skill: allow
    ("メールアドレス", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),  # validate-skill: allow
]
# メールはダミードメイン・noreply 形式なら許容
EMAIL_ALLOWED_RE = re.compile(r"@(?:example\.|users\.noreply\.)")

# フェンス内の非エスケープ置換構文 (\$ でエスケープされていないもの)
UNESCAPED_SUBST_RE = re.compile(r"(?<!\\)\$(?:ARGUMENTS|\d)")

errors = []
warnings = []


def error(path, line_no, msg):
    errors.append(f"ERROR {path}:{line_no}: {msg}")


def warn(path, line_no, msg):
    warnings.append(f"WARN  {path}:{line_no}: {msg}")


def parse_frontmatter(lines):
    """先頭の --- ブロックを {key: value} で返す。無ければ None。"""
    if not lines or lines[0].strip() != "---":
        return None
    fm = {}
    key = None
    for i, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fm
        m = re.match(r"^([\w-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fm[key] = m.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            # ブロックスカラー (>- 等) や折返しの継続行を値に連結する
            if fm[key] in (">", ">-", "|", "|-"):
                fm[key] = line.strip()
            else:
                fm[key] += " " + line.strip()
    return None  # 閉じの --- が無い


def check_skill_md(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        error(skill_md, 1, "SKILL.md が存在しない")
        return

    lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    rel = skill_md.relative_to(skill_dir.parent)

    if len(lines) > SKILL_MAX_LINES:
        error(rel, len(lines), f"SKILL.md が {SKILL_MAX_LINES} 行を超えている ({len(lines)} 行)。references/ に分割する")

    fm = parse_frontmatter(lines)
    if fm is None:
        error(rel, 1, "frontmatter (--- ブロック) が無いか閉じられていない")
        fm = {}

    # ディレクトリ名がコマンド名になるため、name と同じ制約を課す
    dir_name = skill_dir.name
    if len(dir_name) > NAME_MAX or not NAME_RE.match(dir_name):
        error(rel, 1, f"ディレクトリ名 '{dir_name}' が name 制約 (小文字/数字/ハイフン, {NAME_MAX} 字以内) を満たさない")
    for word in RESERVED_WORDS:
        if word in dir_name:
            error(rel, 1, f"ディレクトリ名 '{dir_name}' に予約語 '{word}' が含まれる")

    name = fm.get("name", "")
    if name:
        if len(name) > NAME_MAX:
            error(rel, 2, f"name が {NAME_MAX} 文字を超えている")
        if not NAME_RE.match(name):
            error(rel, 2, "name は小文字・数字・ハイフンのみ")
        for word in RESERVED_WORDS:
            if word in name:
                error(rel, 2, f"name に予約語 '{word}' が含まれる")
        if XML_TAG_RE.search(name):
            error(rel, 2, "name に XML タグが含まれる")
        if name != dir_name:
            warn(rel, 2, f"name '{name}' とディレクトリ名 '{dir_name}' が不一致 (コマンド名はディレクトリ名由来)")

    desc = fm.get("description", "")
    if not desc:
        error(rel, 2, "description が無いか空 (Claude が起動判断に使う最重要フィールド)")
    else:
        if len(desc) > DESC_MAX:
            error(rel, 2, f"description が {DESC_MAX} 文字を超えている ({len(desc)} 文字)")
        if XML_TAG_RE.search(desc):
            error(rel, 2, "description に XML タグが含まれる")

    # フェンス内の非エスケープ置換構文: SKILL.md 本文はレンダリングされるため、
    # 例示のつもりのリテラルが実引数に置換されて壊れる (メタスキルの罠)
    in_fence = False
    for i, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence and UNESCAPED_SUBST_RE.search(line):
            warn(rel, i, "フェンス内に非エスケープの置換構文 ($ARGUMENTS / $N)。例示なら \\$ でエスケープするか reference 側に置く")  # validate-skill: allow


def check_portability(skill_dir):
    targets = sorted(skill_dir.rglob("*.md"))
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        targets += sorted(scripts_dir.glob("*"))
    seen = set()
    for f in targets:
        if not f.is_file() or f in seen:
            continue
        seen.add(f)
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # バイナリ等はスキップ
        rel = f.relative_to(skill_dir.parent)
        for i, line in enumerate(text.splitlines(), start=1):
            if "validate-skill: allow" in line or PLACEHOLDER_RE.search(line):
                continue
            for label, pattern in PORTABILITY_PATTERNS:
                m = pattern.search(line)
                if not m:
                    continue
                if label == "メールアドレス" and EMAIL_ALLOWED_RE.search(m.group(0)):
                    continue
                error(rel, i, f"{label}: {m.group(0)!r} は配布版に含めない (writing-rules「配布版から外すべきパターン」)")


def check_references(skill_dir):
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return
    for f in sorted(refs_dir.glob("*.md")):
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        rel = f.relative_to(skill_dir.parent)
        fm = parse_frontmatter(lines)
        if fm is None:
            warn(rel, 1, "メタデータブロックが無い (source/purpose, fetched_at, note を置く)")
        elif not any(k in fm for k in ("source", "source_primary", "sources", "purpose")):
            warn(rel, 1, "メタデータに source / sources / purpose のいずれも無い")
        if len(lines) > REF_TOC_LINES:
            head = "\n".join(lines[:TOC_SEARCH_LINES])
            if "目次" not in head and "Contents" not in head:
                warn(rel, 1, f"{REF_TOC_LINES} 行超の reference に目次が無い (先頭 {TOC_SEARCH_LINES} 行以内に置く)")


def main():
    # Windows コンソールの既定 (cp932) では日本語メッセージ中の記号が encode できず
    # 落ちるため、stdout を UTF-8 に固定する
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.is_dir():
        print(f"ERROR: ディレクトリが存在しない: {sys.argv[1]}")
        return 2

    check_skill_md(skill_dir)
    check_portability(skill_dir)
    check_references(skill_dir)

    for line in errors + warnings:
        print(line)
    print(f"{skill_dir.name}: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
