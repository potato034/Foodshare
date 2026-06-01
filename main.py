from fastapi import FastAPI, Query,Form, File, UploadFile, Depends
from typing import Annotated
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
# 引入 SQLAlchemy 相關套件
from sqlalchemy.orm import Session
from database import engine, get_db
from models import FoodPost
FoodPost.metadata.create_all(bind=engine)
# 獲取當前檔案所在的目錄路徑，確保後續路徑設定正確
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/index.html")
def index_html():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 掛載靜態資料夾，確保前端能讀取圖片
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_images")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")


# ==== 3. 圖片上傳與資料寫入 API ====
@app.post("/api/upload-food")
async def upload_food_item(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # A. 處理圖片儲存至本地資料夾
    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
        
    saved_image_path = f"/images/{unique_filename}"
    
    # B. 使用 ORM 寫入 SQLite 資料庫
    new_post = FoodPost(
        title=title,
        description=description,
        image_path=saved_image_path
    )
    db.add(new_post)
    db.commit() # 提交存檔
    db.refresh(new_post)
    
    return {
        "result": True,
        "message": "資料與圖片成功存入 SQLite！",
        "data": {
            "id": new_post.id,
            "title": new_post.title,
            "image_url": new_post.image_path
        }
    }