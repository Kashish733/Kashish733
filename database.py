import mysql.connector

DB_CONFIG = {
    "host" : "127.0.0.1",
    "user" : "root",
    "password" : "",
    "database" : "ArlingtonPhysiciansCenter",
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)