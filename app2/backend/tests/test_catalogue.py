import json
from pathlib import Path
import subprocess

from app.rules import OBJECTS, OBJECT_NAMES, ENCHANTMENTS, ENCHANTMENT_NAMES, INCOMPATIBLE


def test_frontend_and_backend_options_match():
    frontend = Path(__file__).resolve().parents[2] / "frontend"
    script = "import {objects,enchantments,incompatible} from './src/data.js'; console.log(JSON.stringify({objects,enchantments,incompatible}))"
    data = json.loads(subprocess.check_output(["node", "--input-type=module", "-e", script], cwd=frontend))
    assert {o["id"]: o["type"] for o in data["objects"]} == OBJECTS
    assert {o["id"]: o["name"] for o in data["objects"]} == OBJECT_NAMES
    assert {e["id"]: (e["max"], set(e["types"])) for e in data["enchantments"]} == ENCHANTMENTS
    assert {e["id"]: e["name"] for e in data["enchantments"]} == ENCHANTMENT_NAMES
    assert {frozenset(group) for group in data["incompatible"]} == {frozenset(group) for group in INCOMPATIBLE}
