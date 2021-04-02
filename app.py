import json
from ttn_api import scheduleDownlink, Uplinks
from flask import Flask, render_template, make_response, request, send_file
from werkzeug.serving import run_simple
import time
import base64
import codecs
from mongo_db_api import storeData, getData
import os

app = Flask(__name__)

# renders main site, gets called when starting the application
@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('index.html')

# gathers uplinks from TTN and parses it for front end
@app.route('/data', methods=["GET", "POST"])
def data():
    # calls for new payload
    newPayload = Uplinks()

    # loops through payload and formats it to json
    unparsedResponse = []
    for i in range(len(newPayload.ids)):
        jsonToAppend = {"time": newPayload.timestamps[i] * 1000,
                        "temperature": newPayload.temperatures[i],
                        "altitude": newPayload.altitudes[i],
                        "battery": newPayload.batteries[i],
                        "pressure": newPayload.pressures[i],
                        "datarate": newPayload.dataRates[i],
                        "plot_this": 1}
        unparsedResponse.append(jsonToAppend)

    # json to response
    response = make_response(json.dumps(unparsedResponse))
    response.content_type = 'application/json'

    # sends data to be stored to data base
    storeData(newPayload)
    # sends response to front end
    return response

# lets user downloads n-number of data in csv
@app.route('/download', methods=["GET", "POST"])
def download():
    # button was pressed
    if request.method == 'POST':
        # creates csv file with n-number of data
        n = request.form['numOfDownloads']
        getData(int(n))

        path = "data.csv"
        # sends file to user
        return send_file(path, as_attachment=True)

# gets called when user wants to issue downlink to TTN
@app.route('/send', methods=['GET', 'POST'])
def send():
    # button was pressed
    if request.method == 'POST':
        # checks user entered password and if it matches the right password
        pwEntered = request.form['password']
        if pwEntered == os.environ.get("POST_PASSWORD"):
            # if the password was correct, prepares downlink to be scheduled
            led_color = request.form['led_color']
            if led_color == "red":
                rgbStr = "00"
            if led_color == "green":
                rgbStr = "01"
            if led_color == "blue":
                rgbStr = "02"
            if led_color == "purple":
                rgbStr = "03"
            if led_color == "yellow":
                rgbStr = "04"
            if led_color == "no":
                rgbStr = "05"

            payloadStr = ""
            drEntered = request.form['dr_sf']
            if drEntered == 'no':
                payloadStr = "06" + rgbStr
            if drEntered == 'dr5':
                payloadStr = "05" + rgbStr
            if drEntered == 'dr4':
                payloadStr = "04" + rgbStr
            if drEntered == 'dr3':
                payloadStr = "03" + rgbStr
            if drEntered == 'dr2':
                payloadStr = "02" + rgbStr
            if drEntered == 'dr1':
                payloadStr = "01" + rgbStr
            if drEntered == 'dr0':
                payloadStr = "00" + rgbStr

            # encodes the message and sends it to TTN
            payloadEncoded = codecs.encode(codecs.decode(payloadStr, 'hex'), 'base64').decode()
            scheduleDownlink(payloadEncoded)

    # refreshes the page, after finishing posting
    return render_template('index.html')

# runs when starting the app
if __name__ == '__main__':
    app.run(debug=True)
