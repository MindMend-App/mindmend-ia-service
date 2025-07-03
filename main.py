from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from deep_translator import GoogleTranslator

# Traducción
translator = GoogleTranslator(source='es', target='en')
translator_back = GoogleTranslator(source='en', target='es')

# Pipelines en inglés
chatbot = pipeline(
    "text2text-generation",
    model="facebook/blenderbot-400M-distill"
)
emotion = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)

app = FastAPI(
    title="MindMend IA Service",
    description="Microservicio con traducción y conversación enfocada en ansiedad",
    version="0.1.0"
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class AnalyzeRequest(BaseModel):
    messages: list[str]

class AnalyzeResponse(BaseModel):
    label: str
    score: float

SYSTEM_PROMPT = (
    "You are a compassionate mental health assistant. "
    "Your goal is to have a natural conversation and ask questions "
    "that help determine if the user is experiencing anxiety. "
    "Keep your tone friendly and empathetic."
)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Si no hay mensaje del usuario, el bot debe iniciar la charla:
    if not req.message.strip():
        # Directamente formulamos la primera pregunta en español:
        first_q = (
            "¡Hola! Soy MindMend, tu asistente de apoyo emocional. "
            "¿Cómo te sientes hoy? ¿Hay algo que te esté preocupando últimamente?"
        )
        return ChatResponse(reply=first_q)

    # 1) Traducimos ES→EN
    en_input = translator.translate(req.message)

    # 2) Construimos el prompt completo en inglés:
    prompt = (
        SYSTEM_PROMPT
        + "\nUser: " + en_input
        + "\nAssistant:"
    )

    # 3) Generamos la respuesta en inglés
    en_reply = chatbot(prompt, max_length=150, do_sample=True, temperature=0.7)[0]["generated_text"]

    # 4) Traducimos EN→ES
    es_reply = translator_back.translate(en_reply)

    return ChatResponse(reply=es_reply)

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    full_es = " ".join(req.messages)
    full_en = translator.translate(full_es)
    res = emotion(full_en)[0]
    label_es = translator_back.translate(res["label"])
    return AnalyzeResponse(label=label_es, score=float(res["score"]))
