from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# 创建一个简单的SQLite数据库
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    c.execute("INSERT INTO users (username, password) VALUES ('user1', 'password123')")
    conn.commit()
    conn.close()

init_db()

# 漏洞1: SQL注入
def get_user(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # 漏洞: 用户输入直接拼接到SQL查询中
    c.execute(f"SELECT * FROM users WHERE username = '{username}'")
    user = c.fetchone()
    conn.close()
    return user

# 漏洞2: XSS
@app.route('/')
def index():
    return render_template_string('''
        <form action="/login" method="post">
            用户名: <input type="text" name="username"><br>
            密码: <input type="password" name="password"><br>
            <input type="submit" value="登录">
        </form>
        <div>{{ message|safe }}</div>
    ''')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = get_user(username)

    if user and user[1] == password:
        return f"登录成功！欢迎，{username}！"
    else:
        # 漏洞: 将错误信息直接显示在页面上，可能导致XSS
        return index() + f"<script>alert('用户名或密码错误');</script>"

# 漏洞3: 不安全的文件上传
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "没有文件上传"
    
    file = request.files['file']
    # 漏洞: 没有验证文件类型和文件名
    file.save(f"./uploads/{file.filename}")
    return "文件上传成功！"

if __name__ == '__main__':
    app.run(debug=True)
