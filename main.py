"""
MixPlayer Application

Routes:

/ - A list of all mixes
/mix/<name> - A page with a single mix.
"""

from flask import Flask, render_template
from models import MixFile

app = Flask(__name__)


@app.route('/mix/<mixname>')
def mix(mixname):
    return render_template(
        'singlemix.html', 
        mixes=list(MixFile.all(filter=mixname))
    )


@app.route('/')
def index():
    return render_template(
        'playlist.html', 
        mixes=list(sorted(MixFile.all(), key=lambda k: k.date, reverse=True))
    )
