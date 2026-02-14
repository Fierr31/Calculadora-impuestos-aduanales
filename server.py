from backend.sugerencias import autocompletado
from backend.consulta import obtener
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir peticiones desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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
    #try:
    lit = obtener(id)
    return lit
    #except ValueError as e:
    #    raise HTTPException(status_code=400, detail=str(e))
    