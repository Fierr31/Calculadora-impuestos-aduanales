from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

_engine = None

def _get_engine():
    global _engine
    if _engine is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL no está configurada")
        _engine = create_engine(db_url)
    return _engine

def autocompletado(palabra):

    palabra = palabra.strip()

    if len(palabra) > 50:
        raise ValueError("Texto demasiado largo")

    query = text("""
        SELECT id, descripcion
        FROM fracciones_arancelarias
        WHERE descripcion ILIKE :busqueda
        LIMIT 20
    """)

    with _get_engine().connect() as conn:
        df = pd.read_sql(query, conn, params={
            "busqueda": f"%{palabra}%"
        })

    df = df.drop_duplicates(subset=["id"])

    return df.to_dict(orient="records")


#result = autocompletado("Maíz")
#print(result)
