from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"


@dataclass(frozen=True)
class Settings:
    app_name: str = "Iapetus Shelf-Life Risk Engine"
    app_version: str = "0.1.0"
    debug: bool = False

    root_dir: Path = ROOT_DIR
    backend_dir: Path = BACKEND_DIR
    data_path: Path = ROOT_DIR / "data" / "raw" / "synthetic_food_micro_challenge_train_100k.csv"
    processed_data_dir: Path = ROOT_DIR / "data" / "processed"
    reports_dir: Path = ROOT_DIR / "reports"
    artifacts_dir: Path = BACKEND_DIR / "artifacts"

    threshold_cfu_g: int = 100
    threshold_log_cfu_g: float = 2.0
    default_simulations: int = 500
    default_day_grid: list[int] = field(default_factory=lambda: [0, 1, 3, 5, 7, 10, 14, 21, 28, 35, 42])
    monte_carlo_seed: int = 42
    dataset_version: str = "food_micro_challenge_v1"

    ollama_enabled: bool = False
    ollama_model: str = "qwen2.5:7b"
    ollama_url: str = "http://localhost:11434/api/generate"


@lru_cache
def get_settings() -> Settings:
    return Settings()
