"""Small command-line interface for both evaluation modes."""
import argparse
from datetime import datetime
import importlib.util
from pathlib import Path
import sys

from site_audit.config import ModelConfig
from site_audit import pipeline, report


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("必须大于 0")
    return number


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("不能小于 0")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description="网站采集、规则检查与可替换模型的内容审查")
    commands = parser.add_subparsers(dest="command", required=True)
    collect = commands.add_parser("collect", help="抓取公开网站，生成规则报告和模型材料包")
    collect.add_argument("url")
    collect.add_argument("--out", type=Path, default=Path("runs") / datetime.now().strftime("%Y%m%d-%H%M%S"))
    collect.add_argument("--max-pages", type=positive, default=30)
    collect.add_argument("--max-depth", type=nonnegative, default=5)
    collect.add_argument("--review-pages", type=positive, default=20)
    collect.add_argument("--scope", choices=("path", "site"), default="path")
    collect.add_argument("--render", choices=("never", "auto", "always"), default="never")
    collect.add_argument("--pagespeed", action="store_true", help="另行调用 Google PageSpeed 检查入口页")
    export = commands.add_parser("export", help="重新生成模型材料包")
    export.add_argument("folder", type=Path)
    export.add_argument("--review-pages", type=positive, default=20)
    evaluate = commands.add_parser("evaluate", help="使用本地配置的模型接口审查材料包")
    evaluate.add_argument("folder", type=Path)
    evaluate.add_argument("--fresh", action="store_true", help="重新调用已成功的任务，可能产生额外费用")
    imp = commands.add_parser("import", help="导入当前聊天模型生成的 answers.json")
    imp.add_argument("folder", type=Path)
    imp.add_argument("--answers", type=Path, required=True)
    render = commands.add_parser("report", help="根据已有证据生成报告")
    render.add_argument("folder", type=Path)
    demo = commands.add_parser("demo", help="生成离线构造样例，不访问网站或模型")
    demo.add_argument("--out", type=Path, default=Path("runs/demo"))
    demo.add_argument("--with-example-judgments", action="store_true", help="加入明确标注的人工构造模型响应")
    commands.add_parser("doctor", help="检查依赖与配置，不请求模型")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            for name in ("requests", "bs4", "lxml", "playwright"):
                print(name + ": " + ("已安装" if importlib.util.find_spec(name) else "未安装"))
            try:
                cfg = ModelConfig.from_env()
                print(f"模型配置已读取：{cfg.model}；模式 {cfg.response_mode}；请求上限 {cfg.max_requests}。未调用接口。")
            except ValueError as error:
                print("模型配置尚未就绪：" + str(error))
            return 0
        if args.command == "collect":
            pipeline.collect(args.url, args.out, args.max_pages, args.max_depth, args.scope, args.render, args.pagespeed)
            pipeline.export_pack(args.out, args.review_pages)
            folder = args.out
        elif args.command == "export":
            pipeline.export_pack(args.folder, args.review_pages)
            folder = args.folder
        elif args.command == "evaluate":
            pipeline.evaluate_api(args.folder, ModelConfig.from_env(), resume=not args.fresh)
            folder = args.folder
        elif args.command == "import":
            count = pipeline.import_answers(args.folder, args.answers)
            print(f"已导入 {count} 个经过格式与原文校验的任务。")
            folder = args.folder
        elif args.command == "demo":
            from site_audit.demo import make_demo
            make_demo(args.out, args.with_example_judgments)
            folder = args.out
        else:
            folder = args.folder
        data = report.render(folder)
        print(f"报告：{(folder / 'report.html').resolve()}")
        print(f"模型任务覆盖：{data['model_jobs_assessed']}/{data['model_jobs_total']}；整改项：{len(data['actions'])}。")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("无法完成：" + str(error), file=sys.stderr)
        return 1
