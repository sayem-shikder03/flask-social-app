from flask import Flask, render_template, request, redirect, session
import sqlite3, os



app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database init
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL
                        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS posts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            content TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(id)
                        )''')

@app.route('/')
def home():
    if 'user_id' in session:
        with sqlite3.connect('users.db') as conn:
            posts = conn.execute('SELECT posts.content, users.username FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.id DESC').fetchall()
        return render_template('feed.html', posts=posts)
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # plain password save
        with sqlite3.connect('users.db') as conn:
            try:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                return redirect('/login')
            except sqlite3.IntegrityError:
                return 'Username already exists!'
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and user[2] == password:
                session['user_id'] = user[0]
                session['username'] = user[1]
                
                if user[1] == 'admin':
                    return redirect('/admin')
                else:
                    return redirect('/')

            else:
                return 'Invalid credentials!'
    return render_template('login.html')


@app.route('/admin')
def admin():
    if session.get('username') == 'admin':  # Only admin can access
        with sqlite3.connect('users.db') as conn:
            users = conn.execute('SELECT id, username, password FROM users').fetchall()
        return render_template('admin.html', users=users)
    return 'Unauthorized access!'


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/login')


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('username') == 'admin':
        with sqlite3.connect('users.db') as conn:
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        return redirect('/admin')
    return 'Unauthorized access!'



@app.route('/post', methods=['POST'])
def post():
    if 'user_id' in session:
        content = request.form['content']
        with sqlite3.connect('users.db') as conn:
            conn.execute('INSERT INTO posts (user_id, content) VALUES (?, ?)', (session['user_id'], content))
        return redirect('/')
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

