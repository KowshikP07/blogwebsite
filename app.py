import sqlite3
import bcrypt
import os
from flask import Flask, render_template, request, redirect, session, url_for, flash, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = 'database/blog.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create required tables
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        mobile_number TEXT NOT NULL,
                        password BLOB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS blogs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        category TEXT,
                        image TEXT,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')

    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['Name']
        username = request.form['Username']
        email = request.form['Email']
        mobile_number = request.form['Mobile_Number']
        password = request.form['Password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO users (name, username, email, mobile_number, password) 
                              VALUES (?, ?, ?, ?, ?)''',
                           (name, username, email, mobile_number, hashed_password))
            conn.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or Email already exists!', 'danger')
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        next_page = request.args.get('next', '/')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name'] 
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        image = request.files.get('image')
        user_id = session.get('user_id')
        image_filename = None

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image.save(image_path)

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(''' 
                INSERT INTO blogs (user_id, title, content, category, image) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, title, content, category, image_filename))
            conn.commit()
            conn.close()
            flash("Blog posted successfully!", "success")
            return redirect('/profile')
        except sqlite3.Error as e:
            print("SQLite Error:", e)
            flash("An error occurred while saving your blog.", "danger")

    return render_template('upload.html')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')

    if user_id:
        blogs = get_user_blogs(user_id)
        return render_template('profile.html', blogs=blogs)
    else:
        return redirect(url_for('login'))

def get_user_blogs(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blogs WHERE user_id = ?', (user_id,))
    blogs = cursor.fetchall()
    conn.close()
    return blogs

@app.route('/blog')
def blog():
    conn = get_db()
    blogs = conn.execute('SELECT * FROM blogs').fetchall()
    conn.close()
    return render_template('blog.html', blogs=blogs)

@app.route('/blog_details/<int:blog_id>')
def blog_details(blog_id):
    conn = get_db()
    cursor = conn.execute('''SELECT blogs.*, users.username FROM blogs 
                              JOIN users ON blogs.user_id = users.id 
                              WHERE blogs.id = ?''', (blog_id,))
    blog = cursor.fetchone()
    conn.close()

    if blog is None:
        abort(404)
    return render_template('blog_details.html', blog=blog)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect('/login')

@app.route('/debug-session')
def debug_session():
    return f"Session data: {dict(session)}"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/write')
def write():
    return render_template('write.html')

@app.route('/blogform')
def blogform():
    return render_template('blogform.html')
@app.route('/categories')
def categories():
    return render_template('categories.html')  # make sure categories.html exists

create_tables()

if __name__ == '__main__':
    app.run(debug=True)
