# agent-assets

Agent に与える資産（Skill・CLAUDE.md・hooks・settings）と Markdown 文書を、作り・監査し・読みやすくするための Claude Code プラグイン。

## 含まれる Skill

| Skill | 内容 |
|---|---|
| `/agent-assets:creating-skills` | Skill を新規作成・修正するときの規約、テンプレート、バリデータ（`scripts/validate-skill.py`） |
| `/agent-assets:context-audit` | リポが Agent に与えている資産を横断監査し、バグ・stale・矛盾・重複を報告して直す |
| `/agent-assets:readability-audit` | Markdown 文書の可読性を診断し、読者の認知負荷が下がる形に編集する |

`context-audit` と `readability-audit` は、Skill を編集したときの検算に `creating-skills` のバリデータを使う。3 つを 1 つのプラグインにまとめているのはこのため。

## 依存

- Python 3（`validate-skill.py`）

## 導入

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install agent-assets@config-plugins
```
