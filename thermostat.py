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
    "secretKeys", ["AIO_Username", "AIO_Key", "Telegram_Bot_Token", "Telegram_Chat_ID"]
)


class Device:
    def __init__(
        self,
        name,
        triggerOnURL,
        triggerOffURL,
        valueKey,
        setpointKey,
        triggerBufferKey,
        isInvertedControl=False,
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

        self.msgTime = 0
        self.msgDelay = 60 * 60  # 2 hours

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
            if self.value < self.setpoint - 2 * self.triggerBuffer:
                if time.time() - self.msgTime > self.msgDelay:
                    self.SendMessage(
                        f"{self.name} is below setpoint by {self.value - self.setpoint}. Check if the device is working properly."
                    )
                    self.msgTime = time.time()
        else:
            if self.value > self.setpoint + self.triggerBuffer:
                self.turnOn()
            elif self.value < self.setpoint - self.triggerBuffer:
                self.turnOff()
            if self.value > self.setpoint + 2 * self.triggerBuffer:
                if time.time() - self.msgTime > self.msgDelay:
                    self.SendMessage(
                        f"{self.name} is above setpoint by {self.setpoint - self.value}. Check if the device is working properly."
                    )
                    self.msgTime = time.time()

        self.status()

    def status(self):
        print(
            f"{self.name} : state -> {self.state} | value -> {self.value} | setpoint -> {self.setpoint} | triggerBuffer -> {self.triggerBuffer} | isInvertedControl -> {self.isInvertedControl} | msgTime -> {time.time() - self.msgTime}"
        )


class Thermostat:
    def __init__(self, params):
        self.AIO_USERNAME = params[secretKeys.AIO_Username.name]
        self.AIO_KEY = params[secretKeys.AIO_Key.name]
        self.AIO = Client(self.AIO_USERNAME, self.AIO_KEY)

        self.Telegram_Bot_Token = params[secretKeys.Telegram_Bot_Token.name]
        self.Telegram_Chat_ID = params[secretKeys.Telegram_Chat_ID.name]

        self.feeds = self.AIO.feeds()
        for f in self.feeds:
            print(f"Feed found : {f} with value -> {self.AIO.receive(f.key).value}")

        self.devices = []
        self.isUpdate = True
        self.updateTriggerKey = "thermostat.update-trigger"

        self.msgTime = time.time()
        self.msgDelay = 60 * 5  # 5 minutes

        self.updateThread = threading.Thread(target=self.updateLoop, daemon=True)

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
                if (
                    self.isUpdate
                    or int(float(self.getFeedValue(self.updateTriggerKey))) != 0
                ):
                    print(f"*" * 20)
                    print(f"Updating Thermostat")
                    for device in self.devices:
                        device.update()
                    print(f"/" * 20)
                    self.isUpdate = False
                    self.AIO.send_data(self.updateTriggerKey, 0)
                if time.time() - self.msgTime > self.msgDelay:
                    self.sendTelegramMessage("Thermostat is Down.")
                self.msgTime = time.time()
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
            json[device.name]["msgTime"] = device.msgTime
            json[device.name]["msgDelay"] = device.msgDelay
            json[device.name]["timeSinceMsg"] = time.time() - device.msgTime
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

    print(f"Secrets file found : {file_lines}")

    # parse the file for the secrets
    params = {}
    for line in file_lines:
        splits = line.split(" ")
        if len(splits) < 3:
            continue
        define = splits[0]
        key = splits[1]
        value = splits[2]
        if define == "#define":
            if key == "IO_USERNAME":
                params[secretKeys.AIO_Username.name] = value.strip()[1:-1]
            elif key == "IO_KEY":
                params[secretKeys.AIO_Key.name] = value.strip()[1:-1]
            elif key == "Telegram_automation_bot_token":
                params[secretKeys.Telegram_Bot_Token.name] = value.strip()[1:-1]
            elif key == "Telegram_automation_chat_id":
                params[secretKeys.Telegram_Chat_ID.name] = int(value.strip()[1:-1])

    print(f"Secrets parsed : {params}")

    thermostat = Thermostat(params)

    # ****************************************************
    print(f"*" * 20)
    print(f"Adding Heater")

    heater = Device(
        "Heater",
        "https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=342d523b-0eb3-4569-b41e-cfa75501a381&token=3b3e350d-9c95-4c44-bc56-3b70bf37110c&response=json",
        "https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=25024e42-c804-4e54-a1aa-4a96b5d52c63&token=0bb2c8db-ee00-440b-8f57-58d0c2ea3ad1&response=json",
        "thermostat.temprature-c",
        "thermostat.setpoint-temprature",
        "thermostat.temprature-buffer",
        True,
    )
    heater.setup(thermostat.AIO, thermostat.sendTelegramMessage)
    thermostat.addDevice(heater)

    # ****************************************************
    print(f"*" * 20)
    print(f"Adding Humidifier")

    humidifier = Device(
        "Humidifier",
        "https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=aee87633-0f8b-4eb9-8c3d-b8b74de27b15&token=f79d10a7-16c5-4c69-8d53-e638bd9e6e51&response=json",
        "https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=fa6a2a20-4663-46b8-bff7-15758e676f27&token=f7f83342-b01c-4c57-a7f1-950309f9d6c2&response=json",
        "thermostat.humidity",
        "thermostat.setpoint-humidity",
        "thermostat.humidity-buffer",
        True,
    )
    humidifier.setup(thermostat.AIO, thermostat.sendTelegramMessage)
    thermostat.addDevice(humidifier)

    # ****************************************************
    print(f"*" * 20)
    print(f"Adding Fan")

    fan = Device(
        "Fan",
        "https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=77420b03-5674-40b5-8829-ea6d0b68c0b0&token=743cdc42-37f1-4b5c-880f-83eeecd28d46&response=json",
        "https://www.virtualsmarthome.xyz/url_routine_trigger/activate.php?trigger=c5e4bfe1-1bb0-48dd-9ea0-6ec5a2110549&token=a9bb3cd6-6085-436d-930e-79f6c4d52c43&response=json",
        "thermostat.temprature-c",
        "thermostat.setpoint-temprature",
        "thermostat.temprature-buffer",
        False,
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
