from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Not Much Going On Here</h1>"

app.run(host="127.0.0.1", port=13579)