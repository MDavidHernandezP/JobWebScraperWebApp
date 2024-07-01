from flask import Flask, render_template, url_for, redirect, request

app = Flask(__name__)

@app.route("/")    # Starting URL, renders the welcome template.
def main():
    return render_template("welcome.html")

@app.route("/welcome")    # Renders the same template as the route of the main function.
def welcome():
    return render_template("welcome.html")

@app.route("/home", methods=["POST", "GET"])    # Home route, both methods get and post, for getting the original url and getting the url with the selected options.
def home():
    if request.method == "POST":    # Using the post method to render the template with the selected options.
        selected_location = request.form.getlist("location")    # List with the location value.
        selected_time = request.form.getlist("time")    # List with the mode time value.
        selected_skills = request.form.getlist("skills")    # List with the skills values.

        selected_options = selected_location + selected_time + selected_skills    # Concatenating lists to have just one main list.

        print(selected_options)    # Printing the main list to check for errors.

        return render_template("main.html", results=selected_options)    # Render the html with the selected options.
    
    return render_template("main.html", results=None)    # Using the get method to render the template.

@app.route("/aboutus")    # About us web page.
def aboutus():
    return render_template("aboutus.html")

@app.route("/acknow")    # Acknowledgement web page.
def acknow():
    return render_template("acknow.html")

if __name__ == "__main__":
    app.run(debug=True)