from backend.sugerencias import autocompletado
from backend.consulta import obtener
from backend.calculadora import basegravable
from backend.chat_agent import AduanalChatAgent
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated, Optional

app = FastAPI()
chat_agent: Optional[AduanalChatAgent] = None


def get_chat_agent() -> AduanalChatAgent:
    global chat_agent
    if chat_agent is None:
        chat_agent = AduanalChatAgent()
    return chat_agent

# Permitir peticiones desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/autocomplete")
def autocomplete(q: str = Query(..., min_length=1, max_length=50)):
    try:
        q = q.strip()

        if not q:
            return {"resultados": []}
        resultados = autocompletado(q)
        return {"resultados": resultados}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/producto/{id}")
def consulta(id: int):
    try:
        lit = obtener(id)
        return lit
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class DatosEntrada(BaseModel):
    precio: float = Field(..., ge=0, le=1_000_000)
    cantidad: int = Field(..., ge=0, le=1_000_000)
    pais: Annotated[str, Field(min_length=1, strip_whitespace=True)]
    flete: float = Field(..., ge=0, le=1_000_000)
    seguro: float = Field(..., ge=0, le=1_000_000)
    impuesto: str
    fracc: str

class ChatRequest(BaseModel):
    message: Annotated[str, Field(min_length=1, max_length=4000, strip_whitespace=True)]

@app.post("/calcular")
def calcular(datos: DatosEntrada):
    calculos = basegravable(datos)
    return calculos

@app.post("/chat")
def chat(payload: ChatRequest):
    try:
        result = get_chat_agent().run(payload.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo generar respuesta: {str(e)}")
