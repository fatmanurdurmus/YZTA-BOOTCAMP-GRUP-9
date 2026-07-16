import uuid

from sqlalchemy.orm import Session

from carbonpilot.db import models
from carbonpilot.schemas.activity import ActivityData
from carbonpilot.schemas.calculation import CalculationResponse


def get_or_create_organization(db: Session, name: str) -> models.Organization:
    organization = db.query(models.Organization).filter_by(name=name).one_or_none()
    if organization is None:
        organization = models.Organization(id=uuid.uuid4(), name=name)
        db.add(organization)
        db.flush()
    return organization


def get_or_create_facility(
    db: Session,
    organization: models.Organization,
    name: str,
    country_code: str,
    sector: str = "steel",
) -> models.Facility:
    facility = (
        db.query(models.Facility)
        .filter_by(organization_id=organization.id, name=name)
        .one_or_none()
    )
    if facility is None:
        facility = models.Facility(
            id=uuid.uuid4(),
            organization_id=organization.id,
            name=name,
            country_code=country_code,
            sector=sector,
        )
        db.add(facility)
        db.flush()
    return facility


def persist_activity_records(
    db: Session, facility: models.Facility, activity_data: ActivityData
) -> list[models.ActivityRecord]:
    """Stores every individual activity line (fuel, electricity, process,
    purchased input, transport) as its own row, with the original payload
    kept in `raw_payload` for audit purposes.
    """
    records: list[models.ActivityRecord] = []

    activity_groups = [
        ("fuel", activity_data.fuels),
        ("process", activity_data.processes),
        ("electricity", activity_data.electricity),
        ("purchased_input", activity_data.purchased_inputs),
        ("transport", activity_data.transport),
    ]

    for activity_type, items in activity_groups:
        for item in items:
            amount = (
                getattr(item, "amount", None)
                or getattr(item, "mass_tonnes", None)
                or getattr(item, "electricity_mwh", None)
                or getattr(item, "output_tonnes", None)
            )
            record = models.ActivityRecord(
                id=uuid.uuid4(),
                facility_id=facility.id,
                activity_type=activity_type,
                activity_name=item.activity_name,
                reporting_period=activity_data.reporting_period,
                amount=amount,
                unit=getattr(item, "unit", None),
                input_reference=item.input_reference,
                raw_payload=item.model_dump(mode="json"),
            )
            db.add(record)
            records.append(record)

    return records


def persist_calculation_run(
    db: Session,
    activity_data: ActivityData,
    thread_id: str,
    status: str,
    critic_passed: bool,
    calculation: CalculationResponse | None = None,
) -> models.CalculationRun:
    """Persists a single agent run: resolves/creates the organization and
    facility, stores each activity line, then stores the calculation run
    outcome for audit purposes. Committing here is intentional — each run
    is its own unit of work.
    """
    organization = get_or_create_organization(db, activity_data.facility.organization_name)
    facility = get_or_create_facility(
        db,
        organization,
        activity_data.facility.facility_name,
        activity_data.facility.country_code,
    )

    persist_activity_records(db, facility, activity_data)

    run = models.CalculationRun(
        id=uuid.uuid4(),
        facility_id=facility.id,
        thread_id=thread_id,
        status=status,
        total_tco2e=calculation.total_tco2e if calculation is not None else None,
        critic_passed=critic_passed,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

def get_episodic_history(
    db: Session, organization_name: str, facility_name: str, limit: int = 5
) -> list[models.CalculationRun]:
    """CP-36: episodic memory — returns the most recent calculation runs for
    a given organization/facility, most recent first. This lets the agent
    (or any caller) see what happened in past runs for this facility before
    reacting to the current one, e.g. "the last 3 runs all failed the
    critic for the same reason".
    """
    return (
        db.query(models.CalculationRun)
        .join(models.Facility, models.CalculationRun.facility_id == models.Facility.id)
        .join(models.Organization, models.Facility.organization_id == models.Organization.id)
        .filter(
            models.Organization.name == organization_name,
            models.Facility.name == facility_name,
        )
        .order_by(models.CalculationRun.requested_at.desc())
        .limit(limit)
        .all()
    )