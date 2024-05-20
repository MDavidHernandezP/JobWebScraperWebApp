from flask import Flask, render_template, url_for, redirect

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/home")
def home():
    return render_template("main.html")

@app.route("/info")
def info():
    return render_template("info.html")

if __name__ == "__main__":
    app.run(debug=True)