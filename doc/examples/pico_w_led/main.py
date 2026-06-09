from uflask.Flask import Flask
from machine import Pin
import network
import socket
import pHeader
import json

led = Pin('LED', Pin.OUT)
app = Flask("/www/pico_w_led")


@app.route("/")
def index():
    status = "on" if led.value() else "off"
    return app.render_template("index.html", title="Pico W LED Control", status=status)


@app.route("/led", methods=["POST"])
def led_control():
    data = json.loads(app.request.content)
    action = data.get("action")
    if action == "on":
        led.value(1)
    elif action == "off":
        led.value(0)
    return {"status": "on" if led.value() else "off"}


@app.route("/status")
def status():
    return {"status": "on" if led.value() else "off"}


app.run(log=True, port=80, host="0.0.0.0")
