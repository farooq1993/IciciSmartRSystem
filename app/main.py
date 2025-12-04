from flask import Flask, render_template
import os
from utils.extension import db, migrate
from utils.database import DATABASE_URL

def create_app():
    app = Flask(__name__, static_url_path='/static')

    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv('SECRET_KEY', None)

    # Initialize DB + Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Import all models so Alembic can detect them
    from models.recon_model import ReconResult
    from models.channel import CreateChannel, DataStructureField
    from models.users import Users

    # Register blueprints
    from routes.recon_routes import recon_api
    from routes.users_routes import user
    from routes.channel import channel

    app.register_blueprint(recon_api, url_prefix="/recon")
    app.register_blueprint(user, url_prefix="/recon")
    app.register_blueprint(channel, url_prefix="/recon")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
