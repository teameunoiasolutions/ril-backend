import asyncio

from fastapi import APIRouter

from app.schemas.chat_schema import ChatRequest

from app.services.gemini_service import ask_gemini

from app.services.image_service import fetch_image_url

from app.services.prompt_builder import (
    build_personalized_prompt,
    build_general_prompt,
    parse_concierge_response,  # add this to app/services/prompt_builder.py
)

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):

    if request.isPersonalized:

        prompt = build_personalized_prompt(
            request.message,
            request.mood,
            request.identity
        )

    else:

        prompt = build_general_prompt(
            request.message
        )

    raw_response = ask_gemini(prompt)

    parsed = parse_concierge_response(raw_response)

    recommendations = parsed["recommendations"]

    image_urls = await asyncio.gather(*[
        fetch_image_url(
            rec.get("image_query"),
            fallback_query=f"{rec.get('name', '')} {rec.get('region', '')} Sri Lanka",
        )
        for rec in recommendations
    ])

    for rec, image_url in zip(recommendations, image_urls):
        rec["image"] = image_url

    return {
        "success": True,
        "narrative": parsed["narrative"],
        "tailoredNote": parsed["tailored_note"],
        "recommendations": recommendations,
        "followUpQuestion": parsed["follow_up_question"],
    }