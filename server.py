import io
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import psycopg2
from psycopg2.extras import RealDictCursor
import os
# Auth0 imports
from urllib.parse import quote_plus, urlencode


from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')


conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET')
###AUTH STUFF ###

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route('/login/')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect(url_for('showList'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + os.environ.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("showList", _external=True),
                "client_id": os.environ.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


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
    name = None
    if "name" in session:
        name = session["name"]
    return render_template('hello.html', guests=guests, name=name, session=session.get('user'))

@app.route('/display')
def display():
    return render_template("display.html")

@app.route('/submit', methods=['POST'])
def submit():
    guest_name = request.form['fname']
    guest_message = request.form['message']
    file = request.files["image"]
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO session_6 (name, message) VALUES (%s, %s)",
                (guest_name, guest_message)
            )
            conn.commit()
            cur.execute(
                "INSERT INTO session_6_images (content) VALUES (%s) returning id;",
                (file.read(),)
            )
            conn.commit()
        conn.close()
    return redirect(url_for('showList'))

@app.route('/<name>')
def hello(name=None):
    if name:
        session["name"] = name
    return render_template('hello.html', name=name)

@app.route('/images/<int:image_id>')
def get_image(image_id):
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM session_6_images where id=%s", (image_id,))
        image_row = cur.fetchone() 
        stream = io.BytesIO(image_row["content"])
        return send_file(stream, download_name="image")