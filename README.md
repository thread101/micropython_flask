# uFlask for MicroPython

A small Flask-like web framework for MicroPython devices. It provides a lightweight router, template rendering, static file serving, and JSON response handling via a familiar `@app.route` decorator style.

## Features

- `@app.route(path, methods=[...])` decorator for defining endpoints
- Path variables with typed route segments: `<str>`, `<int>`, `<float>`
- Wildcard route support using `*`
- Static file serving via `/static/...`
- Template rendering with `app.render_template("template.html", **context)`
- JSON responses returned from dictionaries
- HTTP server built on `socket` and `network`

## Installation to MicroPython `lib` folder

To use `uflask` on a MicroPython board, place the `uflask` package directory into your board's `lib/` folder.

### Option 1: Copy via USB / mounted filesystem
1. Connect the MicroPython device to your computer.
2. Mount the device filesystem or open the board drive.
3. Copy the entire `uflask/` folder into the device's `lib/` directory.

For example, the board filesystem structure should look like:

```
/lib/uflask/Flask.py
/lib/uflask/__init__.py
```

### Option 2: Use `mpremote` or `rshell`
If you have `mpremote` installed, run:

```bash
mpremote cp -r uflask /lib
```

Or with `rshell`:

```bash
rshell -p /dev/ttyUSB0 cp -r uflask /lib
```

> Adjust the serial port or device path as needed for your board.

## Dependency: `pHeader`

This project depends on the `pHeader` packet parsing module. Install it into the same MicroPython `lib/` folder alongside `uflask`.

```bash
mpremote cp -r https://github.com/thread101/micropython_header_parsing.git /lib/pHeader
```

Or clone and copy manually:

```bash
git clone https://github.com/thread101/micropython_header_parsing.git
mpremote cp -r micropython_header_parsing/pHeader /lib
```

## Getting started

Create a new script on your board, for example `main.py`, and import `Flask` from `uflask`:

```python
from uflask.Flask import Flask

app = Flask("/www")  # root folder contains the `templates` and `static` directories
''' Example board layout:
/www/
├── templates/
│   └── index.html
└── static/
    ├── js/
    │   └── main.js
    └── styles/
        └── main.css
'''
@app.route("/")
def home():
    return "Hello, World", 200

@app.route("/api", methods=["POST", "GET"])
def api():
    if app.request.header.method.lower() == "post":
        data = json.loads(app.request.content)
        print(data)
    return {"name": "Joe Doe"}

@app.route("/login/<str>/<int>")
def login(name, age):
    return app.render_template("index.html", title=f"Welcome {name}, age {age}!")

app.run(log=True, port=80, host="0.0.0.0")
```

Then restart the board. The app will listen on the board's network interface.

## Route examples

- Static route:
  - `@app.route("/")`
- Typed dynamic route:
  - `@app.route("/user/<str>/<int>")`
- Wildcard route:
  - `@app.route("/files/*")`
- JSON response:
  - return a Python `dict`
- Template response:
  - use `app.render_template("index.html", title="Hello")`

## Templates and static files

The example `Flask.py` uses `app.render_template` to return HTML templates from the `templates` folder passed to the `Flask` constructor.

Place HTML templates under:

```
/www/templates/
```

For static content, use the `/static` route and refer to files in:

```
/www/static/
```

The built-in static file handler checks the `Referer` header before serving files.

## Notes

- The framework requires a connected Wi-Fi interface (`network.WLAN(network.STA_IF)`) before calling `app.run()`.
- The `Flask` constructor requires a valid path to the package root.
- Use `log=True` in `app.run()` to enable request logging.

## Example board layout

```
/main.py
/www/templates/index.html
/www/static/styles/main.css
/www/static/js/main.js
```

## License

This project is licensed under the terms found in `LICENSE`.
