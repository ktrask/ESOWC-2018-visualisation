from flask import Flask
from flask_bootstrap import Bootstrap
#from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__, static_url_path="/static")
    app.config.from_object('config')
    Bootstrap(app)
    return(app)

app = create_app()
#db = SQLAlchemy(app)


from app import views, models

