from uflask.Flask import Flask
import network
import socket
import pHeader
import json

app = Flask("/www")


@app.route("/")
def home():
    return app.render_template(
        "list.html",
        title="Route Variable Example",
        instructions="Visit /profile/<name>/<age> to render a template with route variables.",
    )


@app.route("/profile/<str>/<int>")
def profile(name, age):
    return app.render_template("profile.html", title="Profile Page", name=name, age=age)


app.run(log=True, port=80, host="0.0.0.0")
