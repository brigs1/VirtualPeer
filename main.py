# main.py
from flask import Flask
from flask_cors import CORS
from app.routes import bp  # app 폴더에서 routes를 import

def create_app():
    app = Flask(__name__,
                template_folder='app/templates')  # template 폴더 경로 지정
    CORS(app)
    
    # Blueprint 등록
    app.register_blueprint(bp)
    
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        app.run(host='127.0.0.1', port=5001, debug=True)
    except Exception as e:
        print(f"Error starting application: {e}")