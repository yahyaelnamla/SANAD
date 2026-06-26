"""Tools API — Fanar STT, translation, and utility endpoints."""

import logging
import uuid

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel, Field

from agents.common.fanar_client import FanarLLMClient, detect_speech_language, prepare_text_for_speech
from backend.app.api.deps import CurrentUser, DbSession
from backend.app.exceptions import ValidationError
from backend.app.schemas.feature_schemas import (
    CompanyScanRequest,
    CompanyScanResponse,
    DocumentAnalysisResponse,
    DocumentCompareRequest,
    DocumentCompareResponse,
    DocumentListResponse,
    PortfolioScanRequest,
    PortfolioScanResponse,
    ZakatAssetsRequest,
    ZakatCalculationResponse,
)
from backend.app.services.document_service import (
    analyze_and_store_pdf,
    compare_user_documents,
    delete_user_document,
    list_user_documents,
)
from backend.app.services.scanner_service import scan_company, scan_portfolio
from backend.app.services.zakat_service import calculate_zakat, fetch_zakat_prices

router = APIRouter(prefix="/tools", tags=["Tools"])
logger = logging.getLogger(__name__)


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    target_language: str = Field(default="en", pattern="^(ar|en|fr|ur|tr|ms)$")
    source_language: str | None = Field(
        default=None,
        pattern="^(ar|en|fr|ur|tr|ms)$",
    )


class TranslateResponse(BaseModel):
    translated_text: str
    model: str


class TranscribeResponse(BaseModel):
    text: str
    model: str


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    language: str = Field(default="ar", pattern="^(ar|en)$")
    voice: str | None = Field(default=None, max_length=64)


class TTSResponse(BaseModel):
    model: str
    voice: str


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    user: CurrentUser,
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> TranscribeResponse:
    """Transcribe voice input using Fanar-Aura-STT."""
    _ = user
    if not file.content_type or not file.content_type.startswith("audio"):
        raise ValidationError("Upload must be an audio file.")

    audio_bytes = await file.read()
    if len(audio_bytes) < 100:
        raise ValidationError("Audio file is too short.")

    client = FanarLLMClient()
    text = await client.transcribe_audio(
        audio_bytes,
        filename=file.filename or "recording.webm",
        language=language,
    )
    from config.fanar_api_keys import FANAR_MODELS

    return TranscribeResponse(text=text, model=FANAR_MODELS["stt"])


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(
    request: TranslateRequest,
    user: CurrentUser,
) -> TranslateResponse:
    """Translate text using Fanar-Shaheen (with chat fallback for long / multi-lang text)."""
    _ = user
    from backend.app.services.translation_service import detect_language, translate_long_text

    client = FanarLLMClient(timeout=180.0)
    source = request.source_language or detect_language(request.text)
    translated = await translate_long_text(
        client,
        request.text,
        target_language=request.target_language,
        source_language=source,
    )
    from config.fanar_api_keys import FANAR_MODELS

    return TranslateResponse(translated_text=translated, model=FANAR_MODELS["translation"])


@router.post("/tts")
async def synthesize_speech(
    request: TTSRequest,
    user: CurrentUser,
):
    """Synthesize speech using Fanar-Aura-TTS-2."""
    from fastapi.responses import Response

    _ = user
    client = FanarLLMClient()
    from config.fanar_api_keys import FANAR_MODELS

    prepared = prepare_text_for_speech(request.text)
    speech_lang = detect_speech_language(prepared, request.language)
    voice = request.voice or ("Abdulrahman" if speech_lang == "ar" else "Amelia")
    audio = await client.synthesize_speech(
        prepared,
        language=speech_lang,
        voice=voice,
    )
    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={"X-SANAD-TTS-Model": FANAR_MODELS["tts"], "X-SANAD-TTS-Voice": voice},
    )


@router.post("/zakat/calculate", response_model=ZakatCalculationResponse)
async def calculate_zakat_endpoint(
    request: ZakatAssetsRequest,
    user: CurrentUser,
) -> ZakatCalculationResponse:
    """Calculate Zakat on cash, gold, stocks, crypto, and debts with live prices."""
    _ = user
    return await calculate_zakat(request)


class ZakatPricesRequest(BaseModel):
    output_currency: str = Field(default="USD", max_length=3)
    gold_currency: str = Field(default="USD", max_length=3)
    stock_symbols: list[str] = Field(default_factory=list)
    crypto_symbols: list[str] = Field(default_factory=list)


@router.post("/zakat/prices")
async def zakat_prices_endpoint(
    request: ZakatPricesRequest,
    user: CurrentUser,
) -> dict:
    """Fetch live gold, stock, crypto, and FX prices for the Zakat calculator."""
    _ = user
    return await fetch_zakat_prices(
        output_currency=request.output_currency,
        gold_currency=request.gold_currency,
        stock_symbols=request.stock_symbols,
        crypto_symbols=request.crypto_symbols,
    )


@router.post("/scanner/company", response_model=CompanyScanResponse)
async def scan_company_endpoint(
    request: CompanyScanRequest,
    user: CurrentUser,
) -> CompanyScanResponse:
    """Screen a company for Shariah compliance indicators."""
    _ = user
    try:
        return await scan_company(request)
    except Exception as exc:
        logger.exception("Company scan failed for %s: %s", request.company_name, exc)
        raise


@router.post("/scanner/portfolio", response_model=PortfolioScanResponse)
async def scan_portfolio_endpoint(
    request: PortfolioScanRequest,
    user: CurrentUser,
) -> PortfolioScanResponse:
    """Analyze a portfolio for halal compliance and purification."""
    _ = user
    return await scan_portfolio(request)


@router.post("/documents/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    user: CurrentUser,
    session: DbSession,
    file: UploadFile = File(...),
    language: str | None = Form(default="en"),
) -> DocumentAnalysisResponse:
    """Analyze an uploaded PDF for Shariah finance signals (Fanar-Oryx-IVU path ready)."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise ValidationError("Upload must be a PDF file.")
    if file.content_type and file.content_type not in {
        "application/pdf",
        "application/x-pdf",
        "application/octet-stream",
    }:
        raise ValidationError("Upload must be a PDF file.")

    content = await file.read()
    client = FanarLLMClient()
    return await analyze_and_store_pdf(
        session,
        user.id,
        content,
        file.filename,
        language=language or "en",
        fanar_client=client,
    )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    user: CurrentUser,
    session: DbSession,
) -> DocumentListResponse:
    """List persisted user documents for document memory."""
    return await list_user_documents(session, user.id)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    user: CurrentUser,
    session: DbSession,
) -> None:
    """Permanently delete a saved user document."""
    await delete_user_document(session, user.id, document_id)


@router.post("/documents/compare", response_model=DocumentCompareResponse)
async def compare_documents(
    request: DocumentCompareRequest,
    user: CurrentUser,
    session: DbSession,
) -> DocumentCompareResponse:
    """Compare two to four saved PDF analyses side-by-side."""
    return await compare_user_documents(session, user.id, request.document_ids)


@router.post("/documents/query")
async def query_from_document(
    user: CurrentUser,
    session: DbSession,
    file: UploadFile = File(...),
    language: str = Form(default="ar"),
):
    """Extract document text via Fanar-Oryx-IVU and run the full reasoning pipeline."""
    from datetime import UTC, datetime

    from backend.app.agents.agent_orchestrator import AgentOrchestrator
    from backend.app.models.enums import QueryStatus
    from backend.app.schemas.query_schemas import QueryResultSchema
    from backend.app.services.query_service import QueryService

    if not file.filename:
        raise ValidationError("Filename is required.")

    content = await file.read()
    if len(content) < 100:
        raise ValidationError("Document is too small.")

    orchestrator = AgentOrchestrator(session)
    try:
        final = await orchestrator.process_document_query(
            content,
            file.filename,
            language=language or "ar",
            user_id=user.id,
        )
    finally:
        await orchestrator.close()

    service = QueryService(session)
    return QueryResultSchema(
        query_id=uuid.uuid4(),
        status=QueryStatus.COMPLETED if not final.refused else QueryStatus.FAILED,
        question=file.filename,
        language=final.language,
        created_at=datetime.now(UTC),
        **service._schema_from_final(final),
    )
