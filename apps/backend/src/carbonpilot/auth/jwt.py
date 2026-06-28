from datetime import datetime, timedelta, timezone


def build_demo_token_payload(user_id: str, organization_id: str) -> dict[str, object]:
    now = datetime.now(timezone.utc)
    return {
        "sub": user_id,
        "organization_id": organization_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=8)).timestamp()),
    }
