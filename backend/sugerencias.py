from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
os.getenv("DATABASE_URL")
)

def autocompletado(palabra):

    palabra = palabra.strip()

    if len(palabra) > 50:
        raise ValueError("Texto demasiado largo")

    

    query = text("""
        SELECT descripcion
        FROM fracciones_arancelarias
        WHERE descripcion ILIKE :busqueda
        LIMIT 20
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={
            "busqueda": f"%{palabra}%"
        })

    return df["descripcion"].drop_duplicates().tolist()


result = autocompletado("Maíz")
print(result)
