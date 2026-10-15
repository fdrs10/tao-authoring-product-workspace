"""Pydantic request models — Phase 3 API.

PATCH bodies distinguish "field not sent" from "explicitly sent as null"
via ``model_dump(exclude_unset=True)``; explicit null clears a nullable
field (e.g. Roadmap Admission back to UNSET), omission leaves it intact.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

ADMISSION = ("COMMITTED", "CANDIDATE", "BACKLOG", "DEFERRED", "NOT PLANNED")
MOSCOW = ("Must", "Should", "Could", "Won't")
STRATEGIC_CATEGORIES = (
    "Create & Design",
    "Manage & Govern",
    "Collaborate & Assure Quality",
    "Standards & Portability",
    "AI-assisted Authoring",
)


def _enum_ok(value: str | None, allowed: tuple[str, ...]) -> bool:
    return value is None or value in allowed


class CapabilityPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    working_name: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    strategic_category: str | None = None
    moscow: str | None = None
    visibility: str | None = None
    scope: str | None = None
    origin: str | None = None
    owner: str | None = None
    decision: str | None = None
    v2_mapping: str | None = None
    ideation_sheet: str | None = None
    roadmap_admission: str | None = None
    analysis_budget_hours: float | None = Field(default=None, ge=0)
    execution_budget_hours: float | None = Field(default=None, ge=0)
    notes: str | None = None
    review_status: str | None = None
    markets: list[str] | None = None  # market names; full replacement set

    def validate_enums(self) -> list[str]:
        errs = []
        if not _enum_ok(self.roadmap_admission, ADMISSION):
            errs.append(f"roadmap_admission must be one of {ADMISSION} or null")
        if not _enum_ok(self.moscow, MOSCOW):
            errs.append(f"moscow must be one of {MOSCOW} or null")
        if not _enum_ok(self.strategic_category, STRATEGIC_CATEGORIES):
            errs.append("strategic_category must be one of the five canonical categories")
        return errs


class JiraLinkCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jira_key: str = Field(min_length=1, max_length=40)
    relationship: str | None = "DELIVERY_EVIDENCE"
    note: str | None = None


class RoadmapTimingPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    start_month: int = Field(ge=0)
    duration_months: int = Field(ge=1)


class MilestoneCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    milestone_id: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=200)
    milestone_date: date | None = None
    scope_type: str | None = None
    scope_ref: str | None = None
    description: str | None = None
    position_month: int | None = Field(default=None, ge=0)


class MilestonePatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    milestone_date: date | None = None
    scope_type: str | None = None
    scope_ref: str | None = None
    description: str | None = None
    position_month: int | None = Field(default=None, ge=0)


class CustomerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1, max_length=60)
    name: str = Field(min_length=1, max_length=200)
    current_use: str | None = None
    min_functionality_today: str | None = None
    min_functionality_studio: str | None = None
    desired_outcome: str | None = None
    value_opportunity: str | None = None
    blockers: str | None = None
    earliest_milestone_interval: str | None = None
    validation_status: str | None = None
    notes: str | None = None


class CustomerPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    current_use: str | None = None
    min_functionality_today: str | None = None
    min_functionality_studio: str | None = None
    desired_outcome: str | None = None
    value_opportunity: str | None = None
    blockers: str | None = None
    earliest_milestone_interval: str | None = None
    validation_status: str | None = None
    notes: str | None = None
