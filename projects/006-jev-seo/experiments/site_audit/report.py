"""Readable Chinese reports with facts and model suggestions kept distinct."""
from html import escape
from pathlib import Path

from site_audit.pipeline import current_pack, existing_results, read_json, write_json
from site_audit.upstream.checks import SEVERITY_WEIGHT

AREA = {"crawl": "抓取与索引", "onpage": "页面标签", "content": "内容质量", "links": "链接与结构",
        "structured": "结构化数据", "ai": "AI 搜索相关", "performance": "性能", "security": "响应配置"}
EFFORT = {1: "数小时", 2: "约一天", 3: "数天", 4: "独立项目"}
SPECS = {
    "helpfulness": ("content", "high", "重要页面未充分回答读者需求", "补充读者需要的答案、细节、案例和后续步骤。", 3),
    "specificity": ("content", "medium", "内容缺少具体信息", "补充自己的功能、数字、流程、案例和实际经验。", 3),
    "trust": ("content", "medium", "重要页面缺少可信依据", "补充真实作者、资质、来源、结果或联系信息。", 2),
    "title_fit": ("onpage", "medium", "标题与正文的匹配度较低", "让标题明确描述本页提供的内容。", 1),
    "meta_fit": ("onpage", "low", "页面描述不够准确具体", "写一段与正文一致的明确摘要。", 1),
    "h1_fit": ("onpage", "low", "主标题未明确说明主题", "用主标题说明本页的主题。", 1),
    "answer_first": ("ai", "low", "页面开头没有直接说明重点", "在开头简短说明答案或产品价值，随后展开。", 1),
    "citable": ("ai", "medium", "内容较少包含可独立理解的事实", "补充有明确主语、来源和背景的定义、数字或事实。", 2),
    "clear_next_step": ("content", "medium", "商业页面缺少明确下一步", "提供与本页相关的联系、购买、试用或阅读入口。", 1),
    "value_prop": ("content", "high", "入口页未清楚说明提供什么", "说明提供什么、适合谁，以及具体价值。", 2),
    "entity_clarity": ("ai", "low", "入口页对主体的介绍不够明确", "清楚说明名称、业务和目标读者或地区。", 1),
    "topical_focus": ("content", "low", "页面主题较分散", "检查页面主题与网站目标是否一致，整理分类与导航。", 2),
}


def number(answer, questions):
    if not answer or answer["value"] is None:
        return None
    if answer["type"] == "score":
        return answer["value"] / (len(questions["criteria"]) - 1)
    return answer["value"]


def model_findings(pack, saved):
    findings, importance = [], {}
    for job in pack["jobs"]:
        result = saved["results"].get(job["id"], {})
        if result.get("status") != "ok" or result.get("fingerprint") != job["fingerprint"]:
            continue
        answers = result["answers"]
        imp = number(answers.get("importance"), job["questions"].get("importance", {}))
        if imp is not None:
            importance[job["urls"][0]] = imp
        page_type = (answers.get("page_type") or {}).get("value")
        intent = (answers.get("intent") or {}).get("value")
        commercial = job["metadata"].get("homepage") or page_type in ("product_or_service", "pricing") or intent in ("commercial", "transactional", "local")
        def add(key, spec, answer):
            cat, severity, title, fix, effort = spec
            findings.append({"id": f"model_{key}_{job['id']}", "origin": "model", "category": cat,
                             "severity": severity, "title": title, "fix": fix, "effort": effort,
                             "urls": job["urls"], "count": len(job["urls"]), "evidence": answer["reason"],
                             "quotes": answer["evidence"], "heuristic": True, "needs_review": True,
                             "job_id": job["id"], "model": result.get("model")})
        for key, spec in SPECS.items():
            answer = answers.get(key)
            if not answer or answer["value"] is None:
                continue
            if page_type in ("legal_or_policy", "contact_or_location") and key not in ("title_fit", "h1_fit"):
                continue
            if key in ("helpfulness", "trust") and (imp is None or imp < 0.5):
                continue
            if key == "clear_next_step" and not commercial:
                continue
            value = number(answer, job["questions"][key])
            threshold = 0.6 if key == "value_prop" else 0.45
            if value is False or (answer["type"] == "score" and value < threshold):
                add(key, spec, answer)
        action = answers.get("action")
        if action and action["value"] in ("rewrite", "merge_or_remove"):
            if action["value"] != "merge_or_remove" or job["metadata"].get("word_count", 0) < 600:
                add("action", ("content", "medium", "建议人工复核页面是否需要改写或合并", "结合页面目的和实际数据决定改写、区分主题或合并；不要自动删除。", 3), action)
        pair = answers.get("same_search_need")
        if pair and pair["value"] is True:
            add("same_search_need", ("content", "medium", "两个页面可能满足同一搜索需求", "人工检查主题是否重叠，考虑区分内容或合并。", 2), pair)
    return findings, importance


def rank_actions(findings, importance, n_pages):
    items = []
    for finding in findings:
        if finding["severity"] == "info":
            continue
        reach = min(1, max(1, finding.get("count", 1)) / max(1, n_pages))
        imp = max((importance.get(url, 0.5) for url in finding["urls"]), default=0.5)
        impact = SEVERITY_WEIGHT[finding["severity"]] * (0.6 + 0.4 * reach) * (0.6 + 0.8 * imp)
        items.append({**finding, "impact_raw": impact})
    top = max((item["impact_raw"] for item in items), default=1)
    for item in items:
        item["impact"] = round(item.pop("impact_raw") / top * 100)
        item["priority"] = "P1" if item["severity"] == "critical" or item["severity"] == "high" and item["impact"] >= 40 else "P2" if item["severity"] == "high" or item["impact"] >= 30 else "P3"
    items.sort(key=lambda item: (item["priority"], -item["impact"], item["effort"]))
    for i, item in enumerate(items, 1):
        item["action_id"] = f"AUDIT-{i:03d}"
    return items


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def render(folder: Path):
    audit = read_json(folder / "audit.json")
    if (folder / "review-pack.json").exists():
        _, pack = current_pack(folder)
        saved = existing_results(folder, pack)
    else:
        pack = {"jobs": []}
        saved = {"results": {}, "ledgers": []}
    model_issues, importance = model_findings(pack, saved)
    pages = [p for p in audit["site"]["pages"] if p.get("kind") == "page"]
    actions = rank_actions(audit["rule_findings"] + model_issues, importance, len(pages))
    ok = sum(saved["results"].get(job["id"], {}).get("status") == "ok" and saved["results"].get(job["id"], {}).get("fingerprint") == job["fingerprint"] for job in pack["jobs"])
    unknown = sum(answer["value"] is None for job in pack["jobs"]
                  for result in [saved["results"].get(job["id"], {})]
                  if result.get("status") == "ok" and result.get("fingerprint") == job["fingerprint"]
                  for answer in result["answers"].values())
    data = {"audit_id": audit["audit_id"], "model_jobs_assessed": ok, "model_jobs_total": len(pack["jobs"]),
            "unknown_answers": unknown, "actions": actions, "model_findings": model_issues,
            "limits": audit["site"].get("limits", {}), "ledgers": saved["ledgers"]}
    write_json(folder / "findings.json", data)
    mode = "离线样例：页面为构造数据；模型来源见各任务记录" if audit["site"].get("fixture") else "公开网站抓取"
    lines = ["# 网站审查报告", "", f"来源：{mode}。", f"入口：{audit['site']['final_url']}",
             f"采集时间：{audit['collected_at']}", f"页面范围：{audit['site'].get('scope_path', '/')}",
             f"抓取页面记录：{len(pages)}；规则问题：{len(audit['rule_findings'])}；模型任务：{ok}/{len(pack['jobs'])}；证据不足答案：{unknown}。", "",
             "> 模型结论均待人工复核；未评估、调用失败和证据不足不代表没有问题。相对影响分只用于排序，不预测排名或流量。", "",
             "## 整改清单", "", "| 编号 | 优先级 | 来源 | 相对影响 | 工作量 | 问题 |", "| --- | --- | --- | --- | --- | --- |"]
    for item in actions:
        source = "模型建议 · 待复核" if item["origin"] == "model" else "规则检查" + (" · 经验建议" if item.get("heuristic") else "")
        lines.append(f"| {item['action_id']} | {item['priority']} | {source} | {item['impact']} | {EFFORT[item['effort']]} | {cell(item['title'])} |")
    if not actions:
        lines.append("\n本次覆盖范围未生成整改项；这不证明整个网站没有问题。")
    lines += ["", "## 问题证据与建议", ""]
    for item in actions:
        lines += [f"### {item['action_id']} · {item['title']}", "", f"领域：{AREA.get(item['category'], item['category'])}；来源：{item['origin']}。",
                  "涉及页面：" + "、".join(item["urls"]), "", "证据：" + item["evidence"], "", "建议：" + item["fix"], ""]
        for quote in item.get("quotes", []):
            lines.append(f"- 原文（{quote['field']}）：{cell(quote['quote'])}")
        if item.get("source"):
            lines.append("- 规则参考：" + item["source"])
        lines.append("")
    infos = [finding for finding in audit["rule_findings"] if finding["severity"] == "info"]
    if infos:
        lines += ["## 提示性信息", ""]
        lines += [f"- {finding['title']}：{finding['evidence']}" for finding in infos]
    lines += ["", "## 模型结论与遗漏", ""]
    for job in pack["jobs"]:
        result = saved["results"].get(job["id"], {})
        lines += [f"### {job['id']} · {job['kind']}", "", "页面：" + "、".join(job["urls"])]
        if result and result.get("fingerprint") != job["fingerprint"]:
            lines += ["状态：证据已变化，需重新评估", ""]
            continue
        if result.get("status") != "ok":
            lines += ["状态：" + result.get("status", "未评估"), ""]
            continue
        lines.append("模型：" + str(result.get("model")))
        for key, answer in result["answers"].items():
            value = "未评估（证据不足）" if answer["value"] is None else str(answer["value"])
            lines.append(f"- {key} = {value}：{answer['reason']}")
        lines.append("")
    lines += ["## 性能与范围", ""]
    performance = audit.get("performance")
    if performance:
        for run in performance["runs"]:
            lines.append(f"- {run['strategy']}：" + (run.get("error") or str(run.get("scores"))))
            if run.get("field_url") or run.get("field_origin"):
                lines.append("  真实用户数据：" + str(run.get("field_url") or run.get("field_origin")))
    else:
        lines.append("- 未调用 PageSpeed；抓取响应时间不能替代真实用户性能数据。")
    lines += ["- 抓取限制：" + str(data["limits"]),
              "- 未接入 Google Search Console、DataForSEO；未检查实际收录、关键词排名或后端代码。",
              "- 站点根目录 robots/sitemap、域名响应探测与链接目标状态检查可能超出页面路径范围；内容评估限定在所选页面。",
              "- 中文正文保留，但原上游词数和标题词集方法没有中文分词，薄内容与页面竞争筛选需要人工核实。", ""]
    markdown = "\n".join(lines)
    (folder / "report.md").write_text(markdown, encoding="utf-8")
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>网站审查报告</title>
<style>body{font-family:system-ui,"Microsoft YaHei",sans-serif;color:#1c2833;background:#f4f6f8;margin:0}main{max-width:1000px;margin:32px auto;padding:32px;background:white;border:1px solid #dce2e6;border-radius:12px}h1{font-size:28px}p{line-height:1.7}pre{font:14px/1.8 system-ui,"Microsoft YaHei",sans-serif;white-space:pre-wrap;overflow-wrap:anywhere}.tag{padding:6px 10px;background:#edf2ff;border-radius:6px;display:inline-block}@media(max-width:600px){main{margin:0;padding:20px;border:0}}</style><main><h1>网站审查报告</h1><p class="tag">规则证据 + 模型建议 · 人工复核</p><pre>'''
    # Escape all webpage and model content; the report never executes collected HTML.
    (folder / "report.html").write_text(html + escape(markdown) + "</pre></main></html>", encoding="utf-8")
    return data
