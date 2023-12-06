#!usr/bin/python3

# import libraries
from Adafruit_IO import Client, Feed, RequestError
from flask import Flask, request
import urllib, requests
import time
import threading
from enum import Enum
import os

# create flask app
app = Flask(__name__)

# define the secrets
secretKeys = Enum(
    "secretKeys",
    [
        "IO_USERNAME",
        "IO_KEY",
        "Telegram_automation_bot_token",
        "Telegram_automation_chat_id",
        "Telegram_bot_chat_id",
        "IO_HUMIDITY_FEED",
        "IO_HUMIDITY_SETPOINT",
        "IO_HUMIDITY_BUFFER",
        "IO_TEMPRATURE_FEED",
        "IO_TEMPRATURE_SETPOINT",
        "IO_TEMPRATURE_BUFFER",
        "IO_TEMPRATURE_FAHRENHEIT_FEED",
        "IO_HEAT_INDEX_FEED",
        "IO_HEAT_INDEX_FAHRENHEIT_FEED",
        "IO_UPDATE_TRIGGER_FEED",
        "IO_UPDATE_TRIGGER",
    ],
)

typeDefs = {}
typeDefs[secretKeys.IO_USERNAME.name] = str
typeDefs[secretKeys.IO_KEY.name] = str
typeDefs[secretKeys.Telegram_automation_bot_token.name] = str
typeDefs[secretKeys.Telegram_automation_chat_id.name] = int
# typeDefs[secretKeys.Telegram_bot_chat_id.name] = int
typeDefs[secretKeys.IO_HUMIDITY_FEED.name] = str
typeDefs[secretKeys.IO_HUMIDITY_SETPOINT.name] = str
typeDefs[secretKeys.IO_HUMIDITY_BUFFER.name] = str
typeDefs[secretKeys.IO_TEMPRATURE_FEED.name] = str
typeDefs[secretKeys.IO_TEMPRATURE_SETPOINT.name] = str
typeDefs[secretKeys.IO_TEMPRATURE_BUFFER.name] = str

typeDefs[secretKeys.IO_UPDATE_TRIGGER_FEED.name] = str
typeDefs[secretKeys.IO_UPDATE_TRIGGER.name] = int


class Device:
    def __init__(
        self,
        name,
        triggerOnURL,
        triggerOffURL,
        valueKey,
        setpointKey,
        triggerBufferKey,
        isInvertedControl,
        warningMultiplier,
        warningDelay,
    ):
        self.name = name

        self.triggerOnURL = triggerOnURL
        self.triggerOffURL = triggerOffURL

        self.state = False

        self.value = 0
        self.valueKey = valueKey
        self.setpoint = 0
        self.setpointKey = setpointKey
        self.triggerBuffer = 0
        self.triggerBufferKey = triggerBufferKey

        self.isInvertedControl = isInvertedControl

        self.AIO = None
        self.SendMessage = None

        self.warningTime = 0
        self.warningDelay = warningDelay
        self.warningMultiplier = warningMultiplier

        self.update()

    def turnOn(self):
        if not self.state:
            self.state = True

            # send request to turn on
            print(f"Turning on {self.name}")

            x = requests.get(self.triggerOnURL)
            print(f"Response from {self.name} : {x.status_code} -> {x.text}")

    def turnOff(self):
        if self.state:
            self.state = False

            # send request to turn off
            print(f"Turning off {self.name}")

            x = requests.get(self.triggerOffURL)
            print(f"Response from {self.name} : {x.status_code} -> {x.text}")

    def setup(self, AIO, sendMessage):
        self.AIO = AIO
        self.SendMessage = sendMessage

        print(f"Setup for {self.name} complete")

        self.state = True
        self.turnOff()

    def update(self):
        if (
            self.AIO is None
            or self.valueKey == ""
            or self.setpointKey == ""
            or self.triggerBufferKey == ""
        ):
            print(f"Setup for {self.name} incomplete")
            return

        # get the values from Adafruit IO
        self.value = float(self.AIO.receive(self.valueKey).value)
        self.setpoint = float(self.AIO.receive(self.setpointKey).value)
        self.triggerBuffer = float(self.AIO.receive(self.triggerBufferKey).value)

        # check if the device should be turned on or off
        if self.isInvertedControl:
            if self.value < self.setpoint - self.triggerBuffer:
                self.turnOn()
            elif self.value > self.setpoint + self.triggerBuffer:
                self.turnOff()
            if self.value < self.setpoint - self.warningMultiplier * self.triggerBuffer:
                if time.time() - self.warningTime > self.warningDelay:
                    self.SendMessage(
                        f"{self.name} is below setpoint by {self.value - self.setpoint}. Check if the device is working properly."
                    )
                    self.warningTime = time.time()
        else:
            if self.value > self.setpoint + self.triggerBuffer:
                self.turnOn()
            elif self.value < self.setpoint - self.triggerBuffer:
                self.turnOff()
            if self.value > self.setpoint + self.warningMultiplier * self.triggerBuffer:
                if time.time() - self.warningTime > self.warningDelay:
                    self.SendMessage(
                        f"{self.name} is above setpoint by {self.value - self.setpoint}. Check if the device is working properly."
                    )
                    self.warningTime = time.time()

        self.status()

    def status(self):
        print(
            f"{self.name} : state -> {self.state} | value -> {self.value} | setpoint -> {self.setpoint} | triggerBuffer -> {self.triggerBuffer} | isInvertedControl -> {self.isInvertedControl} | timeSinceWarning -> {time.time() - self.warningTime}"
        )


class Thermostat:
    def __init__(self, params):
        self.AIO_USERNAME = params[secretKeys.IO_USERNAME.name]
        self.AIO_KEY = params[secretKeys.IO_KEY.name]
        self.AIO = Client(self.AIO_USERNAME, self.AIO_KEY)

        self.Telegram_Bot_Token = params[secretKeys.Telegram_automation_bot_token.name]
        self.Telegram_Chat_ID = params[secretKeys.Telegram_automation_chat_id.name]

        self.devices = []
        self.isUpdate = True
        self.updateTriggerKey = params[secretKeys.IO_UPDATE_TRIGGER_FEED.name]
        self.updateTrigger = params[secretKeys.IO_UPDATE_TRIGGER.name]

        self.warningTime = time.time()
        self.warningDelay = 60 * 5  # 5 minutes

        self.updateThread = threading.Thread(target=self.updateLoop, daemon=True)

        self.feeds = self.AIO.feeds()
        for f in self.feeds:
            print(f"Feed found : {f} with value -> {self.AIO.receive(f.key).value}")

    def run(self):
        self.updateThread.start()

    def addDevice(self, device):
        self.devices.append(device)

    def sendTelegramMessage(self, message):
        url = f"https://api.telegram.org/bot{self.Telegram_Bot_Token}/sendMessage?chat_id={self.Telegram_Chat_ID}&text={message}"
        x = requests.get(url)
        print(f"Response from Telegram : {x.status_code} -> {x.text}")

    def getFeedValue(self, key):
        for feed in self.feeds:
            if feed.key == key:
                val = self.AIO.receive(feed.key).value
                return val
        return None

    def updateLoop(self):
        while True:
            try:
                if time.time() - self.warningTime > self.warningDelay:
                    self.sendTelegramMessage("Thermostat is Down.")
                if (
                    self.isUpdate
                    or int(float(self.getFeedValue(self.updateTriggerKey)))
                    == self.updateTrigger
                ):
                    print(f"*" * 20)
                    print(f"Updating Thermostat")
                    for device in self.devices:
                        device.update()
                    print(f"/" * 20)
                    self.isUpdate = False
                    self.AIO.send_data(self.updateTriggerKey, 0)
                    self.warningTime = time.time()
            except Exception as e:
                print(f"Exception in updateLoop : {e}")
                self.sendTelegramMessage(f"Exception in updateLoop : {e}")
            time.sleep(10)

    def status(self):
        print(f"*" * 20)
        print(f"Thermostat Status")
        for device in self.devices:
            device.status()
        print(f"/" * 20)

    def generateJson(self):
        json = {}
        json["update"] = self.isUpdate
        for device in self.devices:
            json[device.name] = {}
            json[device.name]["state"] = device.state
            json[device.name]["value"] = device.value
            json[device.name]["setpoint"] = device.setpoint
            json[device.name]["triggerBuffer"] = device.triggerBuffer
            json[device.name]["isInvertedControl"] = device.isInvertedControl
            json[device.name]["warningTime"] = device.warningTime
            json[device.name]["warningDelay"] = device.warningDelay
            json[device.name]["timeSinceWarning"] = time.time() - device.warningTime
            json[device.name]["triggerOnURL"] = device.triggerOnURL
            json[device.name]["triggerOffURL"] = device.triggerOffURL
        return json


@app.route("/update")
def postJsonHandler():
    global thermostat
    thermostat.isUpdate = True
    return thermostat.generateJson()


@app.route("/")
def index():
    global thermostat
    thermostat.status()
    return thermostat.generateJson()


if __name__ == "__main__":
    # ****************************************************
    print(f"Starting Thermostat - __main__")

    # ****************************************************
    # load the secrets from a file
    # get all files in the current directory tree
    file_lines = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith("SECRETS.h"):
                with open(os.path.join(root, file), "r") as f:
                    file_lines.extend(f.readlines())

    # print(f"Secrets file found : {file_lines}")

    # parse the file for the secrets
    params = {}
    for line in file_lines:
        splits = line.split(" ")
        if len(splits) < 3:
            continue
        define = splits[0]
        key = splits[1]
        value = splits[2].strip()
        if '"' in str(value) or "'" in str(value):
            value = value[1:-1]
        if define == "#define":
            for defKey in typeDefs:
                if defKey == key:
                    print(f"Found secret : {key} -> {value} -> {typeDefs[defKey]}")
                    if typeDefs[defKey] == type(value):
                        params[key] = value
                    else:
                        params[key] = typeDefs[key](value)

    print(f"Secrets parsed : {params}")

    thermostat = Thermostat(params)

    # ****************************************************
    print(f"*" * 20)
    print(f"Adding Heater")

    heater = Device(
        name="Heater",
        triggerOnURL="https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=342d523b-0eb3-4569-b41e-cfa75501a381&token=3b3e350d-9c95-4c44-bc56-3b70bf37110c&response=json",
        triggerOffURL="https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=25024e42-c804-4e54-a1aa-4a96b5d52c63&token=0bb2c8db-ee00-440b-8f57-58d0c2ea3ad1&response=json",
        valueKey=params[secretKeys.IO_TEMPRATURE_FEED.name],
        setpointKey=params[secretKeys.IO_TEMPRATURE_SETPOINT.name],
        triggerBufferKey=params[secretKeys.IO_TEMPRATURE_BUFFER.name],
        isInvertedControl=True,
        warningMultiplier=10,
        warningDelay=60 * 60,
    )
    heater.setup(thermostat.AIO, thermostat.sendTelegramMessage)
    thermostat.addDevice(heater)

    # ****************************************************
    print(f"*" * 20)
    print(f"Adding Humidifier")

    humidifier = Device(
        name="Humidifier",
        triggerOnURL="https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=aee87633-0f8b-4eb9-8c3d-b8b74de27b15&token=f79d10a7-16c5-4c69-8d53-e638bd9e6e51&response=json",
        triggerOffURL="https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=fa6a2a20-4663-46b8-bff7-15758e676f27&token=f7f83342-b01c-4c57-a7f1-950309f9d6c2&response=json",
        valueKey=params[secretKeys.IO_HUMIDITY_FEED.name],
        setpointKey=params[secretKeys.IO_HUMIDITY_SETPOINT.name],
        triggerBufferKey=params[secretKeys.IO_HUMIDITY_BUFFER.name],
        isInvertedControl=True,
        warningMultiplier=2,
        warningDelay=60 * 60,
    )
    humidifier.setup(thermostat.AIO, thermostat.sendTelegramMessage)
    thermostat.addDevice(humidifier)

    # ****************************************************
    print(f"*" * 20)
    print(f"Adding Fan")

    fan = Device(
        name="Fan",
        triggerOnURL="https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=77420b03-5674-40b5-8829-ea6d0b68c0b0&token=743cdc42-37f1-4b5c-880f-83eeecd28d46&response=json",
        triggerOffURL="https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=c5e4bfe1-1bb0-48dd-9ea0-6ec5a2110549&token=a9bb3cd6-6085-436d-930e-79f6c4d52c43&response=json",
        valueKey=params[secretKeys.IO_TEMPRATURE_FEED.name],
        setpointKey=params[secretKeys.IO_TEMPRATURE_SETPOINT.name],
        triggerBufferKey=params[secretKeys.IO_TEMPRATURE_BUFFER.name],
        isInvertedControl=False,
        warningMultiplier=10,
        warningDelay=60 * 60,
    )
    fan.setup(thermostat.AIO, thermostat.sendTelegramMessage)
    thermostat.addDevice(fan)

    # ****************************************************
    print(f"*" * 20)
    print(f"Running Thermostat")

    thermostat.run()

    thermostat.sendTelegramMessage("Thermostat Started")

    app.run(host="0.0.0.0", port="7000", debug=False)
    # app.run()

    # while True:
    #     thermostat.update()
    #     time.sleep(5)
