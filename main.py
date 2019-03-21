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


#@app.errorhandler(500)
#def server_error(e):
#    # Log the error and stacktrace.
#    logging.exception('An error occurred during a request.')
#    return 'An internal error occurred.', 500


if __name__ == '__main__':
    app.run(debug=True)
