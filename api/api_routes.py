from flask import Blueprint, request, jsonify, make_response
import sqlite3
from database import create_connection

api_bp = Blueprint('api', __name__)

API_KEY = "openbikecle"

@api_bp.before_request
def check_api_key():
    if request.method == "OPTIONS":
        return make_response("", 200)

    if request.endpoint in ["api.get_measurements", "api.add_measurement"]:
        key = request.headers.get("X-API-KEY")
        if key != API_KEY:
            return jsonify({"error": "Accès non autorisé"}), 401

@api_bp.route("/measurements", methods=["GET", "OPTIONS"])
def get_measurements():
    if request.method == "OPTIONS":
        return make_response("", 200)

    limit = request.args.get("limit", default=100, type=int)
    conn = create_connection()
    if conn is None:
        return jsonify({"error": "Connexion DB échouée"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT lat, lng, day, month, year, hour, minute, second,
                   distanceMin_cm, speed_kmh, valid
            FROM measurements
            ORDER BY year DESC, month DESC, day DESC,
                     hour DESC, minute DESC, second DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

        # Si aucune mesure n'est trouvée, retourne une liste vide
        if not rows:
            return jsonify([])

        measurements = [{
            "lat": row[0],
            "lng": row[1],
            "day": row[2],
            "month": row[3],
            "year": row[4],
            "hour": row[5],
            "minute": row[6],
            "second": row[7],
            "distanceMin_cm": row[8],
            "speed_kmh": row[9],
            "valid": row[10]
        } for row in rows]

        return jsonify(measurements)

    except sqlite3.Error as e:
        # Log l'erreur pour le débogage
        print(f"Erreur SQL: {e}")
        return jsonify({"error": "Erreur interne de la base de données"}), 500
    except Exception as e:
        # Attrape toute autre exception inattendue
        print(f"Erreur inattendue: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500
    finally:
        if conn:
            conn.close()

@api_bp.route("/measurements", methods=["POST", "OPTIONS"])
def add_measurement():
    if request.method == "OPTIONS":
        return make_response("", 200)

    data = request.get_json(silent=True)
    required = [
        "lat", "lng", "day", "month", "year",
        "hour", "minute", "second",
        "distanceMin_cm", "speed_kmh", "valid"
    ]

    if not data or not all(k in data for k in required):
        return jsonify({"error": "Champs manquants"}), 400

    conn = create_connection()
    if conn is None:
        return jsonify({"error": "Connexion DB échouée"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO measurements
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(data[k] for k in required))
        conn.commit()
        return jsonify({"status": "succès"}), 201

    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
