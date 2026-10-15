"""Check project coverage, handoff references and generated diagram consistency."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from project_index import markdown_text
from research_workflow import DATA_PATH, DIAGRAM_PATH, load_workflow, render_html, render_markdown, render_svg, update_diagram


class ResearchWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="research-workflow-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.data = json.loads((ROOT / DATA_PATH).read_text(encoding="utf-8"))
        self.projects = [{"id": item, "name": "项目 " + item + "：研究", "directory": item + "-sample"}
                         for item in ("001", "002", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014", "015", "016")]
        self.write_data(self.data)

    def write_data(self, data):
        path = self.root / DATA_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_all_fifteen_projects_have_one_group_and_diagram_node(self):
        data = load_workflow(self.root, self.projects)
        ids = [member["id"] for group in data["groups"] for member in group["members"]]
        self.assertEqual(len(data["groups"]), 6)
        self.assertEqual(len(ids), 15)
        self.assertEqual(set(ids), {project["id"] for project in self.projects})
        svg = ET.fromstring(render_svg(data))
        diagram_ids = [node.attrib["data-project-id"] for node in svg.iter() if "data-project-id" in node.attrib]
        self.assertEqual(sorted(diagram_ids), sorted(ids))

    def test_missing_or_duplicate_projects_and_invalid_handoff_are_rejected(self):
        invalid = copy.deepcopy(self.data)
        invalid["groups"][1]["members"][0]["id"] = "012"
        self.write_data(invalid)
        with self.assertRaisesRegex(ValueError, "unique"):
            load_workflow(self.root, self.projects)
        self.write_data(self.data)
        with self.assertRaisesRegex(ValueError, "missing projects"):
            load_workflow(self.root, self.projects[1:])
        invalid = copy.deepcopy(self.data)
        invalid["combinations"][0]["roles"][0]["id"] = "999"
        self.write_data(invalid)
        with self.assertRaisesRegex(ValueError, "unknown project"):
            load_workflow(self.root, self.projects)

    def test_partial_preview_and_new_project_remain_supported(self):
        self.assertIsNone(load_workflow(self.root, self.projects[:1], allow_partial=True))
        extra = {"id": "017", "name": "新项目", "directory": "017-new"}
        data = load_workflow(self.root, self.projects + [extra])
        self.assertEqual(data["groups"][-1]["key"], "pending")
        self.assertEqual(data["groups"][-1]["members"][0]["id"], "017")

    def test_text_is_escaped_and_research_only_project_uses_document_link(self):
        data = load_workflow(self.root, self.projects)
        data["groups"][0]["purpose"] = "<script>资料 & 来源</script>"
        demos = {project["directory"] for project in self.projects if project["id"] != "004"}
        rendered = render_html(data, self.projects, demos, "example/research")
        self.assertIn("&lt;script&gt;资料 &amp; 来源&lt;/script&gt;", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn('href="https://github.com/example/research/blob/main/projects/004-sample/README.md"', rendered)
        self.assertNotIn('href="./004-sample/"', rendered)
        self.assertIn("需要补齐：", rendered)
        self.assertEqual(rendered.count('class="workflow-case"'), 6)
        markdown = render_markdown(data, self.projects, markdown_text)
        self.assertIn("&lt;script&gt;资料 &amp; 来源&lt;/script&gt;", markdown)
        self.assertIn("职责互补不表示已有现成连接", markdown)

    def test_check_detects_stale_diagram_without_writing(self):
        data = load_workflow(self.root, self.projects)
        self.assertFalse(update_diagram(self.root, data, check=True))
        self.assertFalse((self.root / DIAGRAM_PATH).exists())
        self.assertTrue(update_diagram(self.root, data))
        self.assertTrue(update_diagram(self.root, data, check=True))
        previous = (self.root / DIAGRAM_PATH).read_bytes()
        data["groups"][0]["members"][0]["diagram_role"] = "增加新的资料入口"
        self.assertFalse(update_diagram(self.root, data, check=True))
        self.assertEqual((self.root / DIAGRAM_PATH).read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
