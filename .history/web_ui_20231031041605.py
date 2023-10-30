from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Not Much Going On Here</h1>"

app.run(host="192.168.1.1", port=13579)