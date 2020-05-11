from flask import url_for   # 生成URL
from flask import render_template   # 渲染模板
from flask import request   # 请求对象
from flask import redirect  # 重定向
from flask import flash     # 消息提示
from flask_login import login_required, current_user, login_user, logout_user  # 用户认证

from watchlist import app, db
from watchlist.models import User, Movie


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
    return redirect(url_for('index'))


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
        else:
            flash('Invalid input! Please try again.')

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()     # 用户登出
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
