# CBAM/SKDM Methodology

## Methodology Principle

CarbonPilot AI separates evidence, factors, formulas, and agent reasoning. The platform can use AI to extract candidate values and retrieve references, but final emissions are calculated by deterministic Python functions.

## Scope 1

Direct emissions include fuel combustion and process emissions at the facility.

Formula:

```text
emissions_tco2e = activity_amount * emission_factor
```

Fuel activities may use kg CO2e per unit, which is converted into tonnes CO2e.

## Scope 2

Electricity emissions are calculated from purchased electricity and grid or supplier-specific emission factors.

Formula:

```text
emissions_tco2e = electricity_mwh * factor_tco2e_per_mwh
```

## CBAM-Focused Scope 3

For the demir-celik MVP, Scope 3 focuses on:

- purchased metallic and process inputs;
- supplier-specific or default input factors;
- upstream transport by tonne-kilometer factors.

Formula for purchased inputs:

```text
emissions_tco2e = mass_tonnes * factor_tco2e_per_tonne
```

Formula for transport:

```text
emissions_tco2e = mass_tonnes * distance_km * factor_kgco2e_per_tonne_km / 1000
```

## Audit Evidence

Each output line must include:

- scope;
- category;
- activity name;
- input reference;
- factor source;
- formula;
- calculated tCO2e.

## Compliance Caveat

This project is a bootcamp MVP and not legal advice. Production use requires expert validation of factors, legal interpretations, and report templates.
