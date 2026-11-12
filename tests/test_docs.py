import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "gen_rules_docs", ROOT / "scripts/gen_rules_docs.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_pages(directory: Path) -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(directory.glob("*.md"))}


def test_rule_pages_are_up_to_date(tmp_path):
    load_generator().render_all(tmp_path)
    assert read_pages(tmp_path) == read_pages(
        ROOT / "docs" / "rules"
    ), "docs/rules is stale: run `python scripts/gen_rules_docs.py` and commit the result"


def test_generation_is_idempotent(tmp_path):
    generator = load_generator()
    generator.render_all(tmp_path)
    first = read_pages(tmp_path)
    generator.render_all(tmp_path)
    assert read_pages(tmp_path) == first
