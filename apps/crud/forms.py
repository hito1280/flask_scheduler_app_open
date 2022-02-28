from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, length


class UserForm(FlaskForm):
    # ユーザーフォームのusername属性のラベルとバリデータを設定．
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です"),
            length(max=30, message="30字以内で入力してください"),
        ],
    )
    # ユーザーフォームのemail属性のラベルとバリデータ設定．
    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスは必須です"),
            Email(message="有効なメールアドレスではありません"),
        ],
    )

    # ユーザーフォームのemail属性のラベルとバリデータ設定．
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(message="パスワードは必須です")],
    )

    # ユーザーフォームのsubmit文を設定．
    submit = SubmitField("新規登録")
