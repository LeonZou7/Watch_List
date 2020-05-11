import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLite URI compatible
WIN = sys.platform.startswith('win')    # 判断当前系统类别
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
# 更新路径，将root_path加入os.path.dirname()中以便定位文件到根目录
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):     # 用户加载回调函数，查询用户id然后返回用户对象
    from watchlist.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'


@app.context_processor
def inject_user():      # 模板上下文处理函数，返回的字典会统一注入每一个模板的上下文中，无需重复写入
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)      # 需返回字典，等同于return {'user': user}


from watchlist import views, errors, commands
