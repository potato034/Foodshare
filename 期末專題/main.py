from fastapi import FastAPI, Query
from typing import Annotated
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()



@app.get("/")
def index():
    return FileResponse("index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")