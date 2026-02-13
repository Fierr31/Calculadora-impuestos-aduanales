import os
from contextlib import contextmanager

from flask import Flask, jsonify, render_template, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__, template_folder="../templates", static_folder="../static")


def db_config() -> dict:
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", "aduanas"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    }


@contextmanager
def get_connection():
    conn = psycopg2.connect(**db_config())
    try:
        yield conn
    finally:
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/productos")
def buscar_productos():
    query = request.args.get("query", "").strip()

    if len(query) < 2:
        return jsonify([])

    sql = """
        SELECT id, nombre, categoria
        FROM productos
        WHERE nombre ILIKE %s
        ORDER BY nombre ASC
        LIMIT 10;
    """

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (f"%{query}%",))
                productos = cursor.fetchall()

        return jsonify(productos)
    except Exception as exc:
        return jsonify({"error": f"No se pudo consultar productos: {exc}"}), 500


@app.get("/api/productos/<int:producto_id>")
def detalle_producto(producto_id: int):
    sql = """
        SELECT
            p.id,
            p.nombre,
            p.categoria,
            p.descripcion,
            p.precio_referencia,
            p.arancel,
            p.pais_origen_sugerido,
            ARRAY_REMOVE(ARRAY[
                CASE WHEN p.requiere_permiso THEN 'Requiere permiso especial' END,
                CASE WHEN p.requiere_certificado THEN 'Requiere certificado' END,
                CASE WHEN p.requiere_norma_nom THEN 'Cumple norma NOM' END
            ], NULL) AS requisitos
        FROM productos p
        WHERE p.id = %s;
    """

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, (producto_id,))
                producto = cursor.fetchone()

        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        return jsonify(producto)
    except Exception as exc:
        return jsonify({"error": f"No se pudo consultar detalle: {exc}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
