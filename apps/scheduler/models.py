from datetime import datetime

from apps.app import db


# db.Modelを継承したScheduleクラス->項目を変更のこと．
class ScheduleLists(db.Model):
    __tablename__ = "schedulelists"
    # id, user_id, yyyymm, date, members
    id = db.Column(db.Integer, primary_key=True)
    # usersテーブルのid columnを外部キーに設定．
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    yyyymm = db.Column(db.String)  # schedule month

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # backrefでschedulesとのrelation情報を設定．
    schedules = db.relationship("Schedules", backref="schedulelists")


# db.Modelを継承したScheduleクラス->項目を変更のこと．
class Schedules(db.Model):
    __tablename__ = "schedules"
    # id, user_id, yyyymm, date, members
    id = db.Column(db.Integer, primary_key=True)
    # usersテーブルのid columnを外部キーに設定．
    schedulelist_id = db.Column(db.String, db.ForeignKey("schedulelists.id"))
    date = db.Column(db.DateTime)
    k_members = db.Column(db.String)
    g_members = db.Column(db.String)
