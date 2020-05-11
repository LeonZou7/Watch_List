from flask_login import UserMixin  # 用户认证
from werkzeug.security import generate_password_hash, check_password_hash   # 用户安全

from watchlist import db


# 创建数据库模型，写完之后要在flask shell中from app import db -> db.create_all()
# 若要重新生成表，则需要先db.drop_all() -> db.create_all()
class User(db.Model, UserMixin):   # user模型，继承db.Model而来，表名为user（小写，自动生成）
    id = db.Column(db.Integer, primary_key=True)    # 每一个字段要实例化db.Column，传入字段类型
    name = db.Column(db.String(20))
    user_name = db.Column(db.String(20))    # 用户名
    password_hash = db.Column(db.String(128))   # 密码散列值

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):  # movie模型
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))