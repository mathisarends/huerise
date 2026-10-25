import json
from pathlib import Path
from typing import Any

from huerise.app import app

OUTPUT = Path(__file__).resolve().parent.parent / "specs" / "openapi.json"


def codegen_schema(value: Any) -> Any:
    if isinstance(value, list):
        return [codegen_schema(item) for item in value]
    if not isinstance(value, dict):
        return value
    schema = {key: codegen_schema(item) for key, item in value.items()}
    # ogen accepts enum/anyOf, but not OpenAPI 3.1's const or type arrays.
    if "const" in schema:
        schema["enum"] = [schema.pop("const")]
    if isinstance(schema.get("type"), list):
        variants = [{"type": item} for item in schema.pop("type")]
        if "anyOf" in schema:
            schema.setdefault("allOf", []).append({"anyOf": variants})
        else:
            schema["anyOf"] = variants
    return schema


def main() -> None:
    OUTPUT.write_text(
        json.dumps(codegen_schema(app.openapi()), indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
