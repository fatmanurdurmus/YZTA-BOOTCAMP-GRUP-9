from carbonpilot.schemas.activity import (
    ElectricityActivity,
    FuelActivity,
    ProcessActivity,
    PurchasedInputActivity,
    TransportActivity,
)


def demo_steel_activities() -> dict[str, list[object]]:
    return {
        "fuels": [
            FuelActivity(
                activity_name="Natural gas reheating furnace",
                fuel_type="natural_gas",
                amount=1000.0,
                unit="Nm3",
                emission_factor_kg_co2e_per_unit=2.0,
                factor_source="Demo national inventory placeholder",
                input_reference="ERP-FUEL-001",
            )
        ],
        "processes": [
            ProcessActivity(
                activity_name="Electric arc furnace process emissions",
                process_type="eaf_process",
                output_tonnes=10.0,
                emission_factor_tco2e_per_tonne=1.8,
                factor_source="Demo CBAM default placeholder",
                input_reference="PROD-BATCH-001",
            )
        ],
        "electricity": [
            ElectricityActivity(
                activity_name="Grid electricity for melt shop",
                electricity_mwh=50.0,
                emission_factor_tco2e_per_mwh=0.4,
                factor_source="Demo grid factor placeholder",
                input_reference="UTILITY-INV-001",
            )
        ],
        "purchased_inputs": [
            PurchasedInputActivity(
                activity_name="Purchased steel scrap",
                material_name="steel_scrap",
                cn_code="7204",
                mass_tonnes=25.0,
                emission_factor_tco2e_per_tonne=0.2,
                factor_source="Supplier declaration placeholder",
                input_reference="SUPPLIER-INV-001",
                supplier_name="Demo Scrap Supplier",
            )
        ],
        "transport": [
            TransportActivity(
                activity_name="Road delivery of scrap",
                mode="road",
                mass_tonnes=25.0,
                distance_km=100.0,
                emission_factor_kg_co2e_per_tonne_km=0.1,
                factor_source="Demo freight factor placeholder",
                input_reference="CMR-001",
            )
        ],
    }
