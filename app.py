from flask import Flask
from flask import url_for   # 生成URL
from flask import render_template   # 渲染模板
from flask import request   # 请求对象
from flask import redirect  # 重定向
from flask import flash     # 消息提示
from flask_sqlalchemy import SQLAlchemy     # 数据库拓展
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user  # 用户认证
from werkzeug.security import generate_password_hash, check_password_hash   # 用户安全
import os
import click

app = Flask(__name__)   # 注册应用

# 配置数据库连接地址，win三斜线，其他四斜线
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'    # 签名密钥（存于cookie中）

login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

# # 模板测试数据
# name = 'Leon'
# movies = [
#     {'title': 'Naruto', 'year': '1998'},
#     {'title': 'King of Comedy', 'year': '1999'},
#     {'title': 'Identity', 'year': '2003'}
# ]


@app.route('/', methods=['GET', 'POST'])  # 装饰器，与传入的字符串参数作为URL规则进行绑定（可多个），'/'指根目录
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:   # 若没有用户认证 则重定向返回主页
            return redirect(url_for('index'))

        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input! Please try again.')   # 错误提示
            return redirect(url_for('index'))   # 重定向回主页

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item added.')    # 成功添加提示
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)  # 渲染模板


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required     # 需要用户认证
def edit(movie_id):     # 编辑记录
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(title) > 60 or len(year) > 4:
            flash('Invalid input! Please try again.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Successful updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)    # 传入被编辑的记录


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])     # 只能用post删除
@login_required     # 需要用户认证
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return render_template(url_for('index'))


@app.errorhandler(404)  # errorhandler专门用来处理错误，参数为错误代码
def page_not_found(e):
    return render_template('404.html'), 404  # 返回模板，状态码


@app.route('/user/<user_name>')   # <>可以传入自定义参数，但要注意参数名要和修饰的函数参数名一致(user_name)
def user_page(user_name):
    return 'This is {} page'.format(user_name)


@app.route('/login', methods=['GET', 'POST'])
def login():    # 登录函数
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input! Please try again.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.user_name and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    load_user()     # 用户登出
    flash('Logout success.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@ login_required    # 用户认证
def settings():     # 修改用户名
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input! Please try again.')
            return redirect(url_for('settings'))

        current_user.name = name    # 等同于User.query.first().name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@login_manager.user_loader
def load_user(user_id):     # 用户加载回调函数，查询用户id然后返回用户对象
    user = User.query.get(int(user_id))
    return user


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


@app.cli.command()
@click.option('--username', prompt=True, help='The username to login.')
# hide_input参数隐藏输入，confirmation_prompt参数要求二次确认
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password to login.')
def admin(username, password):
    db.create_all()
    user = User.query.first()

    if user is not None:    # 用户存在，设置密码
        click.echo('Updating user...')
        user.user_name = username
        user.set_password(password)
    else:   # 用户不存在，新建并设置密码
        click.echo('Creating user...')
        user = User(user_name=username, name='Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()     # 保存到数据库
    click.echo('Done.')


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
