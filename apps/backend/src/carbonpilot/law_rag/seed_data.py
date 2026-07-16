"""Curated CBAM/SKDM knowledge base chunks used to seed `law_chunks`.

All chunk_text values are original paraphrased summaries written for this
project, not verbatim excerpts from official regulations, to keep the
knowledge base copyright-safe while still capturing the operative content
CarbonPilot's agents need to reference.
"""

CBAM_LAW_CHUNKS: list[dict[str, str]] = [
    {
        "title": "CBAM Scope and Covered Sectors",
        "jurisdiction": "EU",
        "source_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "chunk_text": (
            "The Carbon Border Adjustment Mechanism applies to imports of iron and steel, "
            "aluminium, cement, fertilisers, hydrogen, and electricity into the EU. Importers "
            "of these goods must account for the embedded greenhouse gas emissions of the "
            "production process, covering both direct and, for some sectors, indirect emissions."
        ),
    },
    {
        "title": "CBAM Transitional Reporting Period",
        "jurisdiction": "EU",
        "source_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "chunk_text": (
            "During the CBAM transitional period, importers must submit quarterly reports "
            "declaring embedded emissions of covered goods without paying a financial "
            "adjustment. Reports must distinguish direct emissions from production and, where "
            "applicable, indirect emissions from electricity consumption."
        ),
    },
    {
        "title": "CBAM Definitive Regime Financial Adjustment",
        "jurisdiction": "EU",
        "source_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "chunk_text": (
            "Under the definitive CBAM regime, importers must purchase CBAM certificates "
            "corresponding to the embedded emissions of imported goods, priced against the "
            "weekly average auction price of EU Emissions Trading System allowances, with "
            "credit given for any carbon price already paid in the country of origin."
        ),
    },
    {
        "title": "Use of Default Emission Values",
        "jurisdiction": "EU",
        "source_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "chunk_text": (
            "Where an importer cannot obtain verified installation-specific emissions data "
            "from a non-EU producer, CBAM allows the use of default values based on the "
            "average emission intensity of the exporting country, or, absent reliable country "
            "data, the average of the worst-performing EU installations for that product."
        ),
    },
    {
        "title": "Verification and Accreditation Requirements",
        "jurisdiction": "EU",
        "source_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "chunk_text": (
            "Embedded emissions data reported under CBAM must be verified by an accredited "
            "verifier once the definitive regime applies. Verification follows principles "
            "consistent with the EU Emissions Trading System's monitoring and reporting rules."
        ),
    },
    {
        "title": "GHG Protocol Scope 1, 2, and 3 Classification",
        "jurisdiction": "Global",
        "source_url": "https://ghgprotocol.org/corporate-standard",
        "chunk_text": (
            "The GHG Protocol Corporate Standard classifies emissions into Scope 1 (direct "
            "emissions from owned or controlled sources), Scope 2 (indirect emissions from "
            "purchased electricity, steam, heating, or cooling), and Scope 3 (all other "
            "indirect emissions occurring in a company's value chain, including purchased "
            "goods, transport, and distribution)."
        ),
    },
    {
        "title": "Embedded Emissions Calculation Boundary",
        "jurisdiction": "EU",
        "source_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "chunk_text": (
            "Embedded emissions calculations for CBAM goods must include direct process "
            "emissions from the production route, relevant precursor materials consumed in "
            "production, and, for specified goods, indirect emissions from electricity used "
            "during manufacturing."
        ),
    },
    {
        "title": "National Competent Authority Registration",
        "jurisdiction": "EU",
        "source_url": "https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en",
        "chunk_text": (
            "Importers of CBAM goods must register as authorised CBAM declarants with the "
            "competent authority of their EU member state before importing covered goods "
            "under the definitive regime, and maintain records supporting their emissions "
            "declarations for review."
        ),
    },
]