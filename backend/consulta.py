from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
os.getenv("DATABASE_URL")
)

def obtener(palabra):

    palabra = palabra.strip()

    if len(palabra) > 50:
        raise ValueError("Texto demasiado largo")

    query = text("""
        SELECT *
        FROM fracciones_arancelarias
        WHERE descripcion = :busqueda
        LIMIT 1
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={
            "busqueda": palabra
        })

    return df

result = obtener("Harina de maíz.")
print(result)