"""Scholar profile schemas."""

from pydantic import BaseModel, Field


class ScholarListItemSchema(BaseModel):
    slug: str
    name: str
    name_ar: str | None = None
    name_en: str | None = None
    institution: str | None = None
    expertise: list[str] = Field(default_factory=list)
    source_count: int = 0
    is_seed: bool = False


class ScholarSourceSchema(BaseModel):
    id: str
    title: str
    source_type: str
    citation_hint: str | None = None


class ScholarOpinionSampleSchema(BaseModel):
    position: str
    question_context: str | None = None
    date: str | None = None
    citations: list[str] = Field(default_factory=list)


class ScholarProfileSchema(BaseModel):
    slug: str
    name: str
    name_ar: str | None = None
    name_en: str | None = None
    institution: str | None = None
    bio: str | None = None
    bio_ar: str | None = None
    expertise: list[str] = Field(default_factory=list)
    source_count: int = 0
    sources: list[ScholarSourceSchema] = Field(default_factory=list)
    opinion_samples: list[ScholarOpinionSampleSchema] = Field(default_factory=list)


class ScholarListResponse(BaseModel):
    items: list[ScholarListItemSchema]
    total: int
