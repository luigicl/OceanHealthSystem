from flask import Flask, render_template
from main import app

@app.route("/")
def home():
    return  render_template("home.html")
