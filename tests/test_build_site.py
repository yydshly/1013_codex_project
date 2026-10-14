"""Verify publication selection, full summaries, safe paths and static-only output."""

import html
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_site import build_site


class BuildSiteTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="research-site-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git("init", "--quiet")

    def git(self, *arguments):
        return subprocess.run(
            ["git", *arguments], cwd=self.root, capture_output=True, check=True,
        )

    def create_project(self, directory="001-sample", *, tracked=False, summary="能力、原理、价值、输入输出与意义。", **changes):
        project = self.root / "projects" / directory
        (project / "web" / "data").mkdir(parents=True)
        (project / "assets").mkdir()
        (project / "experiments").mkdir()
        metadata = {
            "id": directory[:3], "slug": directory[4:], "name": "示例研究",
            "summary": summary, "status": "completed", "source_url": "https://github.com/example/upstream",
            "source_ref": "abcdef", "source_license": "MIT", "tags": ["原理", "演示"],
            "preview": "assets/preview.svg", "preview_caption": "真实演示截图说明", "demo_url": "",
        }
        metadata.update(changes)
        (project / "project.json").write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        (project / "README.md").write_text("Research documentation", encoding="utf-8")
        (project / "assets" / "preview.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        (project / "web" / "index.html").write_text('<script src="./app.js"></script><a href="../">总览</a>', encoding="utf-8")
        (project / "web" / "app.js").write_text('fetch("./data/book.json")', encoding="utf-8")
        (project / "web" / "data" / "book.json").write_text('{"text":"样例正文"}', encoding="utf-8")
        (project / "experiments" / ".env").write_text("API_KEY=never-publish", encoding="utf-8")
        if tracked:
            self.git("add", str(project.relative_to(self.root)))
        return project

    def test_default_only_collects_tracked_projects_and_tracked_assets(self):
        first = self.create_project(tracked=True)
        self.create_project("002-unrelated")
        (self.root / "projects" / "999-malformed").mkdir()
        (first / "web" / "untracked-notes.txt").write_text("local-only", encoding="utf-8")
        published = build_site(self.root)
        self.assertEqual([project["directory"] for project in published], ["001-sample"])
        self.assertTrue((self.root / "site-dist" / "001-sample" / "data" / "book.json").is_file())
        self.assertFalse((self.root / "site-dist" / "002-unrelated").exists())
        self.assertFalse((self.root / "site-dist" / "001-sample" / "untracked-notes.txt").exists())

    def test_explicit_preview_accepts_untracked_project_without_other_projects(self):
        self.create_project()
        self.create_project("002-unrelated")
        published = build_site(self.root, projects=["001-sample"])
        self.assertEqual(len(published), 1)
        self.assertFalse((self.root / "site-dist" / "002-unrelated").exists())

    def test_product_website_survives_build_with_safe_source_label(self):
        project = self.create_project()
        path = project / "project.json"
        metadata = json.loads(path.read_text(encoding="utf-8"))
        metadata.update(source_type="website", source_url="https://vibe42.ai/",
                        source_name='Vibe42 <官网>')
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
        build_site(self.root, projects=["001-sample"])
        home = (self.root / "site-dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<th scope="col">研究来源</th>', home)
        self.assertIn('href="https://vibe42.ai/">Vibe42 &lt;官网&gt; ↗</a>', home)
        self.assertIn('产品网站 · 公开资料研究', home)
        self.assertIn('<title>项目与产品研究 · 能力、原理与价值</title>', home)
        metadata["source_url"] = "https://name:secret@example.com/"
        path.write_text(json.dumps(metadata), encoding="utf-8")
        with self.assertRaises(ValueError):
            build_site(self.root, projects=["001-sample"])

    def test_all_tracked_demos_remain_and_are_ordered(self):
        self.create_project("005-later", tracked=True, demo_url="https://example.com/005-later/")
        self.create_project("001-sample", tracked=True)
        published = build_site(self.root)
        self.assertEqual([project["id"] for project in published], ["001", "005"])
        home = (self.root / "site-dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn('./005-later/', home)

    def test_overviews_precede_table_with_safe_links_order_and_legacy_fallback(self):
        overview = '<script>模型 & 工具</script>，我们拟扩展报告。'
        self.create_project("005-later", name="库 B", summary="旧项目摘要")
        self.create_project("001-sample", name="库 A <示例>：详细研究",
                            summary="完整的研究摘要", overview=overview)
        build_site(self.root, projects=["005-later", "001-sample"])
        home = (self.root / "site-dist" / "index.html").read_text(encoding="utf-8")
        before_table, table = home.split('<table class="project-index">', 1)
        self.assertIn('<h2 id="overviews-heading">一句话速览</h2>', before_table)
        self.assertIn('href="./001-sample/">库 A &lt;示例&gt;</a>', before_table)
        self.assertIn(html.escape(overview), before_table)
        self.assertNotIn('<script>', before_table)
        self.assertIn('href="./005-later/">库 B</a>：旧项目摘要', before_table)
        self.assertLess(before_table.index('overview-number">001'),
                        before_table.index('overview-number">005'))
        self.assertNotIn("完整的研究摘要", before_table)
        self.assertIn("完整的研究摘要", table)

    def test_invalid_overviews_preserve_previous_build(self):
        project = self.create_project()
        build_site(self.root, projects=["001-sample"])
        home = self.root / "site-dist" / "index.html"
        original_home = home.read_bytes()
        path = project / "project.json"
        original_metadata = json.loads(path.read_text(encoding="utf-8"))
        for overview in (None, 1, [], {}, "", " \t ", "第一行\n第二行", "第一行\r第二行"):
            with self.subTest(overview=overview):
                path.write_text(json.dumps({**original_metadata, "overview": overview}), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "overview"):
                    build_site(self.root, projects=["001-sample"])
                self.assertEqual(home.read_bytes(), original_home)

    def test_missing_deployed_demo_stops_build_without_replacing_previous_site(self):
        self.create_project(tracked=True)
        build_site(self.root)
        self.create_project("002-deployed", tracked=True, demo_url="https://example.com/002-deployed/")
        (self.root / "projects" / "002-deployed" / "web" / "index.html").unlink()
        with self.assertRaisesRegex(ValueError, "cannot drop a deployed entry"):
            build_site(self.root)
        self.assertTrue((self.root / "site-dist" / "001-sample" / "index.html").is_file())

    def test_tracked_research_without_static_demo_is_not_published(self):
        project = self.create_project(tracked=True)
        (project / "web" / "index.html").unlink()
        published = build_site(self.root)
        self.assertEqual(published, [])
        self.assertTrue((self.root / "site-dist" / ".nojekyll").is_file())
        home = (self.root / "site-dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="overviews-heading"', home)
        self.assertIn('https://github.com/yydshly/1013_codex_project/blob/main/projects/001-sample/README.md', home)
        self.assertNotIn('href="./001-sample/"', home)
        self.assertFalse((self.root / "site-dist" / "001-sample").exists())

    def test_secrets_backends_dependencies_and_documents_are_excluded(self):
        project = self.create_project()
        for relative in (
            ".env", ".env.local", "private/note.txt", "secrets/secret.json", "credentials.json",
            "server/main.js", "backend/settings.json", "node_modules/module/app.js",
            "README.md", "README.txt", "server.py", "key.pem", "key.key", "package.json", "app.js.map",
        ):
            path = project / "web" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("never-publish", encoding="utf-8")
        build_site(self.root, projects=["001-sample"])
        output_files = [path for path in (self.root / "site-dist").rglob("*") if path.is_file()]
        self.assertFalse(any("never-publish" in path.read_text(encoding="utf-8") for path in output_files))
        self.assertFalse((self.root / "site-dist" / "001-sample" / "experiments").exists())
        self.assertFalse((self.root / "site-dist" / "001-sample" / "README.md").exists())

    def test_summary_is_complete_and_escaped_with_relative_urls(self):
        summary = "能力：生成长文。原理：代码安排请求。" * 80 + '<script>alert("x")</script> 价值与输入输出。'
        self.create_project(summary=summary, name='示例 <项目> & "研究"', tags=['输入 <资料>'])
        build_site(self.root, projects=["001-sample"], repository="example/research")
        home = (self.root / "site-dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn(html.escape(summary), home)
        self.assertNotIn('<script>alert("x")</script>', home)
        self.assertIn('./001-sample/', home)
        self.assertIn('<th scope="col">目标源库</th>', home)
        self.assertIn('href="https://github.com/example/upstream">upstream ↗</a>', home)
        self.assertNotIn('<img', home.split('</table>', 1)[0])
        self.assertIn('<img src="./previews/001-sample.svg"', home.split('</table>', 1)[1])
        self.assertTrue((self.root / "site-dist" / "previews" / "001-sample.svg").is_file())
        self.assertIn('https://github.com/example/research/blob/main/projects/001-sample/README.md', home)
        self.assertNotIn('line-clamp', home)
        self.assertEqual((self.root / "site-dist" / "001-sample" / "app.js").read_text(encoding="utf-8"), 'fetch("./data/book.json")')

    def test_structured_summary_has_complete_separate_labels_without_index_images(self):
        sections = [
            {"label": "能力", "text": "长文初稿 <需审核> & 编辑。"},
            {"label": "原理", "text": "代码组织多次请求。"},
            {"label": "边界与验证", "text": "未实测真实 API。" * 100},
        ]
        project = self.create_project(summary_sections=sections)
        # The image appears outside the index table and remains on the project page.
        detail = '<h1>项目详情</h1><img src="./assets/overview.svg" alt="理解总览图">'
        (project / "web" / "index.html").write_text(detail, encoding="utf-8")
        asset = project / "web" / "assets" / "overview.svg"
        asset.parent.mkdir()
        asset.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding="utf-8")
        build_site(self.root, projects=["001-sample"])
        home = (self.root / "site-dist" / "index.html").read_text(encoding="utf-8")
        for section in sections:
            self.assertIn(f'<dt>{html.escape(section["label"])}</dt>', home)
            self.assertIn(f'<dd>{html.escape(section["text"])}</dd>', home)
        self.assertNotIn('<img', home.split('</table>', 1)[0])
        self.assertIn('id="project-guides"', home.split('</table>', 1)[1])
        self.assertIn('id="guide-001"', home)
        self.assertIn('href="#guide-001"', home)
        self.assertIn('<img src="./previews/001-sample.svg"', home.split('</table>', 1)[1])
        self.assertNotIn('preview-caption', home)
        self.assertNotIn('line-clamp', home)
        self.assertNotIn('text-overflow', home)
        self.assertEqual((self.root / "site-dist" / "001-sample" / "index.html").read_text(encoding="utf-8"), detail)
        self.assertTrue((self.root / "site-dist" / "001-sample" / "assets" / "overview.svg").is_file())

    def test_guide_gallery_keeps_caption_escaping_and_skips_placeholder_images(self):
        caption = '源码理解图 <研究绘制> & "非实测"'
        self.create_project(tracked=True, preview_caption=caption)
        self.create_project('002-placeholder', tracked=True, preview_caption='待添加实际截图（占位图）')
        build_site(self.root)
        home = (self.root / 'site-dist' / 'index.html').read_text(encoding='utf-8')
        table, outside = home.split('</table>', 1)
        self.assertNotIn('<img', table)
        self.assertIn('id="guide-001"', outside)
        self.assertNotIn('id="guide-002"', outside)
        self.assertNotIn('href="#guide-002"', table)
        self.assertIn(f'alt="{html.escape(caption, quote=True)}"', outside)
        self.assertIn(f'<figcaption>{html.escape(caption)}</figcaption>', outside)
        self.assertNotIn('<研究绘制>', outside)
        self.assertTrue((self.root / 'site-dist' / 'previews' / '001-sample.svg').is_file())
        self.assertIn('002-placeholder', table)

    def test_invalid_structured_summaries_fail_before_replacing_previous_site(self):
        project = self.create_project()
        build_site(self.root, projects=["001-sample"])
        original_home = (self.root / "site-dist" / "index.html").read_bytes()
        metadata_path = project / "project.json"
        original = json.loads(metadata_path.read_text(encoding="utf-8"))
        for sections in (None, [], {}, [{"label": "能力", "text": ""}],
                         [{"label": "能力\n原理", "text": "内容"}],
                         [{"label": "能力", "text": "一"}, {"label": "能力", "text": "二"}]):
            metadata_path.write_text(json.dumps({**original, "summary_sections": sections}), encoding="utf-8")
            with self.subTest(sections=sections), self.assertRaises(ValueError):
                build_site(self.root, projects=["001-sample"])
            self.assertEqual((self.root / "site-dist" / "index.html").read_bytes(), original_home)

    def test_output_directory_must_be_generated_and_inside_repository(self):
        self.create_project()
        for output in ("../site-outside", ".", "projects", "scripts", "site-dist/child", str(self.root / "site-absolute")):
            with self.subTest(output=output), self.assertRaises(ValueError):
                build_site(self.root, projects=["001-sample"], output=output)
        output = self.root / "site-dist"
        output.mkdir()
        (output / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Refusing to replace"):
            build_site(self.root, projects=["001-sample"])
        self.assertEqual((output / "keep.txt").read_text(encoding="utf-8"), "keep")

    def test_rebuild_replaces_only_own_generated_output(self):
        self.create_project()
        build_site(self.root, projects=["001-sample"])
        (self.root / "site-dist" / "stale.txt").write_text("old", encoding="utf-8")
        build_site(self.root, projects=["001-sample"])
        self.assertFalse((self.root / "site-dist" / "stale.txt").exists())
        self.assertTrue((self.root / "projects" / "001-sample" / "README.md").is_file())

    def test_metadata_directory_preview_and_repository_are_validated(self):
        project = self.create_project()
        with self.assertRaises(ValueError):
            build_site(self.root, projects=["../outside"])
        with self.assertRaises(ValueError):
            build_site(self.root, projects=["001-sample"], repository='example/repo" onclick="x')
        metadata_path = project / "project.json"
        original = json.loads(metadata_path.read_text(encoding="utf-8"))
        for change in (
            {"id": "002"}, {"summary": ""}, {"source_url": "javascript:alert(1)"},
            {"preview": "assets/../../README.md"}, {"preview": "assets/absent.png"},
        ):
            metadata_path.write_text(json.dumps({**original, **change}), encoding="utf-8")
            with self.subTest(change=change), self.assertRaises(ValueError):
                build_site(self.root, projects=["001-sample"])

    def test_symbolic_link_assets_cannot_escape_web_root(self):
        project = self.create_project()
        secret = self.root / "secret.txt"
        secret.write_text("private", encoding="utf-8")
        link = project / "web" / "public.txt"
        try:
            link.symlink_to(secret)
        except OSError:
            self.skipTest("Symbolic links are unavailable for the current Windows user")
        with self.assertRaisesRegex(ValueError, "symbolic links"):
            build_site(self.root, projects=["001-sample"])


if __name__ == "__main__":
    unittest.main()
