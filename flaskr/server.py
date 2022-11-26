from flask import Flask, render_template, Response
from threading import Lock
import cv2



app = Flask(__name__)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


def start(debug=False):
    app.run(debug=debug)

if __name__ == "__main__": # For rapid testing. (Yes, by running the file.)
    start(debug=True)