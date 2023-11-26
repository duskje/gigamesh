import os.path

from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)

all_setlists = ['Música Electrónica', 'Rancheras', 'Funk Carioca']

@app.route('/new_setlist', methods=['POST', 'OPTIONS'])
def new_setlist():
    """ Create a new setlist """

    if request.method == 'POST':
        all_setlists.append(request.json.get('new_setlist'))

        return 'OK', 200


@app.route('/setlists', methods=['GET'])
def setlists():
    """ Get all registered setlists """

    return {'result': all_setlists}


@app.route('/add_song', methods=['POST'])
def add_song():
    pass


@app.route('/delete_song', methods=['POST'])
def delete_song():
    pass


if __name__ == '__main__':
    os.path.isfile()
    app.run()
