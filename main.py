from fastapi import FastAPI, HTTPException,Query
from typing import List
from pydantic import BaseModel
from uuid import uuid4
import sqlite3

app = FastAPI()

DATABASE_FILE = "carsdata.db"

class CarBase(BaseModel):
    brand: str
    model: str
    color: str
    year_of_manufacture: str
    fuel_type: str
    is_rented: bool
    is_available_to_buy: bool

def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id TEXT PRIMARY KEY,
            brand TEXT,
            model TEXT,
            color TEXT,
            year_of_manufacture TEXT,
            fuel_type TEXT,
            is_rented BOOLEAN,
            is_available_to_buy BOOLEAN
        )
    ''') 
    conn.commit()
    conn.close()

create_table()

@app.post("/api/cars", response_model=dict)
def add_car(car: CarBase):
    car_id = str(uuid4())
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cars (id, brand, model, color, year_of_manufacture, fuel_type, is_rented, is_available_to_buy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (car_id, car.brand, car.model, car.color, car.year_of_manufacture, car.fuel_type,
          car.is_rented, car.is_available_to_buy))
    conn.commit()
    conn.close()
    return {"id": car_id, **car.dict()}

@app.get("/api/cars", response_model=dict)
def get_cars():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars")
    cars = cursor.fetchall() 
    conn.close()
    car_list = [{"id": car[0], **dict(zip(CarBase.__annotations__, car[1:]))} for car in cars]
    return {"cars": car_list}


@app.get("/api/cars", response_model=dict)
def get_cars(
    id: str = Query(None),
    brand: str = Query(None),
    model: str = Query(None)
):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    query = "SELECT * FROM cars WHERE 1=1"
    params = []
    if id:
        query += " AND id = ?"
        params.append(id)

    if brand:
        query += " AND brand = ?"
        params.append(brand)

    if model:
        query += " AND model = ?"
        params.append(model)

    cursor.execute(query, params)
    cars = cursor.fetchall() 
    conn.close()

    car_list = [{"id": car[0], **dict(zip(CarBase.__annotations__, car[1:]))} for car in cars]
    return {"cars": car_list}

@app.put("/api/cars/{car_id}", response_model=dict)
def update_car(car_id: str, car_update: CarBase):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE cars
        SET brand=?, model=?, color=?, year_of_manufacture=?, fuel_type=?, is_rented=?, is_available_to_buy=?
        WHERE id=?
    ''', (car_update.brand, car_update.model, car_update.color, car_update.year_of_manufacture,
          car_update.fuel_type, car_update.is_rented, car_update.is_available_to_buy, car_id))
    conn.commit()
    cursor.execute("SELECT * FROM cars WHERE id=?", (car_id,))
    updated_car = cursor.fetchone()
    conn.close()
    if updated_car:
        return {"id": updated_car[0], **dict(zip(CarBase.__annotations__, updated_car[1:]))}

    raise HTTPException(status_code=404, detail="Car not found")



