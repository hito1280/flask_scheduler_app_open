import os
import tempfile
import zipfile
from datetime import datetime

import pandas as pd
from apps.app import db
from apps.crud.models import User
from apps.scheduler.models import ScheduleLists, Schedules
from apps.scheduler.problem_solving import KandGProblem
from apps.scheduler.read_df import csvtodf, makeical
from flask import Blueprint, make_response, redirect, render_template, request, session
from flask_login import current_user, login_required
from sqlalchemy import asc

scheduler = Blueprint("scheduler", __name__, template_folder="templates")


def preprocess(request):
    """リクエストデータを受け取り、データフレームに変換する関数"""
    # 各ファイルを取得する
    csvfile = request.files["csvfile"]
    data = csvtodf(csvfile)
    df_kagisime, df_gomisute = data.df_input()

    return df_kagisime, df_gomisute


def postprocess(solution_df):
    """最適化結果をHTML形式に変換する関数"""
    solution_html = solution_df.to_html(header=True, index=True)
    return solution_html


def check_request(request):
    """リクエストにcsvfileが含まれているか確認する関数"""
    # 各ファイルを取得する
    csvfile = request.files["csvfile"]

    # ファイルが選択されているか確認
    if csvfile.filename == "":
        # 学生データが選ばれていません
        return False

    return True


@scheduler.route("/")
def index():
    if current_user.is_authenticated:
        user_id = session["_user_id"]
        # スケジュール一覧を取得．
        user_schedulelists = (
            db.session.query(User, ScheduleLists)
            .join(ScheduleLists)
            .filter(User.id == ScheduleLists.user_id, User.id == user_id)
            .all()
        )
    else:
        user_schedulelists = []

    return render_template("scheduler/index.html", schedulelists=user_schedulelists)


@scheduler.route("/schedule_decision", methods=["GET", "POST"])
def schedule_decision():
    """最適化の実行と結果の表示を行う関数"""
    # トップページを表示する（GETリクエストがきた場合）
    if request.method == "GET":
        return render_template("scheduler/schedule_decision.html", solution_html=None)

    # POSTリクエストである「最適化を実行」ボタンが押された場合に実行
    # データがアップロードされているかチェックする。適切でなければ元のページに戻る
    if not check_request(request):
        return redirect(request.url)

    # 前処理（データ読み込み）
    df_kagisime, df_gomisute = preprocess(request)
    # 最適化実行
    prob = KandGProblem(df_kagisime, df_gomisute)
    solution_df = prob.solve()
    L_gomisute_members = list(prob.L_gomisute_members)

    # ログインしている場合，DBに決定した予定表を追加．
    if current_user.is_authenticated:
        yyyy, mm, _ = solution_df.index[0].split("/")
        user_id = session["_user_id"]
        print(user_id)
        print("currentuser:", current_user)
        is_new_schedule = not ScheduleLists.query.filter_by(
            user_id=user_id, yyyymm=yyyy + mm
        ).all()
        if is_new_schedule:
            schedule_list = ScheduleLists(user_id=user_id, yyyymm=yyyy + mm)
            db.session.add(schedule_list)
            db.session.commit()

        schedulelist_id = (
            ScheduleLists.query.filter_by(user_id=user_id, yyyymm=yyyy + mm)
            .group_by("id")
            .first()
        )

        print(schedulelist_id.id)
        for row in solution_df.itertuples():
            if not is_new_schedule:
                print(datetime.strptime(row[0], "%Y/%m/%d"))
                old_schedule = Schedules.query.filter_by(
                    schedulelist_id=schedulelist_id.id,
                    date=datetime.strptime(row[0], "%Y/%m/%d"),
                ).first()
                print(old_schedule)
                if old_schedule:
                    old_schedule.k_members = row[1]
                    old_schedule.g_members = row[2]
                    db.session.add(old_schedule)
                    db.session.commit()

            else:
                schedule = Schedules(
                    schedulelist_id=schedulelist_id.id,
                    date=datetime.strptime(row[0], "%Y/%m/%d"),
                    k_members=row[1],
                    g_members=row[2],
                )
                db.session.add(schedule)
                db.session.commit()

    # 後処理（最適化結果をHTMLに表示できる形式にする）
    solution_html = postprocess(solution_df)
    return render_template(
        "scheduler/schedule_decision.html",
        solution_html=solution_html,
        solution_df=solution_df,
        L_gomisute_members=" ".join(L_gomisute_members),
    )


# とりあえず書いてみる．要検証
@scheduler.route("/download_template", methods=["POST"])
def download_template():
    path = "apps/files/template.csv"
    response = make_response()
    with open(path) as f:
        template_csv = f.read()
        response.data = template_csv
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=template.csv"
    return response


# 過去のデータを見る
@scheduler.route("/pastdata/<user_id>/<yyyymm>", methods=["GET", "POST"])
@login_required
def show_pastdata(user_id, yyyymm):
    user_schedule = ScheduleLists.query.filter_by(
        user_id=user_id, yyyymm=yyyymm
    ).first()

    schedule = (
        Schedules.query.filter_by(
            schedulelist_id=user_schedule.id,
        )
        .order_by(asc(Schedules.date))
        .all()
    )

    return render_template(
        "scheduler/show_pastdata.html", yyyymm=yyyymm, schedules=schedule
    )


# 過去のデータをダウンロードできるようにしたい．要検証
@scheduler.route("/scheduler/<user_id>/<date>", methods=["POST"])
@login_required
def download_past_data(date):

    df = pd.DataFrame(
        [
            ["t1271", "千葉", 51476, "2003-9-25"],
            ["t1272", "勝浦", 42573, "2003-3-16"],
            ["t1273", "市原", 28471, "2003-6-21"],
            ["t1274", "流山", 36872, "2003-8-27"],
            ["t1275", "八千代", 24176, "2003-11-5"],
            ["t1276", "我孫子", 13275, "2003-1-12"],
            ["t1277", "鴨川", 85194, "2003-12-18"],
        ]
    )
    template_csv = df.to_csv(index=True, encoding="utf_8_sig")
    response = make_response()
    response.data = template_csv
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=template.csv"
    return response


@scheduler.route("/schedule_decision/download_csv", methods=["POST"])
def download_csv():
    """リクエストに含まれるHTMLの表形式データをcsv形式に変換してダウンロードする関数"""
    solution_html = request.form.get("solution_html")
    solution_df = pd.read_html(solution_html)[0]
    solution_df = solution_df.set_axis(["日付", "鍵閉め", "ゴミ捨て"], axis="columns")
    solution_csv = solution_df.to_csv(index=True, encoding="utf_8_sig")
    response = make_response()
    response.data = solution_csv
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=solution.csv"
    return response


@scheduler.route("/schedule_decision/download_ical", methods=["POST"])
def download_ical():
    """リクエストに含まれるHTMLの表形式データをcsv形式に変換してダウンロードする関数"""
    solution_html = request.form.get("solution_html")
    L_gomisute_members = list(request.form.get("L_gomisute_members").split())
    solution_df = pd.read_html(solution_html)[0]
    solution_df = solution_df.set_axis(["日付", "鍵閉め", "ゴミ捨て"], axis="columns")
    solution_df = solution_df.set_index(["日付"])

    tmpdir = tempfile.TemporaryDirectory()
    icals = makeical(solution_df, L_gomisute_members)
    data_files = icals.files
    with zipfile.ZipFile(tmpdir.name + "/icalfiles.zip", mode="w") as new_zip:
        for data_file in data_files:
            with open(os.path.join(tmpdir.name, data_file[1]), mode="wb") as f:
                f.write(data_file[0])
            new_zip.write(tmpdir.name + "/" + data_file[1], data_file[1])

    response = make_response()
    with open(tmpdir.name + "/icalfiles.zip", "rb") as f:
        response.data = f.read()
    tmpdir.cleanup()
    response.headers["Content-Type"] = "data/zip"
    response.headers["Content-Disposition"] = "attachment; filename=icalfiles.zip"
    return response
