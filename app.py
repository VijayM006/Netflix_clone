import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import requests

vj = Flask(__name__, static_url_path=os.getenv('STATIC_URL_PATH', '/static'))
vj.secret_key = os.getenv('SECRET_KEY', 'Vijay@006')
vj.config["MYSQL_HOST"] = os.getenv('MYSQL_HOST', 'localhost')
vj.config["MYSQL_USER"] = os.getenv('MYSQL_USER', 'root')
vj.config["MYSQL_PASSWORD"] = os.getenv('MYSQL_PASSWORD', 'Vijay@006')
vj.config["MYSQL_DB"] = os.getenv('MYSQL_DB', 'netflix')

mysql = MySQL(vj)

api_key = os.getenv('TMDB_API_KEY', 'fa348f2691b845728af37d2a4c57e720')
base_url = 'https://api.themoviedb.org/3'

you_key = os.getenv('YOUTUBE_API_KEY', 'AIzaSyBfjA46qEqHeq7M1t8xpTTbeHIGJ_71JYo')
you_base_url = 'https://www.googleapis.com/youtube/v3'


def search_youtube_trailer(query):
    url = f'{you_base_url}/search'
    params = {'key': you_key,'q': query,'part': 'snippet','maxResults': 1,'type': 'video'}
    response = requests.get(url, params=params)
    items = response.json().get('items', [])
    if items:
        return items[0]['id']['videoId']
    return None

def fetch_movie_details(movie_id):
    url = f'{base_url}/movie/{movie_id}'
    params = {'api_key': api_key}
    response = requests.get(url, params=params)
    return response.json()


@vj.route("/a")
def home():
    response = requests.get(f'{base_url}/movie/popular',params={'api_key':api_key})
    data = response.json()
    movies = data.get('results', [])
    res=requests.get(f'{base_url}/movie/top_rated',params={'api_key':api_key})
    datas=res.json()
    topi=datas.get('results',[])


    return render_template('home.html', movies=movies,tops=topi)


@vj.route('/')
def index():
    return render_template("index.html")

@vj.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM netsignup WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()

        if user:
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template("login.html")

@vj.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO netsignup (email, password) VALUES (%s, %s)", (email, password))
        mysql.connection.commit()
        cur.close()
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template("signup.html")

@vj.route("/movie/<int:movie_id>")
def movie(movie_id):
    movie_data = fetch_movie_details(movie_id)
    trailer_id = search_youtube_trailer(movie_data['title'] + ' trailer')
    return render_template('movie.html', movie=movie_data, trailer_id=trailer_id)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    vj.run(debug=True, host='0.0.0.0', port=port)
