import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import CHAR, Boolean, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    facilities: Mapped[list["Facility"]] = relationship(back_populates="organization")


class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    country_code: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    sector: Mapped[str] = mapped_column(Text, nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="facilities")
    documents: Mapped[list["Document"]] = relationship(back_populates="facility")
    activity_records: Mapped[list["ActivityRecord"]] = relationship(back_populates="facility")
    calculation_runs: Mapped[list["CalculationRun"]] = relationship(back_populates="facility")


class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    factor_value: Mapped[float] = mapped_column(Numeric, nullable=False)
    source_name: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    quality: Mapped[str] = mapped_column(Text, nullable=False)


class LawChunk(Base):
    __tablename__ = "law_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    facility: Mapped["Facility"] = relationship(back_populates="documents")
    activity_records: Mapped[list["ActivityRecord"]] = relationship(back_populates="document")


class ActivityRecord(Base):
    __tablename__ = "activity_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    activity_type: Mapped[str] = mapped_column(Text, nullable=False)
    activity_name: Mapped[str] = mapped_column(Text, nullable=False)
    reporting_period: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    emission_factor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("emission_factors.id"), nullable=True
    )
    input_reference: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    facility: Mapped["Facility"] = relationship(back_populates="activity_records")
    document: Mapped["Document | None"] = relationship(back_populates="activity_records")


class CalculationRun(Base):
    __tablename__ = "calculation_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    thread_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    total_tco2e: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    critic_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    facility: Mapped["Facility"] = relationship(back_populates="calculation_runs")
    reports: Mapped[list["Report"]] = relationship(back_populates="calculation_run")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("calculation_runs.id"), nullable=False
    )
    format: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    calculation_run: Mapped["CalculationRun"] = relationship(back_populates="reports")