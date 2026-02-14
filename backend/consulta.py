from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
os.getenv("DATABASE_URL")
)

def obtener(id):
    print("ID recibido:", id)

    query = text("""
        SELECT *
        FROM fracciones_arancelarias
        WHERE id = :id
        LIMIT 1
    """)

    with engine.connect() as conn:
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