from flask import Flask
from flask import url_for
app = Flask(__name__)


@app.route('/')  # 装饰器，与传入的字符串参数作为URL规则进行绑定（可多个），'/'指根目录
@app.route('/home')
def hello():
    return 'hello, flask!'


@app.route('/user/<user_name>')   # <>可以传入自定义参数，但要注意参数名要和修饰的函数参数名一致(user_name)
def user_page(user_name):
    return 'This is {} page'.format(user_name)


# 视图函数名可以作为代表某个路由的端点(endpoint)，同时用来生成URL，'url_for'函数接受的第一个参数就是端点值，默认是视图函数的名称
# 方便生成URL
@app.route('/test')
def test_url_for():
    print(url_for('home'))  # '/home'
    print(url_for('user_page', user_name='leo'))    # '/user/leo'
    print(url_for('user_page', user_name='test'))   # '/user/test'
    print(url_for('test_url_for'))  # '/test'
    print(url_for('test_url_for', num=2))   # '/test?num=2'
    return 'TEST'
