"""Gemini boundary for extracting strictly validated candidate activity data."""

import json

from pydantic import ValidationError

from carbonpilot.config import get_settings
from carbonpilot.schemas.activity import ActivityData, Facility


class ProviderUnavailable(RuntimeError):
    pass


class ExtractionRejected(ValueError):
    pass


def extract_candidate_activity(*, document_text: str, filename: str, facility: Facility, reporting_period: str) -> ActivityData:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ProviderUnavailable("GEMINI_API_KEY is required for document extraction")
    prompt = (
        "Extract only evidenced carbon activity data as JSON matching this exact ActivityData schema. "
        "Do not invent emission factors. Every input_reference must use the supplied filename and page. "
        f"Facility is fixed: {facility.model_dump_json()}; reporting_period is fixed: {reporting_period}. "
        f"Filename: {filename}. Document text:\n{document_text}"
    )
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        response = genai.GenerativeModel("gemini-2.5-flash").generate_content(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        payload = json.loads(response.text)
        payload["facility"] = facility.model_dump(mode="json")
        payload["reporting_period"] = reporting_period
        return ActivityData.model_validate(payload)
    except ValidationError as exc:
        raise ExtractionRejected("Gemini output does not satisfy the strict ActivityData schema") from exc
    except (json.JSONDecodeError, AttributeError) as exc:
        raise ExtractionRejected("Gemini did not return structured JSON") from exc
    except ExtractionRejected:
        raise
    except Exception as exc:
        raise ProviderUnavailable("Gemini extraction is unavailable") from exc
