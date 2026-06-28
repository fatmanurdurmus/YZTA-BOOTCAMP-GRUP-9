from carbonpilot.schemas.law import LawReference


def retrieve_default_references() -> list[LawReference]:
    return [
        LawReference(
            title="European Commission Carbon Border Adjustment Mechanism",
            jurisdiction="EU",
            url="https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
            relevance="CBAM scope, transition to definitive regime, reporting context.",
            source_type="official_guidance",
        ),
        LawReference(
            title="GHG Protocol Corporate Standard",
            jurisdiction="Global",
            url="https://ghgprotocol.org/corporate-standard",
            relevance="Scope 1, Scope 2, and Scope 3 accounting concepts.",
            source_type="standard",
        ),
    ]
