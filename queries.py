from database import get_connection


def insert_speciality():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT IGNORE INTO Speciality (SName)
        VALUES ('Pediatrics')
    """)
    cursor.execute("""
        INSERT IGNORE INTO Physician (PId, FName, MInitial, LName, HId)
        VALUES (601, 'Emily', 'C', 'White', 1);
    """)

    cursor.execute("""
            INSERT IGNORE INTO Physician_Speciality (SpecialityId, SName)
            VALUES (601, "Pediatrics")
        """)
    
    cursor.execute("""
        INSERT INTO Patient (PSSN, PName, Sex, DateOfBirth, PId)
        VALUES ('22233445566', 'Timmy Jones', 'M','2020-01-15', 601);
    """)
    conn.commit()
    cursor.close()
    conn.close()



def get_patient_coverage():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            p.PName AS PatientName,
            c.PoName AS PolicyName,
            c.PoType AS PolicyType,
            p.DateOfBirth AS DateOfBirth         
        FROM Patient p
        JOIN CoveragePolicy c ON p.Pold = c.Pold;
    """)
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result


def update_follow_up():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        UPDATE Consultation
        SET FDate = '2025-08-01' , FTime = '11:00:00'
        WHERE PSSN = '111-22-3333'
          AND CDate = '2025-08-01'
          AND CTime = '06:00:00'
    """)
    conn.commit
    cursor.close()
    conn.close()


def delete_location():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        DELETE FROM Hospital_Location
        WHERE HId = 301
        AND Location = '1000 Hospital Dr, Cityville'
    """)
    conn.commit
    cursor.close()
    conn.close()
