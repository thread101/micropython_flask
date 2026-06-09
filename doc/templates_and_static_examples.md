# uFlask Template + Static Examples

This directory contains example Python MicroPython servers built around `uflask` and its template/static support.

## What these examples show

- How to return HTML templates with `app.render_template("template.html", **context)`
- How to pass variables from a route into a template
- How to serve static CSS and JavaScript files from `/static/...`
- How to build a small Pico W LED control web UI

---

## Example 1: Basic site with HTML template and CSS

This example uses a simple homepage template and a static stylesheet.

Files:

- `doc/examples/basic_site/main.py`
- `doc/examples/basic_site/templates/index.html`
- `doc/examples/basic_site/templates/hello.html`
- `doc/examples/basic_site/static/js/main.js`
- `doc/examples/basic_site/static/styles.css`

Key points:

- `@app.route("/")` returns a template with a title and message.
- Template placeholders are filled by passing keyword arguments to `app.render_template()`.
- Static CSS is served from `/static/styles.css`.
- A second route uses a variable from the URL and renders it in a template.

---

## Example 2: Passing route variables into templates

This example focuses on dynamic routes and clearly shows how variables are passed from a URL into the HTML page.

Files:

- `doc/examples/variable_site/main.py`
- `doc/examples/variable_site/templates/profile.html`
- `doc/examples/variable_site/templates/list.html`
- `doc/examples/variable_site/static/styles/main.css`

Key points:

- `@app.route("/profile/<str>/<int>")` receives `name` and `age` directly from the request URL.
- The handler returns `app.render_template("profile.html", name=name, age=age)`.
- Template placeholders like `{name}` and `{age}` are replaced with actual values.

---

## Example 3: Pico W LED control site

A complete example site for controlling the Pico W built-in LED.

Files:

- `doc/examples/pico_w_led/main.py`
- `doc/examples/pico_w_led/templates/index.html`
- `doc/examples/pico_w_led/static/styles.css`
- `doc/examples/pico_w_led/static/js/led.js`

Key points:

- `@app.route("/")` renders the LED control page with the current status.
- `@app.route("/led/<str>")` accepts `on` or `off` and updates the LED.
- `@app.route("/status")` returns JSON status for frontend polling.
- The page uses `/static` assets for styles and client-side JavaScript.

---

## How to run these examples

1. Copy the example folder to your board storage or into `/www`.
2. Adapt `app = Flask("/www")` to the correct mount path.
3. Ensure Wi-Fi is connected before calling `app.run()`.
4. Visit the board IP in a browser to see the rendered pages.
