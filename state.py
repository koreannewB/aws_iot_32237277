# state.py
TREADMILL = {1: "", 2: "", 3: "", 4: ""}

TOWEL = {
    1: {"name": "Dispenser 1", "count": 15, "max": 20},
    2: {"name": "Dispenser 2", "count": 8,  "max": 20},
    3: {"name": "Dispenser 3", "count": 20, "max": 20},  # ← 추가
}

EQUIPMENT = [
    {"id": 1, "name": "Bench Press",   "status": "available", "in_use": 0},
    {"id": 2, "name": "Dumbbell Rack", "status": "available", "in_use": 0},
]