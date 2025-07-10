from fastapi import FastAPI
from pydantic import BaseModel, Field
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

# Clasificador zero-shot para “anxiety”
anxiety_detector = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

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

    # 5) Generamos la respuesta en inglés
    en_reply = chatbot(
        prompt,
        truncation=True,        # <— trunca el prompt a max_input_length del tokenizer
        max_length=128,         # <— tope para la tokenización
        max_new_tokens=150,     # <— longitud de la respuesta generada
        do_sample=True,
        temperature=0.7
    )[0]["generated_text"]

    # 6) Traducimos EN → ES y devolvemos
    es_reply = translator_back.translate(en_reply)
    return ChatResponse(reply=es_reply)

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    # 1) Unimos toda la conversación
    full_es = " ".join(req.messages)
    # 2) Traducimos ES→EN
    full_en = translator.translate(full_es)

    # 3) Clasificamos con zero-shot para “anxiety”
    res = anxiety_detector(full_en,
                            candidate_labels=["anxiety"],
                            multi_label=False)

    # 4) Devolvemos la puntuación (score) de “anxiety”
    return AnalyzeResponse(
        label="ansiedad",
        score=float(res["scores"][res["labels"].index("anxiety")])
    )