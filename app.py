from flask import Flask, render_template, request
import asyncio
from scraper import JobScraper

app = Flask(__name__)

# Variable global para almacenar los trabajos encontrados
jobs_data = {}

@app.route("/")
def main():
    return render_template("welcome.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        # Obtener los datos del formulario
        location = request.form.get("location")
        selected_technologies = request.form.getlist("technologies")
        selected_techskills = request.form.getlist("techskills")
        selected_robotics = request.form.getlist("robotics")
        selected_embedded = request.form.getlist("embedded")
        selected_softskills = request.form.getlist("softskills")
        selected_modes = request.form.getlist("mode")

        # Unir las cadenas de habilidades en una sola cadena separada por comas
        qskills = ', '.join(selected_technologies + selected_techskills + selected_robotics + selected_embedded + selected_softskills)
        qplace = location
        qtype = ', '.join(selected_modes)

        # Ejecutar el scraper con los parámetros obtenidos
        async def run_scraper():
            scraper = JobScraper(qskills, qplace, qtype)
            await scraper.get_all_jobs()

            # Guardar los trabajos en la variable global jobs_data
            global jobs_data
            jobs_data = scraper.jobs

            scraper.driver.quit()

            # Imprimir los valores encontrados
            print("Jobs found:")
            for job_title, job_details in jobs_data.items():
                print(f"Title: {job_title}, Details: {job_details}")

        asyncio.run(run_scraper())

        return render_template("main.html", jobs=jobs_data)
    
    return render_template("main.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/acknow")
def acknow():
    return render_template("acknow.html")

if __name__ == "__main__":
    app.run(debug=True)
