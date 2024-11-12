from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Dùng để hiển thị thông báo

# Kết nối tới cơ sở dữ liệu
def connect_to_db():
    try:
        conn = psycopg2.connect(
            user='postgres',
            password='123456',
            host='localhost',
            dbname='tung'
        )
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        conn = connect_to_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (user, password))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if user_data:
                return redirect(url_for('menu'))
            else:
                flash('Invalid username or password.')
                return redirect(url_for('login'))
        else:
            flash('Failed to connect to the database.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username and password:
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                    conn.commit()
                    flash('Registration successful! Please log in.')
                    return redirect(url_for('login'))
                except Exception as e:
                    flash(f"Error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            else:
                flash('Failed to connect to the database.')
        else:
            flash('Please fill in all fields.')

    return render_template('register.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        conn = connect_to_db()

        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO students (name, email, age) VALUES (%s, %s, %s)", (name, email, age))
                conn.commit()
                flash('Student added successfully!')
                return redirect(url_for('menu'))
            except Exception as e:
                flash(f"Error: {e}")
            finally:
                cursor.close()
                conn.close()

    return render_template('add_student.html')

@app.route('/search_student', methods=['GET', 'POST'])
def search_student():
    students = []
    if request.method == 'POST':
        name = request.form['name']
        conn = connect_to_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE name ILIKE %s", (f"%{name}%",))
            students = cursor.fetchall()
            cursor.close()
            conn.close()

    return render_template('search_student.html', students=students)

@app.route('/remove_student', methods=['GET', 'POST'])
def remove_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        conn = connect_to_db()

        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            result = cursor.fetchone()
            if result:
                cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
                conn.commit()
                flash('Student deleted successfully!')
            else:
                flash('Student not found.')
            cursor.close()
            conn.close()

    return render_template('remove_student.html')

if __name__ == '__main__':
    app.run(debug=True)
