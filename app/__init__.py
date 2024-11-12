# Flask 애플리케이션 인스턴스 생성 및 설정 초기화

from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes import bp
    app.register_blueprint(bp)

    return app