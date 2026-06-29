from fastapi import APIRouter
from app.schemas.chatbot import ChatbotRequest, ChatbotResponse
from app.services.chatbot import query_chatbot

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/query", response_model=ChatbotResponse)
def chatbot_query(req: ChatbotRequest):
    return query_chatbot(req.query)
