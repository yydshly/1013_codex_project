"""Read public platform metadata only; never fetch textbook files or credentials."""

import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

OUTPUT = Path(__file__).resolve().parent / "results" / "metadata-probe.json"
VERSION_URL = "https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/resources/tch_material/version/data_version.json"
DETAIL_BASE = "https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/details/"


def read_json(url):
    # Only official metadata hosts, never the file/CDN URL returned in a record.
    if urlsplit(url).hostname not in {"s-file-1.ykt.cbern.com.cn", "s-file-2.ykt.cbern.com.cn"}:
        raise ValueError("Metadata probe refuses non-metadata hosts")
    with urlopen(Request(url, headers={"User-Agent": "tchmaterial-research-metadata/1.0"}), timeout=20) as response:
        raw = response.read(20_000_001)
        if len(raw) > 20_000_000:
            raise ValueError("Metadata response exceeds size limit")
        return json.loads(raw), response.status


def main():
    result = {
        "checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "research_ref": "244170e17bf8bc97401f65e04d261533d252572a",
        "environment": {"os": platform.platform(), "python": platform.python_version()},
        "scope": "Public JSON metadata only. No PDFs, audio files, login, or application execution.",
        "requests": [],
    }
    try:
        version, status = read_json(VERSION_URL)
        result["requests"].append({"url": VERSION_URL, "status": status})
        urls = version.get("urls", [])
        urls = [url.strip() for url in urls.split(",") if url.strip()] if isinstance(urls, str) else urls
        result["catalog_parts"] = len(urls)
        sample = None
        for catalog_url in urls[:3]:
            books, status = read_json(catalog_url)
            result["requests"].append({"url": catalog_url, "status": status})
            sample = next((book for book in books if any(
                tag.get("tag_name") == "小学" for tag in book.get("tag_list", [])
            )), None)
            if sample:
                break
        if sample is None:
            result["outcome"] = "No elementary sample found in the first three catalog parts; coverage unverified."
        else:
            detail_url = DETAIL_BASE + sample["id"] + ".json"
            data, status = read_json(detail_url)
            result["requests"].append({"url": detail_url, "status": status})
            result["sample"] = {
                "id": data.get("id", sample["id"]),
                "title": data.get("title", sample.get("title")),
                "tags": [tag.get("tag_name") for tag in data.get("tag_list", [])],
                "files": [{
                    "flag": item.get("ti_file_flag"),
                    "format": item.get("ti_format"),
                    "has_storage": bool(item.get("ti_storage") or item.get("ti_storages")),
                } for item in data.get("ti_items", [])],
                "limitations": "One public elementary metadata record; does not prove download access, file integrity, current school edition, or platform-wide coverage.",
            }
            result["outcome"] = "Public catalog and one elementary resource metadata record returned successfully."
    except Exception as error:
        result["outcome"] = "Metadata probe incomplete"
        result["error"] = str(error)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["outcome"])
    if result.get("sample"):
        print(result["sample"]["title"])
    return 1 if "error" in result else 0


if __name__ == "__main__":
    sys.exit(main())
