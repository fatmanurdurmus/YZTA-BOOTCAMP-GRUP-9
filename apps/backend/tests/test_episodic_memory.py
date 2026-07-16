from carbonpilot.db import models
from carbonpilot.db.repository import get_episodic_history, persist_calculation_run


def test_episodic_history_returns_most_recent_runs_first(
    build_demo_calculation_request, require_database
):
    """
    CP-36: inserts three calculation runs for the same facility and checks
    that `get_episodic_history` returns them most-recent-first, respecting
    `limit`. Cleans up its own rows afterwards regardless of outcome so
    repeated test runs never accumulate junk data in `calculation_runs`.
    """
    db = require_database
    calculation_request = build_demo_calculation_request
    activity_data = calculation_request.activity_data

    try:
        for i in range(3):
            persist_calculation_run(
                db=db,
                activity_data=activity_data,
                thread_id=f"thread-episodic-test-{i}",
                status="completed",
                critic_passed=True,
            )

        history = get_episodic_history(
            db,
            activity_data.facility.organization_name,
            activity_data.facility.facility_name,
            limit=2,
        )

        assert len(history) == 2
        assert history[0].thread_id == "thread-episodic-test-2"
        assert history[1].thread_id == "thread-episodic-test-1"
    finally:
        db.query(models.CalculationRun).filter(
            models.CalculationRun.thread_id.like("thread-episodic-test-%")
        ).delete(synchronize_session=False)
        db.commit()