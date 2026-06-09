from uflask.Flask import Flask
import network
import socket
import pHeader
import json

app = Flask("/www/basic_site")


@app.route("/")
def home():
    return app.render_template(
        "index.html",
        title="Basic uFlask Site",
        message="This page was rendered with uFlask templates and static CSS!",
    )


@app.route("/hello/<str>")
def hello(name):
    return app.render_template("hello.html", title="Hello Page", name=name)


app.run(log=True, port=80, host="0.0.0.0")
