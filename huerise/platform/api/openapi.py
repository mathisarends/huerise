from typing import Any


def include_request_validation(document: dict[str, Any]) -> None:
    validation_ref = "#/components/schemas/RequestValidationProblem"
    validation_schema = {"$ref": validation_ref}
    for path in document["paths"].values():
        for operation in path.values():
            if not isinstance(operation, dict):
                continue
            if not (operation.get("requestBody") or operation.get("parameters")):
                continue
            response = operation.get("responses", {}).get("422")
            if response is None:
                continue
            content = response.get("content", {}).get("application/problem+json")
            if content is None:
                continue
            schema = content["schema"]
            if schema == validation_schema:
                continue
            variants = schema.get("oneOf", [schema])
            if validation_schema in variants:
                continue
            variants = [*variants, validation_schema]
            mapping = {
                document["components"]["schemas"][item["$ref"].rsplit("/", 1)[1]][
                    "properties"
                ]["code"]["const"]: item["$ref"]
                for item in variants
            }
            # Canon 0.7 preserves explicit 422 responses without adding validation.
            content["schema"] = {
                "oneOf": variants,
                "discriminator": {"propertyName": "code", "mapping": mapping},
            }
            response["description"] += " Request validation failed."
