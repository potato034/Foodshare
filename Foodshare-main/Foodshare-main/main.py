from fastapi import FastAPI, Query,Form, File, UploadFile, Depends
from typing import Annotated
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
# 引入 SQLAlchemy 相關套件
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 獲取當前檔案所在的目錄路徑，確保後續路徑設定正確
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 掛載靜態資料夾，確保前端能讀取圖片
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_images")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

# ==== 1. SQLite 資料庫設定 ====
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'food.db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==== 2. 定義資料表模型 (Model) ====
class FoodPost(Base):
    __tablename__ = "food_posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=False) # 儲存圖片網址路徑

# 啟動時自動建立資料庫檔案與資料表 (如果不存在的話)
Base.metadata.create_all(bind=engine)

# 取得資料庫連線的穩定會話 (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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