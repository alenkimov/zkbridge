import json
from typing import Any


def to_json(obj: Any) -> str:
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)