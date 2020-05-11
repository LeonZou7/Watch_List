import click

from watchlist import app, db
from watchlist.models import User, Movie


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


# 一键加入虚拟数据
@app.cli.command()
def forge():
    db.create_all()
    name = 'Leon'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]

    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)

    db.session.commit()
    click.echo('Done.')