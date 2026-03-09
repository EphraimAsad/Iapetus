from dataclasses import dataclass, field
from functools import lru_cache
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = ROOT_DIR / "backend"


@dataclass(frozen=True)
class Settings:
    app_name: str = "Iapetus Shelf-Life Risk Engine"
    app_version: str = "0.2.0"
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
    sensitivity_simulations: int = field(default_factory=lambda: int(os.getenv("SENSITIVITY_SIMULATIONS", "60")))
    default_day_grid: list[int] = field(default_factory=lambda: [0, 1, 3, 5, 7, 10, 14, 21, 28, 35, 42])
    monte_carlo_seed: int = 42
    dataset_version: str = "food_micro_challenge_v1"

    summary_provider: str = field(default_factory=lambda: os.getenv("SUMMARY_PROVIDER", "ollama"))
    ollama_enabled: bool = field(default_factory=lambda: os.getenv("OLLAMA_ENABLED", "true").lower() == "true")
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "qwen3.5:4b"))
    ollama_timeout_seconds: float = field(default_factory=lambda: float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "8")))

    kinetic_curve_default_mode: str = field(default_factory=lambda: os.getenv("IAPETUS_CURVE_MODE", "both"))
    ratkowsky_b: float = field(default_factory=lambda: float(os.getenv("RATKOWSKY_B", "0.02")))
    ratkowsky_tmin_c: float = field(default_factory=lambda: float(os.getenv("RATKOWSKY_TMIN_C", "-1.5")))


@lru_cache
def get_settings() -> Settings:
    return Settings()
