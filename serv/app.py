import os
import datetime
from flask import Flask, jsonify, redirect, request

WEB_APP_DIR = os.path.dirname(__file__)
app = Flask(__name__)


@app.route('/')
def index():
    return "ZBS"


@app.route('/api/events')
def get_events():
    events = [
        {
            'date': datetime.datetime.now(),
            'human': 0,
            'cam': 0,
        },
        {
            'date': datetime.datetime.now(),
            'human': 0,
            'cam': 1
        },
    ]
    return jsonify(events)
    if 'X-File-Name' in request.headers:
        return jsonify({"url": "/{}".format(new_uri)})
    else:
        return redirect("/{}".format(new_uri), code=302)


@app.route('/api/people')
def get_people():
    people = [
        {
            'id': 0,
            'data': {
                'name': 'Pidor',
                'surname': 'Pidoryan',
                'sex': 'male',
                'other': 'Vsyakaya xyunya'
            },
        },
    ]
    return jsonify(people)


@app.route('/api/rooms')
def get_rooms():
    rooms = [
        {
            'id': 0,
            'cam_in': 0,
            'cam_out': 1,
        },
    ]
    return jsonify(rooms)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
