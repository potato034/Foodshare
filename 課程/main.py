from fastapi import FastAPI, Query
from typing import Annotated
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()

@app.get("/food")
def food(
    stinky:Annotated[int,Query(ge=1)],
    sausage:Annotated[int,Query(ge=1)],
    bubble:Annotated[int,Query(ge=1)],
    chicken:Annotated[int,Query(ge=1)]):
    total = (stinky * 65) + (sausage * 75) + (bubble * 55) + (chicken * 90)
     
    if total > 500:
        total_discount = int(total * 0.9)
    else:
        total_discount = "沒折扣"
    return HTMLResponse(f"""
    <b>總費用：</b>{total}<br>
    <b>折扣後費用：</b>{total_discount}
    """)


@app.get("/")
def index():
    return FileResponse("food.html")


@app.get("/test")
def testGet():
    return {"data":10, "method":"GET"}

@app.post("/test")
def testPost():
    return {"result":True, "method":"POST"}

@app.get("/i")
def index():
    return FileResponse("index2.html")