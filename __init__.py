#-*- coding: utf-8 -*-

import sqlite3
import os
from flask import *

app = Flask(__name__)

# 生成秘钥
app.secret_key = os.urandom(24)
print app.secret_key

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database/eh.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def welcome():
    if session.get('logged_in'):
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

# 简化sqlite3的查询方式。
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 检查数据库，先略过。
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['logged_in'] = True;
        user = query_db('select * from user where username = ?', request.form['username'], one=True)
        if user is None:
            print '没有这个用户！'
        else:
            if reque.form['password'] != user[password]:
                print '密码错误！'
        # g.db.execute('insert into user (username, password) values (?, ?)', [request.form['username'], request.form['password']])
        # g.db.commit()
        return redirect(url_for('welcome'));
    return render_template('welcome.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/hello')
def hello():
    return 'Hello World!!!'

@app.route('/1/<username>')
def show_user_profile(username):
    return '你好 %s' % username

@app.route('/1/<int:post_id>')
def show_post(post_id):
    return '你投送了 %d' % post_id

@app.route('/1/about')
def show_about_page():
    return 'This is the ABOUT page.'

@app.route('/2/')
def show_location():
    return render_template('index.html')

@app.route('/3/')
def show_helloHTML():
    return render_template('hello.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == "__main__":
    app.run(debug=True)