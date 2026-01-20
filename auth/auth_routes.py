from flask import Blueprint, request, jsonify
from .auth_utils import hash_password
from .auth_db import check_user, add_user
from database import create_connection
import sqlite3

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    id = data.get('id')
    password = data.get('password')

    if not id or not password:
        return jsonify({'error': 'ID et mot de passe requis'}), 400

    if add_user(id, password):
        return jsonify({'message': 'Utilisateur enregistré'}), 201
    else:
        return jsonify({'error': 'ID déjà utilisé ou erreur DB'}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    id = data.get('id')
    password = data.get('password')

    if not id or not password:
        return jsonify({'error': 'ID et mot de passe requis'}), 400

    if check_user(id, password):
        return jsonify({'message': 'Connexion réussie'}), 200
    else:
        return jsonify({'error': 'ID ou mot de passe invalide'}), 401

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        if not data or 'id' not in data or 'password' not in data:
            return jsonify({'error': 'ID et nouveau mot de passe requis'}), 400

        id = data['id']
        new_password = data['password']

        # Hachage du nouveau mot de passe
        password_hash, salt = hash_password(new_password)

        conn = create_connection()
        if conn is None:
            return jsonify({'error': 'Connexion DB échouée'}), 500

        cursor = conn.cursor()
        # Vérifie que l'utilisateur existe
        cursor.execute("SELECT 1 FROM users WHERE id = ?", (id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

        # Met à jour le mot de passe
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
            (password_hash, salt, id)
        )
        conn.commit()
        return jsonify({'message': 'Mot de passe mis à jour'}), 200

    except sqlite3.Error as e:
        print(f"Erreur DB: {str(e)}")
        return jsonify({'error': 'Erreur base de données'}), 500
    except Exception as e:
        print(f"Erreur inattendue: {str(e)}")
        return jsonify({'error': 'Erreur interne'}), 500
    finally:
        if 'conn' in locals():
            conn.close()
