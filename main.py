import io
import sys
import re
import logging

from flask import Flask, render_template

from models import MixFile

app = Flask(__name__)


@app.route('/mix/<mixname>')
def mix(mixname):
    return render_template('singlemix.html', mixes=MixFile.all(filter=mixname))


@app.route('/')
def index():
    mixes = list(MixFile.all())
    mixes = sorted(mixes, key=lambda k: k.date, reverse=True)
    return render_template('playlist.html', mixes=mixes)


if __name__ == '__main__':
    app.run(debug=True)
