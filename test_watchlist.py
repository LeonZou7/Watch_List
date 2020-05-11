import unittest

from watchlist import app, db
from watchlist.models import User, Movie
from watchlist.commands import forge, initdb


class WatchlistTestCase(unittest.TestCase):
    def setUp(self) -> None:    # 固定函数，用于进行测试之前的设置
        # 更新配置
        app.config.update(
            TESTING=True,   # 打开测试模式
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'    # 使用内存型数据库，不会干扰文件
        )
        # 创建测试数据库和表
        db.create_all()
        # 创建测试数据
        user = User(name='Test', user_name='test')
        user.set_password('123')
        movie = Movie(title='Test Movie', year='2020')
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()     # 得到一个模拟客户端对象用于测试
        self.runner = app.test_cli_runner()     # 得到一个命令运行器对象

    def tearDown(self) -> None:     # 固定函数，用于处理测试之后的数据
        db.session.remove()     # 清除会话
        db.drop_all()   # 删除数据库

    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):  # 测试程序是否处于测试模式
        self.assertTrue(app.config['TESTING'])

    # 404页面测试
    def test_404_page(self):
        response = self.client.get('/nothing')  # 传入目标URL，取得回应
        data = response.get_data(as_text=True)
        self.assertIn('Sorry, not found --- 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)     # 判断响应码

    # 主页测试
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie', data)
        self.assertEqual(response.status_code, 200)

    def login(self):
        self.client.post('login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    # 测试创建功能
    def test_create_item(self):
        self.login()

        response = self.client.post('/', data=dict(
            title='test add',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('test add', data)
        self.assertIn('Item added.', data)

        # 测试非法操作
        response = self.client.post('/', data=dict(
            title='',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item Created', data)
        self.assertIn('Invalid input', data)

        response = self.client.post('/', data=dict(
            title='test add',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item Created', data)
        self.assertIn('Invalid input', data)

    # 测试更新功能
    def test_update_item(self):
        self.login()

        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie', data)
        self.assertIn('2020', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='test edit',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Successful updated.', data)
        self.assertNotIn('Invalid input! Please try again.', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item Updated', data)
        self.assertIn('Invalid input', data)

        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2020'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item Updated', data)
        self.assertIn('Invalid input', data)

    # 测试删除功能
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie', data)

    # 测试登录
    def test_login(self):
        response = self.client.post('login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)

        # 测试错误登录
        response = self.client.post('/login', data=dict(
            username='test',
            password='456'
            ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input! Please try again.', data)

        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input', data)

        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input', data)

        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input', data)

    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Logout success.', data)
        self.assertIn('Login', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    # 测试设置
    def test_settings(self):
        self.login()

        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Old Name', data)

        # 测试更新
        response = self.client.post('/settings', data=dict(
            name='test edit name'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated', data)
        self.assertIn('test edit name', data)

        # 测试错误更新
        response = self.client.post('/settings', data=dict(
            name=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated', data)
        self.assertIn('Invalid input', data)

    # 测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)  # invoke函数执行函数
        self.assertIn('Done.', result.output)   # output属性返回输出信息
        self.assertNotEqual(Movie.query.count(), 0)

    # 测试初始化数据库
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    # 测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin', '--username',
                                          'leon', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().user_name, 'leon')
        self.assertTrue(User.query.first().validate_password('123'))

    # 测试更新管理员账户
    def test_admin_command_update(self):
        # 使用 args 参数给出完整的命令参数列表
        result = self.runner.invoke(args=['admin', '--username',
                                          'Leon', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().user_name, 'Leon')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()
