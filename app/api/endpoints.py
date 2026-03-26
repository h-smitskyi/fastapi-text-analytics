"""
API router — ``/api/v1`` endpoints.

Thin controller layer that validates input via Pydantic, delegates to the
service layer, and returns a typed response.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import TextAnalysisRequest, TextAnalysisResponse
from app.services.analyzer import analyze_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Text Analysis"])


@router.post(
    "/analyze-text",
    response_model=TextAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse a body of text",
    description=(
        "Accepts a raw text payload and returns word frequencies, "
        "Top-N keywords (stop words excluded), and basic text metrics."
    ),
)
async def analyze_text_endpoint(payload: TextAnalysisRequest) -> TextAnalysisResponse:
    """Handle ``POST /api/v1/analyze-text``.

    Pydantic validates the request body automatically.  Remaining edge-
    cases (e.g. text that is effectively empty after stripping) are
    caught here and returned as 422 responses.
    """
    stripped = payload.text.strip()
    if not stripped:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text field must contain at least one non-whitespace character.",
        )

    logger.info(
        "analyze-text called | chars=%d top_n=%d",
        len(stripped),
        payload.top_n,
    )

    try:
        result = await analyze_text(stripped, payload.top_n)
    except Exception as exc:  # pragma: no cover — defensive
        logger.exception("Unexpected error during text analysis")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing the text.",
        ) from exc

    return result
