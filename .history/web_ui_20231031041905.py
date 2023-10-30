from flask import Flask
app = Flask(__name__)
from wtforms import Form, TextField, validators, SubmitField,DecimalField, IntegerField

@app.route("/")
def index():
    return "<h1>Not Much Going On Here</h1>"





class ReusableForm(Form):
    """User entry form for entering specifics for generation"""
    # Starting seed
    seed = TextField("Enter a seed string or 'random':", validators=[
                     validators.InputRequired()])
    # Diversity of predictions
    diversity = DecimalField('Enter diversity:', default=0.8,
                             validators=[validators.InputRequired(),
                                         validators.NumberRange(min=0.5, max=5.0,
                                         message='Diversity must be between 0.5 and 5.')])
    # Number of words
    words = IntegerField('Enter number of words to generate:',
                         default=50, validators=[validators.InputRequired(),
                                                 validators.NumberRange(min=10, max=100, 
                                                 message='Number of words must be between 10 and 100')])
    # Submit button
    submit = SubmitField("Enter")



app.run(host="127.0.0.1", port=13579)