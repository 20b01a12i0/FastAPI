
from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel

app = FastAPI()

class CarBase(BaseModel):
    brand: str
    model: str
    color: str
    year_of_manufacture: str
    fuel_type: str
    is_rented: bool
    is_available_to_buy: bool

data = []

@app.post("/api/cars", response_model=dict)
def add_car(car: CarBase):
    car_id = len(data) + 1
    new_car = {"id": car_id, **car.dict()}
    data.append(new_car)
    return new_car

@app.get("/api/cars", response_model=List[dict])
def get_cars():
    return data

@app.get("/api/cars/{car_id}", response_model=dict)
def get_car(car_id: int):
    for car in data:
        if car["id"] == car_id:
            return car
    raise HTTPException(status_code=404, detail="Car not found")


@app.put("/api/cars/{car_id}", response_model=dict)
def update_car(car_id: int, car_update: CarBase):
    for car in data:
        if car["id"] == car_id:
            for field, value in car_update.dict(exclude_unset=True).items():
                car[field] = value
            return car
    raise HTTPException(status_code=404, detail="Car not found")
