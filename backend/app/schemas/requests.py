from pydantic import BaseModel, Field, field_validator


class ScenarioRequest(BaseModel):
    product_category: str = Field(..., examples=["deli_salad"])
    intended_use: str = Field(default="ready_to_eat")
    pathogen: str = Field(default="Listeria monocytogenes")
    ph: float = Field(..., ge=3.0, le=7.2)
    aw: float = Field(..., ge=0.85, le=0.999)
    salt_percent: float = Field(..., ge=0.0, le=10.0)
    sugar_percent: float = Field(..., ge=0.0, le=20.0)
    fat_percent: float = Field(..., ge=0.0, le=60.0)
    preservative_flag: bool
    preservative_type: str
    acidulant_type: str
    packaging_type: str
    oxygen_condition: str
    storage_temperature_c: float = Field(..., ge=-2.0, le=30.0)
    inoculation_type: str
    initial_inoculum_log_cfu_g: float = Field(..., ge=0.0, le=4.0)
    target_shelf_life_days: int = Field(..., ge=1, le=90)
    study_type: str = Field(default="challenge_test")
    test_purpose: str = Field(default="shelf_life_validation")
    strain_info: str = Field(default="2-strain cocktail")
    temperature_profile_type: str = Field(default="constant")

    @field_validator("preservative_type")
    @classmethod
    def normalize_preservative_type(cls, value: str, info):
        if info.data.get("preservative_flag") is False and value.strip() == "":
            return "none"
        return value
