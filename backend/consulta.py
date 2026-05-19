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

def obtener(id):
    #print("ID recibido:", id)

    query = text("""
        SELECT *
        FROM fracciones_arancelarias
        WHERE id = :id
        LIMIT 1
    """)

    with _get_engine().connect() as conn:
        result = conn.execute(query, {"id": id})
        row = result.mappings().first()

    if not row:
        return {}

    producto = dict(row)

    producto.pop("id", None)
    producto.pop("exento", None)

    return producto
#result = obtener("1888")
#print(result)