from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Not Much Going On Here</h1>"

app.run(host="0.0.0.0", port=13579)