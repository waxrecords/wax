from flask import Flask, render_template, request, jsonify, redirect, url_for
from itertools import zip_longest
from beeprint import pp
import requests_cache
import requests
import datetime
import json
import os

# cache data request from TFL API call for 1 minute
# set relatively low as travel updates change regularly
requests_cache.install_cache(
    'tfl_api_cache', backend='sqlite', expire_after=60)

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# template we will later format to call TFL API
tfl_status_template = 'https://api.tfl.gov.uk/Line/Mode/{TFL_MODE}/Status?app_key={TFL_API_KEY}&app_id={TFL_API_ID}'

# creates a list for good, medium and bad responses from a txt file
# used a txt file here to easily change them around
# the txt files contain typical responses from TFL e.g. Major Delays
# a different CSS class value will be added based on if response is in good, medium or bad
with open('static/messages/good.txt') as input_file:
    good = [line.strip() for line in input_file]
with open('static/messages/medium.txt') as input_file:
    medium = [line.strip() for line in input_file]
with open('static/messages/bad.txt') as input_file:
    bad = [line.strip() for line in input_file]

# list of the different tube lines, ids and display names
# could have retrieved these via TFL API but was easier for editing display names e.g. Hammersmith & City => H'Smith & City
lineid = ['bakerloo', 'central', 'circle', 'district', 'hammersmith-city',
          'jubilee', 'metropolitan', 'northern', 'piccadilly', 'victoria', 'waterloo-city']
lines = ["Bakerloo", "Central", "Circle", "District", "H'Smith & City", "Jubliee",
         "Metropolitan", "Northern", "Piccadilly", "Victoria", "Waterloo & City"]

# initialises empty lists for the tube lines various status'
# these will be populated with the respones from TFL API
# could have implemented better, packing everything into a JSON (ran out of time)
# as we have a fixed number of tube lines (11) we can use while operators to populate each list with the correct item e.g. bakerloo is always status[1], addstatus[1], etc.

status = [""] * 11  # TFL status
icons = [""] * 11   # we will add a CSS class value here later
addstatus = [""] * 11   # TFL additional status'
addicons = [""] * 11    # if there are additional status' we will add a CSS class value here later
hideadd = [""] * 11  # if there are no additional status' we will add a hide CSS class value here later
night = [""] * 11   # TFL night service
nighticon = [""] * 11   # if line has night service we will add a CSS class value here later
hidenight = [""] * 11   # if line has no night service we will add a hide CSS class value here later
closed = ["Service Closed"]   # if service is closed we will add a CSS class value here later

# if within night tube hours e.g. friday - saturday between 23:00 and 05:00 returns true
def nightTube():

    # get the current date and time
    d = datetime.datetime.now()

    # return true if weekend between 23:00 and 05:00, otherwise return false
    if ((d.isoweekday() in range(5, 7)) and (d.hour not in range(5, 23))):

        return True

    return False

# queries the TFL api for all the line information for given mode e.g. tube
def update(mode):

    # formats the URL template defined earlier, adding API key, API id and mode
    tfl_url = tfl_status_template.format(
        TFL_MODE=mode, TFL_API_KEY=app.config['MY_TFL_KEY'], TFL_API_ID=app.config['MY_TFL_ID'])

    # makes request
    data = requests.get(tfl_url)

    # if mode is set to tube then return as tubedata, otherwise return as otherdata
    # ideally would have various scenarious here e.g. dlr, overground, etc.
    # to save time we are grouping everything that isn't tube as other
    if mode == 'tube':
        tubedata = data.json()
        return(tubedata)
    else:
        otherdata = data.json()
        return(otherdata)

# extracts the status, additional status and night service data from tubedata for each line
def getdata(x):

    i = 0

    while i < len(x):
        status[i] = (x[i]['lineStatuses']
                     [0]['statusSeverityDescription'])
        try:
            addstatus[i] = (x[i]['lineStatuses']
                            [1]['statusSeverityDescription'])
        except:
            pass

        try:
            night[i] = (linesdata[i]['serviceTypes'][1]['name'])
        except:
            pass

        i += 1


def addicon():

    x = 0

    while x < len(lines):

        if not (nightTube()):
            hidenight[x] = "hide"

        elif (night[x] == "Night") and (nightTube()):
            nighticon[x] = "fas fa-moon"

        if status[x] in good:
            icons[x] = "fas fa-check"

        elif status[x] in medium:
            icons[x] = "fas fa-exclamation"

        elif status[x] in bad:
            icons[x] = "fas fa-exclamation-triangle"

        elif status[x] in closed:
            icons[x] = "fas fa-times"

        if addstatus[x] == "":
            hideadd[x] = "hide"

        elif addstatus[x] in good:
            addicons[x] = "fas fa-check"

        elif addstatus[x] in medium:
            addicons[x] = "fas fa-exclamation"

        elif addstatus[x] in bad:
            addicons[x] = "fas fa-exclamation-triangle"

        x += 1


@app.route('/')
def redir():
    return redirect(url_for('tflstatus'))


@app.route('/tube/', methods=['GET'])
def tflstatus():

    getdata(update('tube'))
    addicon()

    # because there was no time to repack the data into a single json we have to bring it all across seperately, as well as the zip function to join it all
    return render_template('index.html', zip=zip, lines=lines, status=status, lineid=lineid, icons=icons, addstatus=addstatus, addicons=addicons, hideadd=hideadd, nighticon=nighticon, hidenight=hidenight)


@app.route('/tube/<linesid>')
def linepage(linesid):

    getdata(update('tube'))
    addicon()

    y = 0

    # checks if the url parameter is an existing tube line, returns status.html for that line if it is and 404.html if not
    if linesid not in linesid:
        exit
    else:
        while y < len(lines):
            if lineid[y] == linesid:
                line = lines[y]
                statuses = status[y]
                return render_template('status.html', zip=zip, line=line, status=statuses, lineid=linesid)
            y += 1

    return render_template('404.html'), 404


@app.errorhandler(404)
@app.errorhandler(500)
def page_not_found(e):

    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(port=8080, debug=True)
