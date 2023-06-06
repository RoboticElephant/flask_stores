import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from blocklist import BLOCKLIST
# import models

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)

    # If there is an exception hidden inside an extension then propagate it to the main app so it can be seen
    app.config["PROPAGATE_EXCEPTIONS"] = True
    # Title of the API
    app.config["API_TITLE"] = "Store REST API"
    # Version
    app.config["API_VERSION"] = "v1"
    # OpenAPI Version
    app.config["OPENAPI_VERSION"] = "3.0.3"
    # Where the root of the API is
    app.config["OPENAPI_URL_PREFIX"] = "/"
    # Use swagger for the API implementation
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    # Where the code is to be used
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # The DATABASE_URL allows us to save it outside our code if it exists
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    #
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Initializes flask's sqlalchemy allowing for the connection of Flask to SQLAlchemy
    db.init_app(app)
    # Will create all the tables in our database if they don't already exist
    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db)
    api = Api(app)

    # This is the secret key that makes sure the user hasn't created their own
    # This should be stored as an environment variable.
    # What we can do is run secrets.SystemRandom().getrandbits(128) to create the secret that would be used here
    app.config["JWT_SECRET_KEY"] = "josh" # TODO this will just be temporary for now
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"description": "The token has been revoked.", "error": "token_revoked"}), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"description": "The token is not fresh.", "error": "fresh_token_required"}), 401

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # This current implementation isn't ideal. Should see whether the user is an admin by looking at a database.
        if identity == 1:
            return {"is_admin": True}
        else:
            return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        jsonify({"description": "Request does not contain an access token.", "error": "authorization_required"}), 401

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    return app


if __name__ == '__main__':
    create_app()

# docker build -t flask-stores-api .
# docker run -dp 5005:5000 -w /app -v "$(pwd):/app" flask-stores-api
