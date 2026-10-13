"""Build the public rule handbook from the actual extracted rules and rubrics.

Definitions derived from AgriciDaniel/jev-seo (MIT, Copyright 2026 Agrici Daniel).
Chinese explanations are research annotations, not executable rule expressions.
"""
import json
from pathlib import Path

from site_audit.upstream.checks import RULES, SRC
from site_audit.upstream.questions import page_questions, site_questions, pair_question
from site_audit.evaluation import SYSTEM_PROMPT

ROOT = Path(__file__).resolve().parent
WEB = ROOT.parent / "web"
COMMIT = "55a184a3b0d09565a4c84268f725a47784e62528"
UPSTREAM = f"https://github.com/AgriciDaniel/jev-seo/blob/{COMMIT}/jevseo/"

# title, observed condition, practical next step, interpretation limit
RULE_NOTES = {
    "robots_missing": ("未找到 robots.txt", "站点根文件缺失、请求失败、返回 HTML 或正文为空。", "按需要提供抓取政策和站点地图入口。", "缺失不等于禁止抓取，也不自动意味着收录故障。"),
    "robots_blocks_site": ("根路径阻止搜索爬虫", "根路径不允许通用爬虫，或 Googlebot/Bingbot 至少一个不允许。", "核实是否意图屏蔽公开站点，再调整对应策略。", "当前规则以根路径为探测点；不能覆盖所有子路径策略。"),
    "sitemap_missing": ("未发现可用站点地图", "robots 指向或默认 /sitemap.xml 的文件没有可用解析结果。", "按需提供列出规范、可收录网址的 XML 站点地图。", "没有地图不等于搜索引擎无法发现页面；小型站点也可能不需要。"),
    "sitemap_errors": ("部分站点地图不可用", "至少有可用地图，同时其他地图请求或解析失败。", "修复不可用的文件或地图引用。", "只覆盖发现到的地图；未检查全部地图生成逻辑。"),
    "sitemap_bad_urls": ("地图中包含异常网址", "已抓取的地图条目是重定向、HTTP 错误或非可收录页面。", "地图优先列出最终、正常、规范的网址。", "没抓到的条目状态未知；不会证明整张地图正确。"),
    "not_in_sitemap": ("可收录页面未列入地图", "成功抓取、按本地判定可收录的页面不在地图 URL 集合中。", "结合发布策略补充重要页面。", "这里的可收录只是本地筛选，不是 Google 实际收录。"),
    "http_errors": ("页面请求失败", "页面返回 4xx/5xx，或非 robots 阻止的请求失败。", "检查地址、发布文件与服务状态，按目的恢复或重定向。", "网络失败可能是暂时故障；仅凭响应无法定位后端代码根因。"),
    "broken_internal_links": ("站内链接目标不可达", "目标状态为 4xx/5xx 或不可达；robots 阻止目标按未知处理。", "更新链接、恢复目标，或移除失效入口。", "采集时点的可达性需要复核，未进行完整用户业务流程测试。"),
    "redirect_chains": ("重定向超过一跳", "记录的重定向链包含多于一次跳转。", "让跳转尽量直接到最终目标。", "某些鉴权或地区跳转有业务目的，不应直接删除。"),
    "links_to_redirects": ("站内链接经过重定向", "已抓取页面链接到已知重定向地址。", "可更新为最终正常地址，减少绕行。", "有意保持稳定短链接时，需结合业务判断。"),
    "noindex": ("页面声明禁止收录", "页面 meta robots 或 X-Robots-Tag 含 noindex；入口页提升为严重项。", "确认用途；需公开收录的页面再移除 noindex。", "测试站、账户页可能应该 noindex；抓取禁止与收录禁止不同。"),
    "canonical_missing": ("没有规范网址声明", "本地判定可收录的页面未发现 canonical。", "在重复网址需要合并信号时明确规范版本。", "canonical 并非每页必须补齐的硬性条件；不能保证 Google 采纳。"),
    "canonical_elsewhere": ("规范网址指向其他页", "canonical 与当前页面网址不同。", "核实重复关系，确认是否应指向自己。", "重复页面指向主版本可能完全正确。"),
    "canonical_broken": ("规范目标异常", "规范目标为已知重定向或返回错误。", "指向最终正常、可作为主版本的网址。", "未采集/探测的目标不能确认为正常。"),
    "soft_404": ("不存在的网址返回 200", "随机生成的不存在地址返回 HTTP 200。", "真实缺失页应返回适当的 404/410。", "这是状态探测提示，不是完整的 Google soft 404 判定；SPA 需结合页面内容。"),
    "host_temporary_redirect": ("域名或 HTTPS 使用临时跳转", "HTTP 或域名变体的首次跳转为 302/303/307。", "永久迁移场景考虑 301/308。", "临时业务跳转可能有意；不是所有 302 都是错误。"),
    "host_variant": ("域名变体同时提供内容", "www/非 www 变体返回 200，未导向选定主域名。", "若内容重复，统一首选版本与跳转政策。", "域名变体响应探测不能证明两个网站正文完全相同。"),
    "no_https": ("HTTPS 或 HTTP 转向存在问题", "入口不是 HTTPS，或根 HTTP 探测未转向 HTTPS。", "确认安全访问与适当的永久跳转。", "对输入项目路径和站点根路径的响应需分别理解。"),
    "deep_pages": ("页面位于较深链接层级", "采集深度大于 3 且小于 99。", "为重要页面增加相关导航或主题聚合入口。", "三次点击是经验阈值；深度 99 的地图种子不按已知点击深度处理。"),
    "orphan_pages": ("地图页面缺少已见内链", "地图内的非入口页面，在本次抓取中没有内部入链。", "检查是否需要从相关页面链接过去。", "采样之外可能存在入链，不能据此断言全站孤立。"),
    "js_dependent": ("正文依赖 JavaScript 渲染", "渲染后内容更多且满足上游 js_dependent 判定。", "重要内容考虑服务端输出或预渲染。", "默认不渲染；未触发不代表没有 JavaScript 依赖。"),
    "title_missing": ("页面标题缺失", "本地判定可收录的页面没有非空 title。", "添加准确、可区分的页面标题。", "检查采集到的 HTML；动态注入标题需考虑渲染覆盖。"),
    "title_duplicate": ("多个页面标题相同", "成功 HTML 页的标题去首尾空格、转小写后重复。", "让不同目的页面拥有可区分标题。", "相同标题是提示，需要判断是否为合理重复版本。"),
    "title_length": ("标题长度偏短或偏长", "存在标题的可收录页面，字符数不在 15–65 范围。", "保持简洁、准确，结合实际展示检查。", "字符范围是经验值，不是 Google 固定上限；中文与像素宽度不同。"),
    "multiple_titles": ("多个 title 元素", "解析到的 title 数量超过 1。", "整理为一个清晰的页面标题。", "规则检查元素数量，不直接判断搜索结果显示哪一段。"),
    "meta_missing": ("页面摘要缺失", "可收录页面缺少 meta description。", "为重要页面提供准确摘要。", "搜索引擎可自行生成摘要；缺失不等于无法展示。"),
    "meta_duplicate": ("多个页面摘要相同", "页面摘要去首尾空格、转小写后重复。", "针对各页内容写不同摘要。", "需结合页面目的判断是否有必要区分。"),
    "h1_missing": ("未发现 H1 主标题", "可收录页面没有非空 H1。", "用清晰的可见主标题说明主题。", "属于上游结构经验建议；不是单独的排名保证。"),
    "h1_multiple": ("存在多个 H1", "可收录页面的 H1 数量大于 1。", "核实页面层级和主要主题表达。", "多个 H1 不自动意味着搜索引擎错误，需结合结构。"),
    "heading_skips": ("标题层级有跳跃", "解析标题顺序时记录到跨级嵌套。", "按语义组织 H1/H2/H3 等层级。", "这是结构建议；完整可访问性仍需另行审查。"),
    "lang_missing": ("未声明页面语言", "html 元素没有 lang 属性。", "填写与主要内容一致的语言标记。", "检查声明，不验证整页语言或多语言翻译质量。"),
    "viewport_missing": ("移动端视口声明缺失", "未发现 viewport meta。", "提供适当的响应式视口设置。", "存在标签也不能证明手机布局、触控或可读性合格。"),
    "thin_content": ("正文词数较少", "可收录页按原解析器词数低于 150。", "对需要回答用户需求的页面补充有用内容。", "词数不是排名因子；中文连续文本不是按语义词切分，不能机械扩写。"),
    "duplicate_content": ("多个页面正文相同", "正文词数至少 50，规范化后正文哈希重复。", "核实重复版本、合并或规范关系。", "只查近乎完全相同的文本，不代表语义相似度全面检测。"),
    "images_alt": ("图片缺少 alt 属性", "存在没有 alt 属性的 img。", "信息图片提供准确描述；装饰图片可使用空 alt。", "空 alt 与缺失不同；该规则不判断已有描述是否准确。"),
    "images_dimensions": ("图片缺少宽高", "img 未同时提供 width 与 height。", "预留适当尺寸或布局空间。", "CSS 也可能预留空间；缺失属性不等于已发生布局抖动。"),
    "no_structured_data": ("入口未发现结构化数据", "入口记录没有 JSON-LD 或 microdata 类型。", "有适用实体信息时提供真实、一致的标记。", "不是所有网站都需要每一种标记；缺失不等于不能被收录。"),
    "jsonld_errors": ("JSON-LD 无法解析", "JSON-LD 解析产生错误。", "修复语法并校验标记内容。", "语法正确不代表 Google 富媒体展示资格或内容真实性。"),
    "schema_required": ("部分结构化字段不完整", "检查 Product、SoftwareApplication、BreadcrumbList、LocalBusiness 的选定必需字段。", "补充真实字段，或移除无法真实补齐的标记。", "只实现选定类型和字段；不是完整 Schema 验证器，规范需持续更新。"),
    "faq_rich_result_limited": ("FAQ 富媒体展示有资格限制", "页面标记包含 FAQPage。", "确认用途和展示资格，再决定保留。", "信息提示；不是所有网站添加 FAQ 都能获得搜索富媒体展示。"),
    "og_missing": ("分享预览标题或图片缺失", "可收录页面缺少 og:title 或 og:image。", "按分享需要补齐准确的 Open Graph 信息。", "这检查分享元信息，不是直接排名检查。"),
    "hreflang_issues": ("语言版本标记缺少自引用", "存在 hreflang，但列表中没有当前页面自己。", "结合多语言版本补齐正确对应与互返关系。", "当前代码只检测自引用；没有完整验证互返或 x-default。"),
    "ai_bots_blocked": ("根路径限制 AI 爬虫", "robots 根路径探测中至少一个所列 AI user-agent 不允许。", "按内容使用政策决定哪些抓取允许。", "只提示政策，不要求全部开放；不同爬虫用途不同。"),
    "llms_txt_missing": ("未发现 llms.txt", "根路径文件未成功返回非 HTML 且正文超过 20 字符。", "如果认为对消费者有用，可提供导览文件。", "社区提议，可选信息，不是 Google AI 搜索的必需文件。"),
    "hsts_missing": ("HTTPS 入口未声明 HSTS", "HTTPS 入口响应没有 Strict-Transport-Security。", "在 HTTPS 稳定后按部署策略配置。", "响应配置提示，不是完整安全审计。"),
    "security_headers": ("部分常见响应头缺失", "缺少 nosniff、Referrer-Policy 或框架嵌入政策等。", "结合实际功能补充合适的响应策略。", "存在响应头不证明鉴权、注入或后端业务安全。"),
    "mixed_content": ("HTTPS 页面引用 HTTP 资源", "发现选定 img/script/媒体/样式等资源的 HTTP 引用。", "使用安全资源地址或去除无效引用。", "静态解析并不覆盖所有动态网络请求。"),
    "favicon_missing": ("入口未声明网站图标", "未发现 link rel=icon。", "按站点展示需要声明图标。", "不证明图标在各搜索结果和浏览器中已正确展示。"),
    "slow_ttfb": ("本次首字节响应偏慢", "抓取测得 ttfb_ms 大于 800。", "结合多次测量调查缓存、网络与服务响应。", "单次爬虫观测不是完整 Core Web Vitals 或真实用户性能。"),
    "heavy_html": ("HTML 响应体较大", "页面记录 bytes 大于 500,000。", "检查内联数据和重复标记，按需要减少传输。", "经验阈值；不代表整页资源总量或下载耗时。"),
    "generic_anchors": ("部分站内锚文本过于通用", "英文锚文本规范化后命中 click here/read more 等集合。", "让入口文字说明目标内容。", "当前通用词集合主要是英文，不完整覆盖中文锚文本。"),
    "broken_external_links": ("抽样外链返回错误", "样本外链状态至少 400，但排除 401/403/429/999。", "复核可达性，更新或移除真正失效外链。", "只采样前 80 个外链；限制访问与反爬响应不直接判作死链。"),
}

# Chinese research rendering of the original question dimensions.
QUESTION_NOTES = {
    "page_type": ("页面类型", "判断这页是服务、文章、文档还是其他类型，让后续建议符合用途。", ["首页", "产品或服务", "分类或列表", "文章或指南", "团队或关于", "联系或地址", "定价", "案例或证明", "支持或文档", "法律或政策", "其他"]),
    "intent": ("用户搜索需求", "判断来访者是学习、比较、购买、导航还是寻找本地服务。", ["信息了解", "商业比较", "交易行动", "品牌导航", "本地需求", "不明确"]),
    "importance": ("业务重要性", "判断这页对网站目标与潜在客户有多重要。", ["工具/法律页，对获客无直接作用", "轻度支持页面", "能帮助潜在客户了解或信任", "主要产品、线索或销售核心页"]),
    "action": ("建议处理方式", "判断应保留改善、重写，还是人工核实合并/移除。", ["保留或改善", "重写", "考虑合并或移除"]),
    "helpfulness": ("对用户是否有用", "正文是否充分回答用户为这个主题而来的需求。", ["几乎没有可用内容", "浅显，仍需到别处寻找答案", "有足够实用细节回答主要问题", "全面回答并覆盖后续问题"]),
    "specificity": ("是否具体且有独特信息", "有没有自己的功能、数字、流程、案例或第一手经验。", ["几乎全是通用宣传", "通用内容中少量具体信息", "多处具体功能、数字或示例", "有专属数据、成果或第一手细节"]),
    "answer_first": ("开头是否直接说明重点", "主标题后前两句话是否说明读者得到什么。", ["直接说出答案、服务或内容范围", "口号、悬念、背景等占据开头"]),
    "citable": ("是否有可独立引用的陈述", "定义、数字和事实是否有清晰主语与背景，便于独立理解。", ["主要是口号，无可引用具体事实", "少量事实，依赖上下文", "多个清晰完整的定义或数字", "大量精确、独立可理解的陈述"]),
    "trust": ("可信依据", "是否展示真实作者、资质、来源、案例、结果或联系信息。", ["匿名或无支撑宣传", "有名称等信号，缺少证明", "有人员、资质、评价、来源等依据", "有可验证专家、数据、成果与责任主体"]),
    "clear_next_step": ("是否有合理下一步", "是否提供与本页目的相关的联系、试用、购买或自然阅读入口。", ["有具体相关行动入口", "只有通用导航或没有行动邀请"]),
    "title_fit": ("标题与正文是否匹配", "标题是否准确区分这页，并说明值得打开的内容。", ["误导或与内容无关", "只说品牌或模糊主题", "准确描述页面主题", "贴近用户表达并有具体打开理由"]),
    "meta_fit": ("摘要与正文是否匹配", "页面描述是否准确、具体地概括提供的内容。", ["无关、模板或关键词堆积", "相关但模糊", "准确概括页面", "准确具体并有访问理由"]),
    "h1_fit": ("主标题是否点明主题", "H1 是否直接说明本页主题，而不是口号或泛称。", ["主标题点明主题", "只是口号、泛称或其他主题"]),
    "business_model": ("网站业务类型", "从入口材料判断网站主体服务什么业务。", ["本地服务", "电商", "软件或 SaaS", "机构/B2B 服务", "媒体出版", "教育课程", "公益公共服务", "个人作品集", "其他"]),
    "value_prop": ("入口价值说明", "是否说清提供什么、面向谁以及选择的理由。", ["看不出提供什么", "可猜到但模糊或埋得很深", "产品与对象清晰，选择理由较弱", "开头明确对象与具体价值；需要位置证据支撑"]),
    "entity_clarity": ("主体介绍清晰度", "是否说清名称、业务与市场/服务对象或地区。", ["这些信息清楚", "至少一项缺失或不清楚"]),
    "topical_focus": ("全站主题聚焦", "依据提供的页面标题判断主题是否连贯。", ["主题分散无可见联系", "松散主题，较多无关页", "清晰主题，少量偏离", "围绕相关主题有清晰组织"]),
    "serves_local_area": ("是否面向具体地区", "是否有明确地址、服务区域或当地客户信息。", ["明确表现为服务某个地区", "不限定地区，或未说明"]),
    "same_search_need": ("页面是否满足同一需求", "两页是否让同一位搜索者觉得可以互相替代。", ["目标需求相同，可能互相替代", "需求、对象或阶段不同"]),
}


def build():
    if set(RULE_NOTES) != set(RULES):
        raise ValueError("Chinese rule notes must match the actual rule IDs")
    rules = []
    for rid, definition in RULES.items():
        category, severity, original_title, original_fix, source, effort, heuristic = definition
        title, condition, fix, limit = RULE_NOTES[rid]
        rules.append({"id": rid, "category": category, "severity": severity, "title": title,
                      "condition": condition, "fix": fix, "limit": limit,
                      "heuristic": heuristic, "effort": effort, "reference": SRC[source],
                      "source": UPSTREAM + "checks.py", "original_title": original_title,
                      "original_fix": original_fix})
    registry = []
    groups = (("page", page_questions({"title": "sample", "meta_description": "sample", "h1": ["sample"]})),
              ("site", site_questions()), ("pair", {"same_search_need": pair_question("pair")}))
    for scope, questions in groups:
        for key, definition in questions.items():
            title, purpose, translated = QUESTION_NOTES[key]
            criteria = definition["criteria"]
            if len(translated) != len(criteria):
                raise ValueError(f"Mismatched criterion count for {key}")
            values = list(criteria) if isinstance(criteria, dict) else list(range(len(criteria)))
            registry.append({"id": key, "scope": scope, "type": definition["type"], "title": title,
                             "purpose": purpose, "criteria": [{"value": value, "label": label} for value, label in zip(values, translated)],
                             "source": UPSTREAM + "jev.py"})
    catalogue = {"schema_version": "1.0", "updated": "2026-10-13", "source_commit": COMMIT,
                 "attribution": "Definitions derived from AgriciDaniel/jev-seo, Copyright (c) 2026 Agrici Daniel, MIT. Chinese research annotations by this repository.",
                 "rules": rules, "questions": registry}
    WEB.mkdir(exist_ok=True)
    payload = json.dumps(catalogue, ensure_ascii=False, indent=2)
    (WEB / "catalog.json").write_text(payload + "\n", encoding="utf-8")
    (WEB / "catalog.js").write_text("/* MIT upstream attribution: see LICENSE.txt and catalog.json. */\nwindow.AUDIT_CATALOG = " + payload + ";\n", encoding="utf-8")
    (WEB / "LICENSE.txt").write_bytes((ROOT / "LICENSE.upstream").read_bytes())
    (WEB / "review-prompt.txt").write_text("网站内容审查提示词 · 本仓库提取实验\n\n" + SYSTEM_PROMPT + "\n使用方法：由采集程序提供 state 与 questions，再按材料审查。此文本本身不提供网页访问能力，也不替代固定规则执行器。\n", encoding="utf-8")
    print(f"Public handbook: {len(rules)} rules, {len(registry)} question dimensions")


if __name__ == "__main__":
    build()
