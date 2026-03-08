import json

from app.services.model_registry import load_model_bundle


def main() -> None:
    for model_name in ("regressor", "classifier"):
        _, metadata = load_model_bundle(model_name)
        print(model_name.upper())
        print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
