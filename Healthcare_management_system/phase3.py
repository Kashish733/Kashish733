from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database import get_connection
import os
from queries import (
    insert_speciality,
    get_patient_coverage,
    update_follow_up,
    delete_location
)
app = FastAPI(title = 'APC FastAPI', version = "1.0.0")
template_file = os.path.join(os.path.dirname(__file__), "templates/index.html")

def templates(result= ""):
    """Load HTML template"""
    with open(template_file, "r") as f:
        html = f.read()
    return html.replace ("{{result}}", result)


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(templates())


#Q1
@app.post("/q1/add-speciality", response_class = HTMLResponse)
def q1_add_speciality():
    insert_speciality()
    return HTMLResponse(templates("Speciality and pedriatic added"))

#Q2
@app.get("/q2/patient-coverage", response_class = HTMLResponse)
def q2_patient_coverage():
    r = get_patient_coverage()
    if not r:
        result = "No data found."
    else:
        result = "<table border= '1' cellpadding= '5'><tr><th>Name</th><th>Policy</th><th>Type</th><th>DOB</th></tr>"
        for i in r:
            result += f"<tr><td>{i['PatientName']}</td><td>{i['PolicyName']}</td><td>{i['PolicyType']}</td><td>{i['DateOfBirth']}</td></tr>"
        result+= "</table>"
    return HTMLResponse(templates(result))

# Q3 
@app.post("/q3/update-followup", response_class = HTMLResponse)
def q3_update_followup():
    update_follow_up()
    return HTMLResponse(templates("Follow-up updated."))

# Q4 
@app.post("/q4/delete-location", response_class = HTMLResponse)
def q4_delete_location():
    delete_location()
    return HTMLResponse(templates("Hospital location deleted."))

#-----------------------------------View-------------------------------

#for view
@app.get("/views", response_class= HTMLResponse)
def views_menu():
    html = """
    <html>
    <head>
        <title>Hospital Views Menu</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2c3e50; }
            a.button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px;
                background-color: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 16px;
            }
            a.button:hover { background-color: #2980b9; }
        </style>
    </head>
    <body>
        <h1>Hospital Views Menu</h1>
        <a href="/views/hospitals_cityville" class="button">QV1 – Hospitals in Cityville</a><br>
        <a href="/views/patients_over_30" class="button">QV2 – Patients Over 30</a><br>
        <a href="/views/top_physician" class="button">QV3 – Physician with Most Specialities</a><br>
        <a href="/views/average_patient_age" class="button">QV4 – Average Patient Age</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html)



#qv1
@app.get("/views/hospitals_cityville", response_class = HTMLResponse)
def qv1():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT HospitalName, Locations
            FROM HospitalLocationSummary
            WHERE Locations LIKE '%Cityville%';
        """)
        hospitals = cursor.fetchall()

        cursor.close()
        conn.close()

        if hospitals:
            result = "<table border='1' cellpadding='5'><tr><th>Hospital</th><th>Locations</th></tr>"
            for h in hospitals:
                result += f"<tr><td>{h['HName']}</td><td>{h['Locations']}</td></tr>"
            result += "</table>"
        else:
            result = "No hospital Found"
        return HTMLResponse(templates(result))


#qv2
@app.get("/views/patients_over_30", response_class = HTMLResponse)
def qv2():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT PatientName, Age
            FROM PatientAgeDistribution
            WHERE Age > 30;
        """)
        patients = cursor.fetchall()

        cursor.close()
        conn.close()

        if patients:
            result = "<table border='1' cellpadding='5'><tr><th>Name</th><th>Age</th></tr>"
            for p in patients:
                result += f"<tr><td>{p['PatientName']}</td><td>{p['Age']}</td></tr>"
            result += "</table>"
        else:
            result = "No patient Found"
        return HTMLResponse(templates(result))

        

#qv3
@app.get("/views/top_physician", response_class = HTMLResponse)
def qv3():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)


        cursor.execute("""
            SELECT PhysicianFullName, SpecialityCount
            FROM PhysicianSpecialityCount
            ORDER BY SpecialityCount DESC
            LIMIT 1;
        """)
        physician = cursor.fetchone()

        cursor.close()
        conn.close()

        if physician:
            result = f"<p>Name: {physician['PhysicianFullName']}</p><p>Specialities: {physician['SpecialityCount']}</p>"
        else:
            result = "No physician data found."
        return HTMLResponse(templates(result))

#qv4   
@app.get("/views/average_patient_age", response_class = HTMLResponse)
def qv4():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)


        cursor.execute("""
            SELECT AVG(Age) AS AverageAge
            FROM PatientAgeDistribution;
        """)
        result = cursor.fetchone()['AverageAge']

        cursor.close()
        conn.close()

        result = f"<p>Average Age: {round(result,2)}</p>"  
        return HTMLResponse(templates(result))
