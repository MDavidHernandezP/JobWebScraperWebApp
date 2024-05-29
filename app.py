from flask import Flask, render_template, url_for, redirect, request

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("welcome.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        selected_options = request.form.getlist("options")
        print(selected_options)

        return render_template("main.html", results=selected_options)
    
    return render_template("main.html", results=None)

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/acknow")
def acknow():
    return render_template("acknow.html")

if __name__ == "__main__":
    app.run(debug=True)