from flask import Flask
from flask import request
import sys
import pickle
from datetime import datetime

app = Flask(__name__)


@app.route("/DHTPost", methods=["POST"])
def postJsonHandler():
    content = request.json
    # print(content)
    HandleLogging(content)
    return "Data Posted"


itr = 0


def saveFile(data):
    global itr
    with open(f"dat/DHT_Data_{itr}.pickle", "wb") as file:
        pickle.dump(data, file)
    if len(data) % 1000 == 0:
        itr += 1
        itr %= 5


def HandleLogging(json):

    temprature = json["temprature"]
    humidity = json["humidity"]
    temprature_F = json["temprature_F"]
    now = datetime.now()

    print(
        f"Temprature is {temprature} C and Humidity is {humidity} at {now} also fahrenheit is {temprature_F}"
    )
    data.append((now, temprature, humidity))
    saveFile(data)


data = []


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="7000", debug=False)
