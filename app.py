from flask import Flask, send_from_directory
from backend.routes import api
import os


# ============================================================
# CREATE FLASK APP
# ============================================================

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)


# ============================================================
# REGISTER API ROUTES
# ============================================================

app.register_blueprint(api)


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def home():
    return send_from_directory(
        "frontend",
        "index.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():
    return {
        "status": "success",
        "message": "Cosmora backend is running"
    }


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )