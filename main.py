from flask import Flask
from flask_cors import CORS
from database import init_db
from auth.auth_routes import auth_bp
from api.api_routes import api_bp

app = Flask(__name__)

# CORS
CORS(
    app,
    resources={
        r"/api/*": {"origins": "*"},
        r"/auth/*": {"origins": "*"}  # Autorise CORS pour tous les endpoints /auth/
    },
    allow_headers=["Content-Type", "X-API-KEY", "ngrok-skip-browser-warning"],
    methods=["GET", "POST", "OPTIONS"]
)


# Initialisation DB
init_db()

# Enregistrement des blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
