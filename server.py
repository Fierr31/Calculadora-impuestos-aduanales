from dotenv import load_dotenv
load_dotenv()

from backend.sugerencias import autocompletado
from backend.consulta import obtener
from backend.calculadora import basegravable
from backend.agente import chat_con_agente
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Annotated

import os

app = FastAPI()

# Permitir peticiones desde frontend
# En producción (Railway) se permite el dominio asignado
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("templates/index.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

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

@app.post("/calcular")
def calcular(datos: DatosEntrada):
    calculos = basegravable(datos)
    return calculos


# ── Chatbot ──────────────────────────────────────────────────────────
class ChatInput(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=2000)

@app.post("/chat")
async def chat(data: ChatInput):
    try:
        respuesta = await chat_con_agente(data.mensaje)
        return {"respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del agente: {str(e)}")