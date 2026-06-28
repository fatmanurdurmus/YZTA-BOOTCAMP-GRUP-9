from typing import Literal

from pydantic import Field, model_validator

from carbonpilot.schemas.common import FactorQuality, StrictBaseModel


class Facility(StrictBaseModel):
    organization_name: str = Field(min_length=2)
    facility_name: str = Field(min_length=2)
    country_code: str = Field(min_length=2, max_length=2, examples=["TR"])
    sector: Literal["iron_steel", "cement", "aluminum", "fertilizer", "chemicals"] = "iron_steel"


class FuelActivity(StrictBaseModel):
    activity_name: str = Field(min_length=2)
    fuel_type: str = Field(min_length=2)
    amount: float = Field(ge=0)
    unit: Literal["Nm3", "kg", "tonne", "liter", "mwh"]
    emission_factor_kg_co2e_per_unit: float = Field(ge=0)
    factor_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)
    factor_quality: FactorQuality = "national_default"


class ProcessActivity(StrictBaseModel):
    activity_name: str = Field(min_length=2)
    process_type: str = Field(min_length=2)
    output_tonnes: float = Field(ge=0)
    emission_factor_tco2e_per_tonne: float = Field(ge=0)
    factor_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)
    factor_quality: FactorQuality = "cbam_default"


class ElectricityActivity(StrictBaseModel):
    activity_name: str = Field(min_length=2)
    electricity_mwh: float = Field(ge=0)
    emission_factor_tco2e_per_mwh: float = Field(ge=0)
    factor_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)
    market_based: bool = False
    factor_quality: FactorQuality = "national_default"


class PurchasedInputActivity(StrictBaseModel):
    activity_name: str = Field(min_length=2)
    material_name: str = Field(min_length=2)
    cn_code: str = Field(min_length=2)
    mass_tonnes: float = Field(ge=0)
    emission_factor_tco2e_per_tonne: float = Field(ge=0)
    factor_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)
    supplier_name: str | None = None
    factor_quality: FactorQuality = "supplier_specific"


class TransportActivity(StrictBaseModel):
    activity_name: str = Field(min_length=2)
    mode: Literal["road", "rail", "sea", "air"]
    mass_tonnes: float = Field(ge=0)
    distance_km: float = Field(ge=0)
    emission_factor_kg_co2e_per_tonne_km: float = Field(ge=0)
    factor_source: str = Field(min_length=2)
    input_reference: str = Field(min_length=2)
    factor_quality: FactorQuality = "national_default"


class ActivityData(StrictBaseModel):
    facility: Facility
    reporting_period: str = Field(pattern=r"^\d{4}-(Q[1-4]|M(0[1-9]|1[0-2]))$")
    fuels: list[FuelActivity] = Field(default_factory=list)
    processes: list[ProcessActivity] = Field(default_factory=list)
    electricity: list[ElectricityActivity] = Field(default_factory=list)
    purchased_inputs: list[PurchasedInputActivity] = Field(default_factory=list)
    transport: list[TransportActivity] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_at_least_one_activity(self) -> "ActivityData":
        if not any(
            [
                self.fuels,
                self.processes,
                self.electricity,
                self.purchased_inputs,
                self.transport,
            ]
        ):
            raise ValueError("At least one activity record is required.")
        return self
