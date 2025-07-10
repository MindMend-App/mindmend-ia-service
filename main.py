from fastapi import FastAPI
from pydantic import BaseModel, Field
import os
from deep_translator import GoogleTranslator
from huggingface_hub import InferenceClient

client = InferenceClient(token=os.environ["HF_TOKEN"])
def chat_with_hf(prompt: str) -> str:
    resp = client.text_generation(
        model="facebook/blenderbot-400M-distill",
        inputs=prompt,
        parameters={"max_new_tokens": 150, "temperature": 0.7}
    )
    return resp.generated_text

# Traducción
translator = GoogleTranslator(source='es', target='en')
translator_back = GoogleTranslator(source='en', target='es')

# En lugar de pipeline, reutiliza el mismo InferenceClient:
def detect_anxiety(text: str) -> float:
    # zero-shot classification via inference API
    resp = client.zero_shot_classification(
      model="facebook/bart-large-mnli",
      inputs=text,
      parameters={
        "candidate_labels": ["anxiety"],
        "multi_label": False
      }
    )
    # resp["scores"] y resp["labels"]
    idx = resp["labels"].index("anxiety")
    return float(resp["scores"][idx])

app = FastAPI(
    title="MindMend IA Service",
    description="Microservicio con traducción y conversación enfocada en ansiedad",
    version="0.1.0"
)

class ChatRequest(BaseModel):
    message: str
    history: list[str] = Field(
        default_factory=list,
        description="Todos los mensajes (del bot y del usuario) hasta ahora, en orden"
    )

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

@app.get("/", tags=["health"])
def healthcheck():
    return {"status":"ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # 1) Si no hay historial, devolvemos sólo el saludo inicial (en español)
    if not req.history:
        greeting = (
            "¡Hola! Soy MindMend, tu asistente de apoyo emocional. "
            "¿Cómo te sientes hoy? ¿Hay algo que te esté preocupando últimamente?"
        )
        return ChatResponse(reply=greeting)

    # 2) Traducimos ES → EN
    en_input = translator.translate(req.message)

    # 3) Reconstruimos la conversación en inglés:
    #    turnamos cada elemento de history (en español) a inglés
    history_en = [translator.translate(msg) for msg in req.history]
    convo_en = "\n".join(
        f"{'User' if i % 2 else 'Assistant'}: {txt}"
        for i, txt in enumerate(history_en)
    )

    # 4) Montamos el prompt completo
    prompt = "\n".join([
        SYSTEM_PROMPT,
        convo_en,
        f"User: {en_input}",
        "Assistant:"
    ])

    # 5) Generamos la respuesta en inglés vía HF Inference API
    en_reply = chat_with_hf(prompt)

    # 6) Traducimos EN → ES y devolvemos
    es_reply = translator_back.translate(en_reply)
    return ChatResponse(reply=es_reply)

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    full_es = " ".join(req.messages)
    full_en = translator.translate(full_es)
    score = detect_anxiety(full_en)
    return AnalyzeResponse(label="ansiedad", score=score)