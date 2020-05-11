from flask import render_template

from watchlist import app


@app.errorhandler(404)  # errorhandler专门用来处理错误，参数为错误代码
def page_not_found(e):
    return render_template('errors/404.html'), 404  # 返回模板，状态码


# 400
@app.errorhandler(400)
def page_not_found(e):
    return render_template('errors/400.html'), 400  # 返回模板，状态码


# 500
@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500  # 返回模板，状态码

