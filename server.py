import time, math
from datetime import datetime
from typing import Dict
import numpy as np
import matplotlib.pyplot as plt
from fastapi import FastAPI, responses

app = FastAPI()
last_time = float()
start_time = time.time()

@app.post("/cpm/")
async def add_new_data(data: str, sensor: str):
    print("Data: "+data)
    print("Sensor: "+sensor)
    
    return {"message": "Data received"}