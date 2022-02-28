from apps.app import db
from apps.crud.forms import UserForm
from apps.crud.models import User
from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_required

crud = Blueprint("crud", __name__, template_folder="templates", static_folder="static")


@crud.route("/")
@login_required
def index():
    return render_template("crud/index.html")


@crud.route("/sql")
@login_required
def sql():
    db.session.query(User).all()
    return "コンソールログを確認してください"


@crud.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    form = UserForm()
    # フォームの値をバリデート．
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        # ユーザーを追加してコミット
        db.session.add(user)
        db.session.commit()
        # ユーザー一覧画面へリダイレクト．
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)


@crud.route("/users")
@login_required
def users():
    """ユーザー一覧を取得"""
    users = User.query.all()
    return render_template("crud/index.html", users=users)


@crud.route("/users/<user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    form = UserForm()

    # get user using User model
    user = User.query.filter_by(id=user_id).first()

    # フォームの値をバリデート．
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        # ユーザーを追加してコミット
        db.session.add(user)
        db.session.commit()
        # ユーザー一覧画面へリダイレクト．
        return redirect(url_for("crud.users"))

    return render_template("crud/edit.html", user=user, form=form)


@crud.route("/users/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    # ユーザーを削除してコミット
    db.session.delete(user)
    db.session.commit()
    # ユーザー一覧画面へリダイレクト．
    return redirect(url_for("crud.users"))
