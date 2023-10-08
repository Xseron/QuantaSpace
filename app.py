import os

import yaml
from flask import Flask, render_template
from flask_cors import CORS

import routers

# from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "asdasasdhadsbhjadshjadshjdahads"

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.register_blueprint(routers.page)
    app.register_blueprint(routers.api)
    # app.app_context().push()
    # db.create_all()
    app.run(debug=True)