import sqlite3
from flask import Flask, render_template, redirect, request, url_for, flash
from werkzeug.exceptions import abort
from random import choice
from string import ascii_uppercase


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def generate_short_url(url):
    s = ''.join(choice(ascii_uppercase) for i in range(6)).lower()
    conn = get_db_connection()
    pair = conn.execute('SELECT * FROM urls WHERE short_url = ?',
                        (s,)).fetchone()
    while pair is not None:
        s = ''.join(choice(ascii_uppercase) for i in range(6)).lower()
    conn.close()
    return s


def get_true_url(short_url):
    conn = get_db_connection()
    pair = conn.execute('SELECT * FROM urls WHERE short_url = ?',
                        (short_url,)).fetchone()
    if pair is None:
        ### AND ADD TO DATABASE (or not)
        return "Error"
        abort(404)

    print("true_url = ", pair['url'])
    conn.close()
    return pair


app = Flask(__name__)


@app.route('/<string:short_url>')
def post(short_url):
    pair = get_true_url(short_url)
    return redirect(pair['url'])


lst_url = ''


@app.route('/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        url = request.form['url']
        short_url = request.form['short_url']

        if len(url) == 0:
            flash('Url is required!')
        else:
            if len(short_url) == 0:
                short_url = generate_short_url(url)
            print('SHORT_URL = ', short_url)
            conn = get_db_connection()
            conn.execute('INSERT INTO urls (url, short_url) VALUES (?, ?)',
                         (url, short_url))
            conn.commit()
            conn.close()
            global lst_url
            lst_url= short_url
        return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/success')
def index():
    global lst_url
    return render_template('index.html', url='http://127.0.0.1:5000/' + lst_url)


if __name__ == '__main__':
    app.run()
