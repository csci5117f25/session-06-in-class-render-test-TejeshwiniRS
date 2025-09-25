from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')


conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()


app = Flask(__name__)
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        return None


@app.route('/', methods=["GET", "POST"])
def showList():
    conn = get_db_connection()
    guests = []
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, message FROM session_6")
            guests_all = cur.fetchall()
            for row in guests_all:
                guests.append({'name': row[0], 'message': row[1]})
        conn.close()
    return render_template('hello.html', guests=guests)

@app.route('/submit', methods=['POST'])
def submit():
    guest_name = request.form['fname']
    guest_message = request.form['message']
    
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO session_6 (name, message) VALUES (%s, %s)",
                (guest_name, guest_message)
            )
            conn.commit()
        conn.close()
    return redirect(url_for('showList'))

@app.route('/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)