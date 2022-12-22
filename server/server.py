from flask import Flask, render_template, url_for, redirect
from threading import Lock

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))

def start(debug=False):
    app.run(debug=debug)

if __name__ == "__main__":
    start(debug=True)