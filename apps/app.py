from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from apps.config import config

db = SQLAlchemy()

csrf = CSRFProtect()

login_manager = LoginManager()
# 未ログイン時にリダイレクトするエンドポイントの指定
login_manager.login_view = "auth.signup"
login_manager.login_message = ""  # ログイン時に何も表示しない


# make create_app function
# brueprintで分割．
def create_app(config_key):
    # Flask instance
    app = Flask(__name__)

    # config_keyにマッチする環境のコンフィグクラスを読み込む．
    app.config.from_object(config[config_key])

    """# setting config
    app.config.from_mapping(
        SECRET_KEY="2AZSMss3p5QPbcY2hBsJ",  # defalt value from text.
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(__file__).parent.parent/'local.sqlite'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=True,
        WTF_CSRF_SECRET_KEY="AuwzyszU5sugKN7KZs6f",
    )"""

    csrf.init_app(app)

    # SQLAlchemy, Migrateとアプリを連携.
    db.init_app(app)
    Migrate(app, db)

    login_manager.init_app(app)

    # viewsのcrudをアプリへ登録
    from apps.crud import views as crud_views

    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    # viewsのauthをアプリへ登録
    from apps.auth import views as auth_views

    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    # viewsのschedulerをアプリへ登録
    from apps.scheduler import views as scheduler_views

    app.register_blueprint(scheduler_views.scheduler)

    return app
