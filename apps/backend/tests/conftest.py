import pytest

from carbonpilot.schemas.activity import (
    ActivityData,
    ElectricityActivity,
    Facility,
    FuelActivity,
    ProcessActivity,
    PurchasedInputActivity,
    TransportActivity,
)
from carbonpilot.schemas.calculation import CalculationRequest


@pytest.fixture
def build_demo_calculation_request() -> CalculationRequest:
    return CalculationRequest(
        carbon_price_eur_per_tonne=80.0,
        activity_data=ActivityData(
            facility=Facility(
                organization_name="Demo Steel Exporter",
                facility_name="Izmir Steel Plant",
                country_code="TR",
            ),
            reporting_period="2026-Q1",
            fuels=[
                FuelActivity(
                    activity_name="Natural gas reheating furnace",
                    fuel_type="natural_gas",
                    amount=1000.0,
                    unit="Nm3",
                    emission_factor_kg_co2e_per_unit=2.0,
                    factor_source="Test factor",
                    input_reference="ERP-FUEL-001",
                )
            ],
            processes=[
                ProcessActivity(
                    activity_name="EAF process emissions",
                    process_type="eaf",
                    output_tonnes=10.0,
                    emission_factor_tco2e_per_tonne=1.8,
                    factor_source="Test process factor",
                    input_reference="PROD-001",
                )
            ],
            electricity=[
                ElectricityActivity(
                    activity_name="Grid electricity",
                    electricity_mwh=50.0,
                    emission_factor_tco2e_per_mwh=0.4,
                    factor_source="Test grid factor",
                    input_reference="UTILITY-001",
                )
            ],
            purchased_inputs=[
                PurchasedInputActivity(
                    activity_name="Purchased steel scrap",
                    material_name="steel_scrap",
                    cn_code="7204",
                    mass_tonnes=25.0,
                    emission_factor_tco2e_per_tonne=0.2,
                    factor_source="Supplier factor",
                    input_reference="SUPPLIER-001",
                )
            ],
            transport=[
                TransportActivity(
                    activity_name="Road delivery of scrap",
                    mode="road",
                    mass_tonnes=25.0,
                    distance_km=100.0,
                    emission_factor_kg_co2e_per_tonne_km=0.1,
                    factor_source="Freight factor",
                    input_reference="CMR-001",
                )
            ],
        ),
    )
