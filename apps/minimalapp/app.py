import logging
import os

from email_validator import EmailNotValidError, validate_email
from flask import (
    Flask,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message

app = Flask(__name__)
# add SECRET_KEY
app.config["SECRET_KEY"] = "EHarMwPz2dL6BKVaChNU"
# set log level
app.logger.setLevel(logging.DEBUG)
# リダイレクトを中断しないようにする．リダイレクトするとリクエストした値がflask-debugtoolbarで確認できなくなるので
# デフォルトではTrue（リダイレクトを中断）になっている．
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# DebugToolbarExtensionにアプリケーションをセット．
toolbar = DebugToolbarExtension(app)
# add condig for mail class
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_POST"] = os.environ.get("MAIL_POST")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# flask-mail拡張．
mail = Mail(app)


@app.route("/")
def index():
    return "Hello flask"


@app.route("/hello/<name>", methods=["GET", "POST"], endpoint="hello-endpoint")
def hello(name):
    return f"Hello, {name}!"


@app.route("/name/<name>", methods=["GET"])
def show_name(name):
    return render_template("index.html", name=name)


@app.route("/contact", methods=["GET"])
def contact():
    # レスポンスオブジェクトの取得
    response = make_response(render_template("contact.html"))

    # setting cookie
    response.set_cookie("flasktrain key", "frasktrain value")

    # setting session
    session["username"] = "ichiro"

    return response


@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        # get values using form attribute
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]
        # 入力チェック
        is_valid = True
        if not username:
            flash("ユーザー名は必須です")
            is_valid = False

        if not email:
            flash("メールアドレスは必須です")
            is_valid = False
        else:
            try:
                validate_email(email)
            except EmailNotValidError:
                flash("メールアドレスの形式で入力してください")
                is_valid = False

        if not description:
            flash("問い合わせ内容は必須です")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))
        # send mail
        send_email(
            email,
            "問い合わせありがとうございます。",
            "contact_mail",
            username=username,
            description=description,
        )
        # redirect to contact-endpoint
        flash("問い合わせありがとうございました。")
        return redirect(url_for("contact_complete"))
    return render_template("contact_complete.html")


def send_email(to, subject, template, **kwargs):
    """sending email"""
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)
