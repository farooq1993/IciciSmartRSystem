from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from routes.recon_routes import recon_api
from routes.users_routes import user
from routes.channel import channel
from models.recon_model import ReconResult
from utils.database import Base, engine,DATABASE_URL
import os
from flask_migrate import Migrate


Base.metadata.create_all(bind=engine)

app = Flask(__name__, static_url_path='/static')

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


migrate = Migrate(app, db)


app.secret_key = os.getenv('SECRET_KEY',None)

app.register_blueprint(recon_api, url_prefix="/recon")
app.register_blueprint(user, url_prefix="/recon")
app.register_blueprint(channel, url_prefix="/recon")

    
@app.route("/health", methods=['GET'])
def home():
    return {"message": "SMART-R Reconciliation API is running"}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
