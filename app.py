from flask import Flask
from flask import url_for   # 生成URL
from flask import render_template   # 渲染模板
from flask_sqlalchemy import SQLAlchemy     # 数据库拓展
import os
import click

app = Flask(__name__)   # 注册应用

# 配置数据库连接地址，win三斜线，其他四斜线
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # 关闭对模型修改的监控

db = SQLAlchemy(app)

# # 模板测试数据
# name = 'Leon'
# movies = [
#     {'title': 'Naruto', 'year': '1998'},
#     {'title': 'King of Comedy', 'year': '1999'},
#     {'title': 'Identity', 'year': '2003'}
# ]


@app.route('/')  # 装饰器，与传入的字符串参数作为URL规则进行绑定（可多个），'/'指根目录
@app.route('/home')
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)  # 渲染模板


@app.errorhandler(404)  # errorhandler专门用来处理错误，参数为错误代码
def page_not_found(e):
    user = User.query.first()
    return render_template('404.html'), 404  # 返回模板，状态码


@app.route('/user/<user_name>')   # <>可以传入自定义参数，但要注意参数名要和修饰的函数参数名一致(user_name)
def user_page(user_name):
    return 'This is {} page'.format(user_name)


@app.context_processor  # 模板上下文处理函数，返回的字典会统一注入每一个模板的上下文中，无需重复写入
def inject_user():
    user = User.query.first()
    return dict(user=user)  # 需返回字典，等同于return {'user': user}


# 'url_for'函数常用来根据传入的参数生成URL
# 视图函数名可以作为端点(endpoint)，同时用来生成URL，'url_for'函数接受的第一个参数就是端点值，默认是视图函数的名称
@app.route('/test')
def test_url_for():
    print(url_for('home'))  # '/home'
    print(url_for('user_page', user_name='leo'))    # '/user/leo'
    print(url_for('user_page', user_name='test'))   # '/user/test'
    print(url_for('test_url_for'))  # '/test'
    print(url_for('test_url_for', num=2))   # '/test?num=2'
    return 'TEST'


# 实现数据库清空和初始化的自动化操作
@app.cli.command()  # 注册即为命令
@click.option('--drop', is_flag=True, help='Create after drop.')    # 使用'--drop'选项来删表
def initdb(drop):   # 初始化数据库
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


# 创建数据库模型，写完之后要在flask shell中from app import db -> db.create_all()
# 若要重新生成表，则需要先db.drop_all() -> db.create_all()
class User(db.Model):   # user模型，继承db.Model而来，表名为user（小写，自动生成）
    id = db.Column(db.Integer, primary_key=True)    # 每一个字段要实例化db.Column，传入字段类型
    name = db.Column(db.String(20))


class Movie(db.Model):  # movie模型
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))
