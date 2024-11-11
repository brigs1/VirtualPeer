# Flask 애플리케이션 인스턴스 생성 및 설정 초기화

from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # CORS 활성화

    with app.app_context():
        from . import routes

    return app