from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Not Much Going On Here</h1>"

app.run(host=localhost, port=13579)