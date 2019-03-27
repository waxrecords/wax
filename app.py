from flask import Flask, render_template, request, jsonify
import json
import requests
from beeprint import pp
import requests_cache
import random
from itertools import zip_longest
import os
import datetime


app = Flask(__name__, instance_relative_config=False)
app.config.from_object('config')
app.config.from_pyfile('config.py')

tfl_status_template = 'https://api.tfl.gov.uk/Line/Mode/tube/Status?app_key={TFL_API_KEY}&app_id={TFL_API_ID}'

tfl_lines_url = tfl_status_template.format(
    TFL_API_KEY=app.config['MY_TFL_KEY'], TFL_API_ID=app.config['MY_TFL_ID'])


with open('static/messages/good.txt') as input_file:
    good = [line.strip() for line in input_file]
with open('static/messages/medium.txt') as input_file:
    medium = [line.strip() for line in input_file]
with open('static/messages/bad.txt') as input_file:
    bad = [line.strip() for line in input_file]


lineid = ['bakerloo', 'central', 'circle', 'district', 'hammersmith-city',
          'jubilee', 'metropolitan', 'northern', 'piccadilly', 'victoria', 'waterloo-city']

lines = ["Bakerloo", "Central", "Circle", "District", "H'Smith & City", "Jubliee",
         "Metropolitan", "Northern", "Piccadilly", "Victoria", "Waterloo & City"]

status = [""] * 11
addstatus = [""] * 11
hideadd = [""] * 11
night = [""] * 11
hidenight = [""] * 11
icons = [""] * 11
addicons = [""] * 11
nighticon = [""] * 11

closed = ["Service Closed"]


def nightTube():

    # get the current date and time
    d = datetime.datetime.now()

    # return true if weekend between 23:00 and 05:00, otherwise return false
    if ((d.isoweekday() in range(5, 7)) and (d.hour not in range(5, 23))):

        return True

    return False


def update():

    data = requests.get(tfl_lines_url)
    linesdata = data.json()

    i = 0
    x = 0

    while i < len(linesdata):
        status[i] = (linesdata[i]['lineStatuses']
                     [0]['statusSeverityDescription'])
        try:
            addstatus[i] = (linesdata[i]['lineStatuses']
                            [1]['statusSeverityDescription'])
            pp(addstatus[i])
        except:
            pass

        try:
            night[i] = (linesdata[i]['serviceTypes'][1]['name'])
        except:
            pass

        i += 1

    while x < len(lines):

        if not (nightTube()):
            hidenight[x] = "hide"

        elif (night[x] == "Night") and (nightTube()):
            nighticon[x] = "fas fa-moon"

        if addstatus[x] == "":
            hideadd[x] = "hide"

        elif addstatus[x] in good:
            addicons[x] = "fas fa-check"

        elif addstatus[x] in medium:
            addicons[x] = "fas fa-exclamation"

        elif addstatus[x] in bad:
            addicons[x] = "fas fa-exclamation-triangle"

        if status[x] in good:
            icons[x] = "fas fa-check"

        elif status[x] in medium:
            icons[x] = "fas fa-exclamation"

        elif status[x] in bad:
            icons[x] = "fas fa-exclamation-triangle"

        elif status[x] in closed:
            icons[x] = "fas fa-times"

        x += 1


@app.route('/', methods=['GET'])
@app.route('/tflstatus', methods=['GET'])
def tflstatus():

    update()

    return render_template('index.html', zip=zip, lines=lines, status=status, lineid=lineid, icons=icons, addstatus=addstatus, addicons=addicons, hideadd=hideadd, nighticon=nighticon, hidenight=hidenight)


@app.route('/tflstatus/<linesid>')
def linepage(linesid):

    y = 0

    while y < len(lines):
        if lineid[y] == linesid:
            line = lines[y]
            statuses = status[y]

        y += 1

    return render_template('status.html', zip=zip, line=line, status=statuses, lineid=linesid)


@app.errorhandler(404)
def page_not_found(e):

    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(port=8080, debug=True, ssl_context=(
        'instance/cert.pem', 'instance/key.pem'))
