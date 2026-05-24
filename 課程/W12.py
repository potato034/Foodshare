from fastapi import FastAPI, Query
from typing import Annotated
from fastapi.responses import HTMLResponse, FileResponse

app = FastAPI()

@app.get("/square")
def square(num:Annotated[int, Query(ge=1)]):
    return {"result":num**2}

@app.get("/")
def index():
    return FileResponse("index.html")

@app.get("/mul")
def mul(n1:Annotated[int,None], n2:Annotated[int,None]):
    result = n1 * n2
    return {"data":result}