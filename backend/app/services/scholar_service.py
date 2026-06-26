"""Scholar profiles — aggregate authors from knowledge base and pipeline opinions."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.response import Response
from backend.app.repositories.source_repository import SourceRepository
from backend.app.schemas.scholar_schemas import (
    ScholarListItemSchema,
    ScholarListResponse,
    ScholarOpinionSampleSchema,
    ScholarProfileSchema,
    ScholarSourceSchema,
)
from backend.app.utils.slugify import slugify

SEED_SCHOLARS: list[dict[str, object]] = [
    {
        "name": "AAOIFI Shariah Board",
        "name_ar": "هيئة المعايير الشرعية لـ AAOIFI",
        "name_en": "AAOIFI Shariah Board",
        "institution": "Accounting and Auditing Organization for Islamic Financial Institutions",
        "bio": "Sets global Shariah standards for Islamic banks, sukuk, and equity screening.",
        "bio_ar": "تضع معايير شرعية عالمية للمصارف الإسلامية والصكوك وفحص الأسهم.",
        "expertise": ["AAOIFI", "stocks", "sukuk", "banking"],
    },
    {
        "name": "International Islamic Fiqh Academy",
        "name_ar": "مجمع الفقه الإسلامي الدولي",
        "name_en": "International Islamic Fiqh Academy",
        "institution": "OIC International Islamic Fiqh Academy",
        "bio": "Resolves contemporary fiqh issues including modern finance and digital assets.",
        "bio_ar": "يعالج قضايا فقهية معاصرة تشمل التمويل الحديث والأصول الرقمية.",
        "expertise": ["fiqh", "contemporary fatwa", "international"],
    },
    {
        "name": "Sheikh Muhammad Taqi Usmani",
        "name_ar": "الشيخ محمد تقي عثماني",
        "name_en": "Sheikh Muhammad Taqi Usmani",
        "institution": "Darul Uloom Karachi",
        "bio": "Leading Hanafi scholar with extensive writings on Islamic finance and muamalat.",
        "bio_ar": "عالم حنفي بارز بمؤلفات واسعة في التمويل الإسلامي والمعاملات.",
        "expertise": ["Hanafi", "banking", "stocks", "murabaha"],
    },
    {
        "name": "Sheikh Yusuf al-Qaradawi",
        "name_ar": "الشيخ يوسف القرضاوي",
        "name_en": "Sheikh Yusuf al-Qaradawi",
        "institution": "European Council for Fatwa and Research",
        "bio": "Influential contemporary scholar on zakat, stocks, and modern economic issues.",
        "bio_ar": "عالم معاصر مؤثر في الزكاة والأسهم والقضايا الاقتصادية الحديثة.",
        "expertise": ["contemporary fatwa", "zakat", "stocks"],
    },
    {
        "name": "Sheikh Abdul Sattar Abu Ghuddah",
        "name_ar": "الشيخ عبد الستار أبو غدة",
        "name_en": "Sheikh Abdul Sattar Abu Ghuddah",
        "institution": "AAOIFI / Islamic Fiqh Academy",
        "bio": "Specialist in Islamic commercial law and Shariah governance for financial institutions.",
        "bio_ar": "متخصص في القانون التجاري الإسلامي والحوكمة الشرعية للمؤسسات المالية.",
        "expertise": ["AAOIFI", "commercial law", "standards"],
    },
]


class ScholarService:
    """Build scholar directory from seed data, sources, and stored opinions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.source_repo = SourceRepository(session)

    async def list_scholars(self, *, query: str | None = None, limit: int = 50) -> ScholarListResponse:
        """Return merged seed + source-author scholar directory."""
        sources = await self.source_repo.list_filtered(is_authenticated=True, limit=200)
        by_slug: dict[str, ScholarListItemSchema] = {}

        for seed in SEED_SCHOLARS:
            name = str(seed["name"])
            item_slug = slugify(name)
            by_slug[item_slug] = ScholarListItemSchema(
                slug=item_slug,
                name=name,
                name_ar=str(seed["name_ar"]) if seed.get("name_ar") else None,
                name_en=str(seed["name_en"]) if seed.get("name_en") else name,
                institution=str(seed.get("institution") or ""),
                expertise=list(seed.get("expertise") or []),
                source_count=0,
                is_seed=True,
            )

        for source in sources:
            author = source.author.strip()
            if not author or len(author) < 2:
                continue
            item_slug = slugify(author)
            existing = by_slug.get(item_slug)
            if existing:
                existing.source_count += 1
                continue
            by_slug[item_slug] = ScholarListItemSchema(
                slug=item_slug,
                name=author,
                institution=source.title[:80] if source.source_type.value == "fatwa" else None,
                expertise=[source.source_type.value],
                source_count=1,
                is_seed=False,
            )

        items = sorted(by_slug.values(), key=lambda s: (-s.source_count, s.name.lower()))
        if query:
            needle = query.strip().lower()
            items = [
                item
                for item in items
                if needle in item.name.lower()
                or (item.name_ar and needle in item.name_ar.lower())
                or (item.name_en and needle in item.name_en.lower())
                or (item.institution and needle in item.institution.lower())
                or any(needle in tag.lower() for tag in item.expertise)
            ]

        trimmed = items[:limit]
        return ScholarListResponse(items=trimmed, total=len(items))

    async def get_scholar(self, slug: str) -> ScholarProfileSchema | None:
        """Return a scholar profile with related sources and opinion samples."""
        listing = await self.list_scholars(limit=200)
        match = next((item for item in listing.items if item.slug == slug), None)
        if match is None:
            return None

        seed = next((s for s in SEED_SCHOLARS if slugify(str(s["name"])) == slug), None)
        bio = str(seed["bio"]) if seed and seed.get("bio") else None
        bio_ar = str(seed["bio_ar"]) if seed and seed.get("bio_ar") else None
        institution = match.institution
        expertise = list(match.expertise)

        if seed:
            institution = str(seed.get("institution") or institution)
            expertise = list(seed.get("expertise") or expertise)

        sources = await self.source_repo.list_filtered(is_authenticated=True, limit=200)
        related: list[ScholarSourceSchema] = []
        name_lower = match.name.lower()
        for source in sources:
            if name_lower not in source.author.lower() and source.author.lower() not in name_lower:
                continue
            related.append(
                ScholarSourceSchema(
                    id=str(source.id),
                    title=source.title,
                    source_type=source.source_type.value,
                    citation_hint=source.author,
                )
            )

        opinion_samples = await self._opinion_samples_for(name_lower, limit=6)

        return ScholarProfileSchema(
            slug=slug,
            name=match.name,
            name_ar=match.name_ar,
            name_en=match.name_en,
            institution=institution,
            bio=bio,
            bio_ar=bio_ar,
            expertise=expertise,
            source_count=max(match.source_count, len(related)),
            sources=related[:12],
            opinion_samples=opinion_samples,
        )

    async def _opinion_samples_for(self, name_lower: str, *, limit: int) -> list[ScholarOpinionSampleSchema]:
        """Extract recent pipeline opinions mentioning this scholar."""
        stmt = select(Response).order_by(Response.created_at.desc()).limit(80)
        result = await self.session.execute(stmt)
        responses = list(result.scalars().all())

        samples: list[ScholarOpinionSampleSchema] = []
        for response in responses:
            for opinion in response.opinions or []:
                if not isinstance(opinion, dict):
                    continue
                scholar = str(opinion.get("scholar") or "")
                if name_lower not in scholar.lower() and scholar.lower() not in name_lower:
                    continue
                samples.append(
                    ScholarOpinionSampleSchema(
                        position=str(opinion.get("position") or "")[:480],
                        question_context=response.summary[:160] if response.summary else None,
                        date=str(opinion.get("date")) if opinion.get("date") else None,
                        citations=[str(c) for c in opinion.get("citations") or []][:5],
                    )
                )
                if len(samples) >= limit:
                    return samples
        return samples
