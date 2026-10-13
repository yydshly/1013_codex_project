"""Exercise project creation, index ordering and invalid metadata in isolated folders."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from new_project import create_project
from project_index import (
    END, START, load_projects, render_index, replace_index, source_repository_name,
    update_readme, validate_summary_sections,
)


class ProjectToolsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="research-index-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "projects").mkdir()
        shutil.copytree(ROOT / "templates", self.root / "templates")
        self.readme = f"# Test index\n\n{START}\nstale content\n{END}\n\nKeep this footer.\n"
        (self.root / "README.md").write_text(self.readme, encoding="utf-8")

    def create(self, slug="sample-project", name="示例研究", summary="源码分析与运行复现"):
        return create_project(
            slug, name, "https://github.com/example/source", summary, root=self.root
        )

    def modify_metadata(self, directory, **changes):
        path = directory / "project.json"
        metadata = json.loads(path.read_text(encoding="utf-8"))
        metadata.update(changes)
        path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")

    def test_empty_index_ignores_templates_and_preserves_other_content(self):
        self.assertEqual(load_projects(self.root), [])
        self.assertFalse(update_readme(self.root, check=True))
        self.assertEqual((self.root / "README.md").read_text(encoding="utf-8"), self.readme)
        update_readme(self.root)
        result = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("**0**", result)
        self.assertTrue(result.startswith("# Test index\n\n"))
        self.assertTrue(result.endswith("\n\nKeep this footer.\n"))
        self.assertTrue(update_readme(self.root, check=True))

    def test_create_copies_complete_template_and_updates_index(self):
        target = self.create(name='名称含 "引号"', summary="摘要含 | 表格符号")
        self.assertEqual(target.name, "001-sample-project")
        for path in ("README.md", "project.json", "assets/cover.svg", "web/README.md", "experiments/README.md"):
            self.assertTrue((target / path).is_file())
        metadata = load_projects(self.root)[0]
        self.assertEqual(metadata["name"], '名称含 "引号"')
        self.assertNotIn("{{", (target / "README.md").read_text(encoding="utf-8"))
        index = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("<img", index)
        self.assertNotIn("图片预览", index)
        self.assertIn("| 目标源库 |", index)
        self.assertIn("[source](https://github.com/example/source)<br>example", index)
        self.assertIn("摘要含 \\| 表格符号", index)
        self.assertIn("演示未部署", index)
        self.assertTrue(update_readme(self.root, check=True))

    def test_next_id_and_index_follow_number_order_not_name(self):
        self.create("z-first")
        self.create("a-second")
        self.assertEqual([item["id"] for item in load_projects(self.root)], ["001", "002"])
        rendered = render_index(load_projects(self.root))
        self.assertLess(rendered.index("z-first"), rendered.index("a-second"))

    def test_duplicate_slug_is_rejected_without_changing_index(self):
        self.create()
        original = (self.root / "README.md").read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.create()
        self.assertEqual(len(load_projects(self.root)), 1)
        self.assertEqual((self.root / "README.md").read_text(encoding="utf-8"), original)

    def test_invalid_creation_input_leaves_registry_empty(self):
        with self.assertRaises(ValueError):
            self.create("../outside")
        with self.assertRaises(ValueError):
            self.create(name="")
        with self.assertRaises(ValueError):
            create_project("sample", "Sample", "javascript:alert(1)", "Summary", root=self.root)
        self.assertEqual(load_projects(self.root), [])

    def test_bad_readme_markers_prevent_project_creation(self):
        (self.root / "README.md").write_text("No markers", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "markers"):
            self.create()
        self.assertEqual(load_projects(self.root), [])
        with self.assertRaises(ValueError):
            replace_index(f"{END}\n{START}", "test")

    def test_changed_metadata_makes_check_fail_until_regenerated(self):
        target = self.create()
        self.modify_metadata(target, status="reproduced", demo_url="https://example.com/demo/")
        self.assertFalse(update_readme(self.root, check=True))
        update_readme(self.root)
        index = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertIn("已复现", index)
        self.assertIn("[在线演示](https://example.com/demo/)", index)
        self.assertTrue(update_readme(self.root, check=True))

    def test_metadata_must_match_directory(self):
        target = self.create()
        self.modify_metadata(target, id="002")
        with self.assertRaisesRegex(ValueError, "does not match"):
            load_projects(self.root)

    def test_preview_must_exist_inside_assets(self):
        target = self.create()
        for preview in ("assets/missing.png", "assets/../../README.md", "../outside.png"):
            with self.subTest(preview=preview):
                self.modify_metadata(target, preview=preview)
                with self.assertRaises(ValueError):
                    load_projects(self.root)

    def test_invalid_status_url_and_tags_are_rejected(self):
        target = self.create()
        metadata_path = target / "project.json"
        original = metadata_path.read_text(encoding="utf-8")
        for change in (
            {"status": "unknown"}, {"demo_url": "javascript:alert(1)"},
            {"tags": "AI"}, {"source_url": "https://example.com/source"},
        ):
            with self.subTest(change=change):
                metadata_path.write_text(original, encoding="utf-8")
                self.modify_metadata(target, **change)
                with self.assertRaises(ValueError):
                    load_projects(self.root)

    def test_optional_sections_preserve_legacy_summary_and_render_labeled_lines(self):
        target = self.create(summary="保留原始摘要作为兼容字段")
        sections = [
            {"label": "能力", "text": "输入主题，生成长文初稿。"},
            {"label": "原理", "text": "先生成目录，再分节生成正文。"},
            {"label": "价值", "text": "复用流程，减少重复操作与整理。"},
        ]
        self.modify_metadata(target, summary_sections=sections)
        project = load_projects(self.root)[0]
        self.assertEqual(project["summary"], "保留原始摘要作为兼容字段")
        self.assertEqual(project["summary_sections"], sections)
        rendered = render_index([project])
        self.assertIn(
            "**能力：** 输入主题，生成长文初稿。<br>"
            "**原理：** 先生成目录，再分节生成正文。<br>"
            "**价值：** 复用流程，减少重复操作与整理。", rendered,
        )
        self.assertNotIn("<img", rendered)
        self.assertFalse(update_readme(self.root, check=True))
        update_readme(self.root)
        self.assertTrue(update_readme(self.root, check=True))

    def test_optional_sections_escape_markdown_and_html_without_truncation(self):
        target = self.create()
        long_text = "完整内容 " * 100
        self.modify_metadata(target, summary_sections=[
            {"label": "能力|边界", "text": "<script> *不是链接* [示例] " + long_text},
        ])
        rendered = render_index(load_projects(self.root))
        self.assertIn("**能力\\|边界：**", rendered)
        self.assertIn("&lt;script&gt; \\*不是链接\\* \\[示例\\]", rendered)
        self.assertIn(long_text, rendered)
        self.assertNotIn("<script>", rendered)

    def test_missing_optional_sections_are_backward_compatible(self):
        self.assertEqual(validate_summary_sections({}, "001-example"), [])
        self.create(summary="已有项目完整单段摘要")
        project = load_projects(self.root)[0]
        self.assertNotIn("summary_sections", project)
        self.assertIn("已有项目完整单段摘要", render_index([project]))

    def test_invalid_summary_sections_are_rejected(self):
        target = self.create()
        metadata_path = target / "project.json"
        original = metadata_path.read_text(encoding="utf-8")
        invalid_sections = (
            None, "能力", {}, [], ["能力"], [{}],
            [{"label": "", "text": "说明"}],
            [{"label": " \t ", "text": "说明"}],
            [{"label": "能力\n原理", "text": "说明"}],
            [{"label": 1, "text": "说明"}],
            [{"label": "能力"}],
            [{"label": "能力", "text": ""}],
            [{"label": "能力", "text": " \t "}],
            [{"label": "能力", "text": "第一行\r第二行"}],
            [{"label": "能力", "text": 1}],
            [{"label": "能力", "text": "一"}, {"label": "能力", "text": "二"}],
            [{"label": "能力", "text": "一"}, {"label": " 能力 ", "text": "二"}],
        )
        for sections in invalid_sections:
            with self.subTest(sections=sections):
                metadata_path.write_text(original, encoding="utf-8")
                self.modify_metadata(target, summary_sections=sections)
                with self.assertRaisesRegex(ValueError, "summary[_ ]section"):
                    load_projects(self.root)

    def test_repository_name_handles_optional_trailing_slash(self):
        for url in (
            "https://github.com/Bklieger/infinite-bookshelf",
            "https://github.com/Bklieger/infinite-bookshelf/",
        ):
            self.assertEqual(source_repository_name(url), "infinite-bookshelf")


if __name__ == "__main__":
    unittest.main()
