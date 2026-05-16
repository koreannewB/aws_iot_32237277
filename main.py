# 실행: python main.py
# 가상환경: source venv/bin/activate

import threading
import state
import treadmill
import towel_remaining
import fitness_equipment
import uvicorn 
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("templates/index.html")


@app.get("/TMdata")
async def tm_data():
    return {
        "Tmn1": state.TREADMILL[1],
        "Tmn2": state.TREADMILL[2],
        "Tmn3": state.TREADMILL[3],
        "Tmn4": state.TREADMILL[4],
    }


@app.get("/toweldata")
async def towel_data():
    return state.TOWEL


@app.get("/equipmentdata")
async def equipment_data():
    return state.EQUIPMENT
@app.get("/monitor")
async def monitor():
    return FileResponse('templates/monitor.html')

@app.get("/video")
async def video():
    print(f"current_frame: {treadmill.current_frame is None}")  # 확인용
    return {"frame": treadmill.current_frame}

def main():
    try:
        import sensor
        sensor.init_gpio()
        sensor.start_threads()
    except ImportError:
        pass

    thread_treadmill = threading.Thread(target=treadmill.trail_detect_run, daemon=True)
    thread_towel   = threading.Thread(target=towel_remaining.run, daemon=True)
    #thread_fitness = threading.Thread(target=fitness_equipment.run, daemon=True)

    thread_treadmill.start()
    thread_towel.start()
    # thread_fitness.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
