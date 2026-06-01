from fastapi import FastAPI, Form, File, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os, uuid

from database import engine, get_db
from models import Base, User, FoodPost, Reservation, Location, Message

# 啟動時自動建立所有資料表
Base.metadata.create_all(bind=engine)

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploaded_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# 允許前端（開發時用 file:// 或 localhost）跨域呼叫 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 靜態檔案掛載 ───────────────────────────────────────────────
@app.get("/")
def index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/index.html")
def index_html():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

# 地點座標從 DB 查（不再硬編碼）
DEFAULT_COORDS = [24.1232, 120.6776]   # 查不到時的備用座標（中興大學中心）

def get_location_coords(name: str, db: Session) -> list:
    loc = db.query(Location).filter(Location.name == name).first()
    return [loc.lat, loc.lng] if loc else DEFAULT_COORDS

# ── 查找表：類別 → emoji 與顏色 ───────────────────────────────
CATEGORY_META = {
    "便當": {"emoji": "🍱", "bg_color": "bg-teal-50",    "text_color": "text-teal-600",   "badge_color": "bg-teal-50"},
    "飲料": {"emoji": "🧋", "bg_color": "bg-orange-100", "text_color": "text-orange-600", "badge_color": "bg-orange-50"},
    "餐盒": {"emoji": "🥡", "bg_color": "bg-blue-50",    "text_color": "text-blue-600",   "badge_color": "bg-blue-50"},
    "甜點": {"emoji": "🍰", "bg_color": "bg-yellow-50",  "text_color": "text-yellow-600", "badge_color": "bg-yellow-50"},
    "其他": {"emoji": "🥪", "bg_color": "bg-purple-50",  "text_color": "text-purple-600", "badge_color": "bg-purple-50"},
}

STATUS_LABEL = {
    "available": "可領取",
    "reserved":  "已預約",
    "completed": "已完成",
    "expired":   "已過期",
}

# ── 輔助函式 ───────────────────────────────────────────────────
def time_ago(dt: datetime) -> str:
    minutes = int((datetime.utcnow() - dt).total_seconds() / 60)
    if minutes < 1:   return "剛剛"
    if minutes < 60:  return f"{minutes} 分鐘前"
    if minutes < 1440: return f"{minutes // 60} 小時前"
    return f"{minutes // 1440} 天前"

def food_to_card(post: FoodPost, db: Session = None) -> dict:
    """轉換成首頁地圖卡片格式。"""
    meta   = CATEGORY_META.get(post.category, CATEGORY_META["其他"])
    coords = get_location_coords(post.main_location, db) if db else DEFAULT_COORDS
    loc    = f"{post.main_location}　{post.detail_location or ''}".strip()
    sharer_name = ""
    if post.sharer:
        sharer_name = post.sharer.display_name or post.sharer.email.split("@")[0]
    return {
        "id":              post.id,
        "title":           post.title,
        "category":        post.category,
        "description":     post.description or "",
        "pickup_location": loc,
        "main_location":   post.main_location or "",
        "detail_location": post.detail_location or "",
        "time_limit":      post.time_limit,   # 單位：分鐘（編輯頁預填用）
        "time_ago":        time_ago(post.created_at),
        "coords":          coords,
        "emoji":           post.emoji or meta["emoji"], # 用戶自選優先
        "bg_color":        meta["bg_color"],
        "text_color":      meta["text_color"],
        "badge_color":     meta["badge_color"],
        "status":          post.status,
        "status_label":    STATUS_LABEL.get(post.status, post.status),
        "quantity":        post.quantity if post.quantity is not None else "",
        "quantity_left":   post.quantity_left if post.quantity_left is not None else post.quantity,
        "sharer_name":     sharer_name,
        "image_path":      post.image_path or "",
        "expires_at_iso":  (post.expires_at.isoformat() + "Z") if post.expires_at else None,
    }

def food_to_list_item(post: FoodPost) -> dict:
    """轉換成清單卡片格式（share.html / food.html 共用）。"""
    meta = CATEGORY_META.get(post.category, CATEGORY_META["其他"])
    loc  = f"{post.main_location}　{post.detail_location or ''}".strip()
    return {
        "id":         post.id,
        "title":      post.title,
        "emoji":      post.emoji or meta["emoji"],  # 用戶自選優先
        "image_path": post.image_path or "",        # 清單卡片顯示圖片用
        "location":   loc,
        "timeLabel":  time_ago(post.created_at),
        "href":       f"./detail.html?id={post.id}",
        "status":     STATUS_LABEL.get(post.status, post.status),
    }

# ══════════════════════════════════════════════════════════════
# API：地點管理
# ══════════════════════════════════════════════════════════════

@app.get("/api/locations")
def get_locations(db: Session = Depends(get_db)):
    """取得所有地點（供上傳表單下拉選單使用）。"""
    locs = db.query(Location).order_by(Location.name).all()
    return [{"id": l.id, "name": l.name, "lat": l.lat, "lng": l.lng} for l in locs]

@app.post("/api/locations")
def add_location(
    name: str   = Form(...),
    lat:  float = Form(...),
    lng:  float = Form(...),
    db: Session = Depends(get_db),
):
    """新增地點。name 不能重複。"""
    if db.query(Location).filter(Location.name == name).first():
        raise HTTPException(status_code=400, detail="此地點名稱已存在")
    db.add(Location(name=name, lat=lat, lng=lng))
    db.commit()
    return {"ok": True}

@app.put("/api/locations/{loc_id}")
def update_location(
    loc_id: int,
    name:   str   = Form(...),
    lat:    float = Form(...),
    lng:    float = Form(...),
    db: Session   = Depends(get_db),
):
    """修改地點名稱或座標。"""
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="找不到此地點")
    loc.name = name
    loc.lat  = lat
    loc.lng  = lng
    db.commit()
    return {"ok": True}

@app.delete("/api/locations/{loc_id}")
def delete_location(loc_id: int, db: Session = Depends(get_db)):
    """刪除地點。"""
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="找不到此地點")
    db.delete(loc)
    db.commit()
    return {"ok": True}

# ══════════════════════════════════════════════════════════════
# API：使用者
# ══════════════════════════════════════════════════════════════

@app.post("/api/users/sync")
def sync_user(
    firebase_uid: str = Form(...),
    email:        str = Form(...),
    display_name: str = Form(None),
    db: Session = Depends(get_db),
):
    """Firebase 登入後，把使用者資料同步到 SQLite。"""
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    if user:
        user.email = email
        if display_name:
            user.display_name = display_name
    else:
        user = User(firebase_uid=firebase_uid, email=email, display_name=display_name)
        db.add(user)
    db.commit()
    return {"ok": True}

# ══════════════════════════════════════════════════════════════
# API：食物貼文
# ══════════════════════════════════════════════════════════════

@app.get("/api/foods")
def get_foods(db: Session = Depends(get_db)):
    """首頁地圖用：取得所有狀態為 available 且尚未過期的食物。
    順便把到期的食物自動標記為 expired。
    """
    now = datetime.utcnow()
    # 自動將過期食物標記為 expired
    expired_posts = db.query(FoodPost).filter(
        FoodPost.status == "available",
        FoodPost.expires_at < now
    ).all()
    for p in expired_posts:
        p.status = "expired"
    if expired_posts:
        db.commit()

    posts = db.query(FoodPost).filter(
        FoodPost.status == "available",
        FoodPost.expires_at > now
    ).all()
    return [food_to_card(p, db) for p in posts]

@app.get("/api/foods/{food_id}")
def get_food(food_id: int, uid: str = None, db: Session = Depends(get_db)):
    """詳細頁用：取得單一食物完整資訊。
    可選傳入 uid 查詢參數，回傳該使用者對這筆食物的預約狀態。
    """
    post = db.query(FoodPost).filter(FoodPost.id == food_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="找不到此食物貼文")
    data = food_to_card(post, db)
    # 判斷目前使用者的身份與預約狀態
    data["is_my_post"] = (uid == post.sharer_uid) if uid else False
    my_reservation = None
    if uid:
        my_reservation = (
            db.query(Reservation)
            .filter(Reservation.food_post_id == food_id,
                    Reservation.requester_uid == uid)
            .order_by(Reservation.created_at.desc())
            .first()
        )
    data["my_reservation_status"] = my_reservation.status if my_reservation else None
    return data

@app.post("/api/foods")
async def create_food(
    sharer_uid:      str        = Form(...),
    title:           str        = Form(...),
    category:        str        = Form(...),
    emoji_choice:    str        = Form(None),   # 使用者自選的 emoji，沒選則用類別預設
    quantity:        int        = Form(None),
    main_location:   str        = Form(...),
    detail_location: str        = Form(None),
    time_limit:      int        = Form(2),
    description:     str        = Form(None),
    file:            UploadFile = File(None),
    db:              Session    = Depends(get_db),
):
    """upload.html 發布食物用。"""
    user = db.query(User).filter(User.firebase_uid == sharer_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在，請重新登入")

    image_path = None
    if file and file.filename:
        ext      = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        contents = await file.read()
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
            f.write(contents)
        image_path = f"/images/{filename}"

    meta   = CATEGORY_META.get(category, CATEGORY_META["其他"])
    coords = get_location_coords(main_location, db)
    now    = datetime.utcnow()
    # 使用者自選 emoji 優先，否則用類別預設
    emoji  = emoji_choice.strip() if emoji_choice and emoji_choice.strip() else meta["emoji"]

    post = FoodPost(
        sharer_uid=sharer_uid,
        title=title,
        category=category,
        emoji=emoji,
        description=description,
        quantity=quantity,
        quantity_left=quantity,   # 初始剩餘 = 總份數
        main_location=main_location,
        detail_location=detail_location,
        lat=coords[0],
        lng=coords[1],
        time_limit=time_limit,
        image_path=image_path,
        created_at=now,
        expires_at=now + timedelta(minutes=time_limit),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"ok": True, "id": post.id}

# ══════════════════════════════════════════════════════════════
# API：預約
# ══════════════════════════════════════════════════════════════

@app.put("/api/foods/{food_id}")
async def update_food(
    food_id:         int,
    sharer_uid:      str        = Form(...),
    title:           str        = Form(...),
    category:        str        = Form(...),
    emoji_choice:    str        = Form(None),
    quantity:        int        = Form(None),
    main_location:   str        = Form(...),
    detail_location: str        = Form(None),
    time_limit:      int        = Form(2),
    description:     str        = Form(None),
    status:          str        = Form(None),   # 分享者可手動改狀態
    file:            UploadFile = File(None),
    db:              Session    = Depends(get_db),
):
    """share.html 編輯食物用。只有分享者本人可以編輯。"""
    post = db.query(FoodPost).filter(FoodPost.id == food_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="找不到此食物貼文")
    if post.sharer_uid != sharer_uid:
        raise HTTPException(status_code=403, detail="只有分享者才能編輯")

    meta  = CATEGORY_META.get(category, CATEGORY_META["其他"])
    emoji = emoji_choice.strip() if emoji_choice and emoji_choice.strip() else meta["emoji"]
    coords = LOCATION_COORDS.get(main_location, [post.lat or 24.1232, post.lng or 120.6776])

    if file and file.filename:
        ext      = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        contents = await file.read()
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
            f.write(contents)
        post.image_path = f"/images/{filename}"

    post.title           = title
    post.category        = category
    post.emoji           = emoji
    post.description     = description
    post.quantity        = quantity
    post.main_location   = main_location
    post.detail_location = detail_location
    post.lat             = coords[0]
    post.lng             = coords[1]
    post.time_limit      = time_limit
    post.expires_at      = datetime.utcnow() + timedelta(minutes=time_limit)  # 從現在重新計時
    if status in ("available", "completed"):   # 只允許分享者手動切這兩個狀態
        post.status = status
    db.commit()
    return {"ok": True}

@app.delete("/api/foods/{food_id}")
def delete_food(
    food_id:    int,
    sharer_uid: str     = Form(...),
    db:         Session = Depends(get_db),
):
    """share.html 刪除食物用。只有分享者本人可以刪除。"""
    post = db.query(FoodPost).filter(FoodPost.id == food_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="找不到此食物貼文")
    if post.sharer_uid != sharer_uid:
        raise HTTPException(status_code=403, detail="只有分享者才能刪除")
    db.query(Reservation).filter(Reservation.food_post_id == food_id).delete()
    db.delete(post)
    db.commit()
    return {"ok": True}

@app.post("/api/foods/{food_id}/reserve")
def reserve_food(
    food_id:               int,
    requester_uid:         str     = Form(...),
    quantity_reserved:     int     = Form(1),
    requester_name:        str     = Form(None),
    student_id:            str     = Form(None),
    estimated_pickup_time: str     = Form(None),
    db:                    Session = Depends(get_db),
):
    """detail.html 預約食物。"""
    post = db.query(FoodPost).filter(FoodPost.id == food_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="找不到此食物貼文")
    if post.status not in ("available",):
        raise HTTPException(status_code=400, detail="此食物目前不可預約")
    if post.sharer_uid == requester_uid:
        raise HTTPException(status_code=400, detail="不能預約自己發布的食物")

    left = post.quantity_left if post.quantity_left is not None else post.quantity
    if left is None or quantity_reserved > left:
        raise HTTPException(status_code=400, detail=f"剩餘份數不足（剩 {left} 份）")

    # 扣除份數
    post.quantity_left = left - quantity_reserved
    if post.quantity_left <= 0:
        post.status = "completed"   # 全部被預約完 → 下架

    reservation = Reservation(
        food_post_id=food_id,
        requester_uid=requester_uid,
        quantity_reserved=quantity_reserved,
        requester_name=requester_name,
        student_id=student_id,
        estimated_pickup_time=estimated_pickup_time,
    )
    db.add(reservation)

    # 更新預約者的累積預約次數
    requester = db.query(User).filter(User.firebase_uid == requester_uid).first()
    if requester:
        requester.total_reservations += 1

    db.commit()
    return {"ok": True, "quantity_left": post.quantity_left}

@app.post("/api/foods/{food_id}/complete")
def complete_food(
    food_id:       int,
    sharer_uid:    str     = Form(...),   # 由分享者點確認
    reservation_id: int    = Form(...),
    db:            Session = Depends(get_db),
):
    """分享者確認對方已領取。"""
    r = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.food_post_id == food_id,
        Reservation.status == "pending"
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="找不到對應的預約")
    if r.food_post.sharer_uid != sharer_uid:
        raise HTTPException(status_code=403, detail="只有分享者可以確認完成")

    r.status = "completed"
    # 如果所有 pending 預約都完成，食物標記為 completed
    pending_count = db.query(Reservation).filter(
        Reservation.food_post_id == food_id,
        Reservation.status == "pending"
    ).count()
    if pending_count == 0:
        r.food_post.status = "completed"
    db.commit()
    return {"ok": True}

@app.post("/api/foods/{food_id}/no_show")
def mark_no_show(
    food_id:        int,
    sharer_uid:     str     = Form(...),
    reservation_id: int     = Form(...),
    db:             Session = Depends(get_db),
):
    """分享者標記「未取」，計入取貨率。"""
    r = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.food_post_id == food_id,
        Reservation.status == "pending"
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="找不到對應的預約")
    if r.food_post.sharer_uid != sharer_uid:
        raise HTTPException(status_code=403, detail="只有分享者可以標記未取")

    r.status = "no_show"
    # 退還份數
    r.food_post.quantity_left = (r.food_post.quantity_left or 0) + r.quantity_reserved
    if r.food_post.status == "completed":
        r.food_post.status = "available"

    # 計入未取次數
    requester = db.query(User).filter(User.firebase_uid == r.requester_uid).first()
    if requester:
        requester.no_show_count += 1

    db.commit()
    return {"ok": True}

@app.post("/api/foods/{food_id}/cancel")
def cancel_food(
    food_id:        int,
    requester_uid:  str     = Form(...),
    reservation_id: int     = Form(...),
    db:             Session = Depends(get_db),
):
    """預約者取消預約（距過期 > 10 分鐘才可取消）。"""
    r = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.food_post_id == food_id,
        Reservation.requester_uid == requester_uid,
        Reservation.status == "pending"
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="找不到對應的預約")

    # 距過期不足 10 分鐘則不能取消
    if r.food_post.expires_at:
        mins_left = (r.food_post.expires_at - datetime.utcnow()).total_seconds() / 60
        if mins_left < 10:
            raise HTTPException(status_code=400, detail="距過期不足 10 分鐘，無法取消")

    r.status = "cancelled"
    # 退還份數
    r.food_post.quantity_left = (r.food_post.quantity_left or 0) + r.quantity_reserved
    if r.food_post.status == "completed":
        r.food_post.status = "available"

    db.commit()
    return {"ok": True}

# ══════════════════════════════════════════════════════════════
# API：使用者清單
# ══════════════════════════════════════════════════════════════

@app.get("/api/users/{uid}/pickup-rate")
def get_pickup_rate(uid: str, db: Session = Depends(get_db)):
    """取得使用者的取貨率統計。"""
    user = db.query(User).filter(User.firebase_uid == uid).first()
    if not user:
        return {"total": 0, "no_show": 0, "rate": 100}
    total   = user.total_reservations
    no_show = user.no_show_count
    rate    = round((1 - no_show / total) * 100) if total > 0 else 100
    return {"total": total, "no_show": no_show, "rate": rate}

@app.get("/api/foods/{food_id}/reservations")
def get_food_reservations(food_id: int, sharer_uid: str, db: Session = Depends(get_db)):
    """分享者查看某食物的所有預約訂單。"""
    post = db.query(FoodPost).filter(FoodPost.id == food_id).first()
    if not post or post.sharer_uid != sharer_uid:
        raise HTTPException(status_code=403, detail="無權限")
    return [
        {
            "reservation_id":        r.id,
            "status":                r.status,
            "quantity_reserved":     r.quantity_reserved,
            "requester_name":        r.requester_name or "—",
            "student_id":            r.student_id or "—",
            "estimated_pickup_time": r.estimated_pickup_time or "—",
            "requester_uid":         r.requester_uid,
        }
        for r in post.reservations
        if r.status != "cancelled"
    ]

@app.get("/api/users/{uid}/shares")
def get_user_shares(uid: str, db: Session = Depends(get_db)):
    """share.html 用：取得此使用者發布的所有食物。"""
    posts = (db.query(FoodPost)
               .filter(FoodPost.sharer_uid == uid)
               .order_by(FoodPost.created_at.desc())
               .all())
    return [food_to_list_item(p) for p in posts]

# ══════════════════════════════════════════════════════════════
# API：後台管理（Admin）
# ══════════════════════════════════════════════════════════════

@app.get("/api/admin/foods")
def admin_get_foods(db: Session = Depends(get_db)):
    """後台：取得所有食物貼文（含過期/完成）。"""
    posts = db.query(FoodPost).order_by(FoodPost.created_at.desc()).all()
    result = []
    for p in posts:
        d = food_to_card(p, db)
        d["sharer_uid"] = p.sharer_uid
        d["created_at"] = p.created_at.isoformat() if p.created_at else None
        d["expires_at"] = p.expires_at.isoformat() if p.expires_at else None
        d["reservation_count"] = len([r for r in p.reservations if r.status != "cancelled"])
        result.append(d)
    return result

@app.patch("/api/admin/foods/{food_id}/status")
def admin_update_food_status(
    food_id: int,
    status:  str     = Form(...),
    db:      Session = Depends(get_db),
):
    """後台：直接修改食物狀態。"""
    post = db.query(FoodPost).filter(FoodPost.id == food_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="找不到此食物")
    if status not in ("available", "completed", "expired"):
        raise HTTPException(status_code=400, detail="無效的狀態值")
    post.status = status
    db.commit()
    return {"ok": True}

@app.delete("/api/admin/foods/{food_id}")
def admin_delete_food(food_id: int, db: Session = Depends(get_db)):
    """後台：強制刪除食物（不需要 sharer_uid 驗證）。"""
    post = db.query(FoodPost).filter(FoodPost.id == food_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="找不到此食物")
    db.query(Reservation).filter(Reservation.food_post_id == food_id).delete()
    db.delete(post)
    db.commit()
    return {"ok": True}

@app.get("/api/admin/users")
def admin_get_users(db: Session = Depends(get_db)):
    """後台：取得所有使用者。"""
    users = db.query(User).order_by(User.email).all()
    result = []
    for u in users:
        share_count = db.query(FoodPost).filter(FoodPost.sharer_uid == u.firebase_uid).count()
        rsv_count   = db.query(Reservation).filter(Reservation.requester_uid == u.firebase_uid).count()
        rate = round((1 - u.no_show_count / u.total_reservations) * 100) if u.total_reservations > 0 else 100
        result.append({
            "firebase_uid":      u.firebase_uid,
            "email":             u.email,
            "display_name":      u.display_name or "",
            "total_reservations": u.total_reservations,
            "no_show_count":     u.no_show_count,
            "pickup_rate":       rate,
            "share_count":       share_count,
            "rsv_count":         rsv_count,
        })
    return result

@app.get("/api/admin/reservations")
def admin_get_reservations(db: Session = Depends(get_db)):
    """後台：取得所有預約紀錄。"""
    rows = db.query(Reservation).order_by(Reservation.created_at.desc()).all()
    result = []
    for r in rows:
        result.append({
            "id":                    r.id,
            "food_post_id":          r.food_post_id,
            "food_title":            r.food_post.title if r.food_post else "—",
            "requester_uid":         r.requester_uid,
            "requester_name":        r.requester_name or "—",
            "student_id":            r.student_id or "—",
            "quantity_reserved":     r.quantity_reserved,
            "estimated_pickup_time": r.estimated_pickup_time or "—",
            "status":                r.status,
            "created_at":            r.created_at.isoformat() if r.created_at else None,
        })
    return result

@app.get("/api/users/{uid}/requests")
def get_user_requests(uid: str, db: Session = Depends(get_db)):
    """food.html 用：取得此使用者的所有預約紀錄。"""
    reservations = (db.query(Reservation)
                      .filter(Reservation.requester_uid == uid)
                      .order_by(Reservation.created_at.desc())
                      .all())
    result = []
    for r in reservations:
        item = food_to_list_item(r.food_post)
        item["reservation_id"]        = r.id
        item["quantity_reserved"]     = r.quantity_reserved
        item["requester_name"]        = r.requester_name or ""
        item["student_id"]            = r.student_id or ""
        item["estimated_pickup_time"] = r.estimated_pickup_time or ""
        item["reservation_status"]    = r.status
        if r.status == "pending":
            item["status"] = "待領取"
        elif r.status == "completed":
            item["status"] = "已完成"
        elif r.status == "cancelled":
            item["status"] = "已取消"
        elif r.status == "no_show":
            item["status"] = "未取"
        result.append(item)
    return result

# ══════════════════════════════════════════════════════════════
# API：私訊
# ══════════════════════════════════════════════════════════════

def _display(user: User) -> str:
    if not user:
        return "未知使用者"
    return user.display_name or user.email.split("@")[0]

@app.post("/api/messages")
def send_message(
    sender_uid:   str     = Form(...),
    receiver_uid: str     = Form(...),
    content:      str     = Form(...),
    food_post_id: int     = Form(None),
    db:           Session = Depends(get_db),
):
    """傳送私訊。"""
    if sender_uid == receiver_uid:
        raise HTTPException(status_code=400, detail="不能傳訊息給自己")
    if not content.strip():
        raise HTTPException(status_code=400, detail="訊息內容不能為空")
    # 確保雙方都在 users 表裡
    if not db.query(User).filter(User.firebase_uid == sender_uid).first():
        raise HTTPException(status_code=404, detail="傳送者不存在，請重新登入")
    msg = Message(
        sender_uid=sender_uid,
        receiver_uid=receiver_uid,
        food_post_id=food_post_id,
        content=content.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"ok": True, "id": msg.id}

@app.get("/api/messages/conversations/{uid}")
def get_conversations(uid: str, db: Session = Depends(get_db)):
    """取得某使用者的所有對話列表（依最新訊息排序）。"""
    msgs = (db.query(Message)
              .filter((Message.sender_uid == uid) | (Message.receiver_uid == uid))
              .order_by(Message.created_at.desc())
              .all())

    # 以 (other_uid, food_post_id) 為 key 去重，保留最新那則
    seen = {}
    for m in msgs:
        other = m.receiver_uid if m.sender_uid == uid else m.sender_uid
        key   = (other, m.food_post_id)
        if key not in seen:
            seen[key] = m

    result = []
    for (other_uid, food_post_id), m in seen.items():
        other_user  = db.query(User).filter(User.firebase_uid == other_uid).first()
        unread      = db.query(Message).filter(
            Message.sender_uid   == other_uid,
            Message.receiver_uid == uid,
            Message.food_post_id == food_post_id,
            Message.is_read      == False,
        ).count()
        entry = {
            "other_uid":     other_uid,
            "other_name":    _display(other_user),
            "food_post_id":  food_post_id,
            "food_title":    m.food_post.title if m.food_post else None,
            "food_emoji":    m.food_post.emoji if m.food_post else None,
            "last_message":  m.content,
            "last_time":     m.created_at.isoformat(),
            "unread":        unread,
        }
        result.append(entry)

    result.sort(key=lambda x: x["last_time"], reverse=True)
    return result

@app.get("/api/messages/thread/{uid}/{other_uid}")
def get_thread(
    uid:         str,
    other_uid:   str,
    food_post_id: int = None,
    db:          Session = Depends(get_db),
):
    """取得兩人之間的訊息紀錄（可選擇性依 food_post_id 篩選）。"""
    q = db.query(Message).filter(
        ((Message.sender_uid == uid)   & (Message.receiver_uid == other_uid)) |
        ((Message.sender_uid == other_uid) & (Message.receiver_uid == uid))
    )
    if food_post_id is not None:
        q = q.filter(Message.food_post_id == food_post_id)
    msgs = q.order_by(Message.created_at.asc()).all()

    # 把對方傳給 uid 的訊息標為已讀
    for m in msgs:
        if m.receiver_uid == uid and not m.is_read:
            m.is_read = True
    db.commit()

    other_user = db.query(User).filter(User.firebase_uid == other_uid).first()
    me_user    = db.query(User).filter(User.firebase_uid == uid).first()

    # 若有 food_post_id，附帶訂單資訊
    order_info = None
    if food_post_id:
        post = db.query(FoodPost).filter(FoodPost.id == food_post_id).first()
        if post:
            rsv = db.query(Reservation).filter(
                Reservation.food_post_id  == food_post_id,
                (Reservation.requester_uid == uid) | (Reservation.requester_uid == other_uid),
                Reservation.status != "cancelled",
            ).order_by(Reservation.created_at.desc()).first()
            order_info = {
                "food_id":    post.id,
                "title":      post.title,
                "emoji":      post.emoji,
                "location":   f"{post.main_location} {post.detail_location or ''}".strip(),
                "status":     STATUS_LABEL.get(post.status, post.status),
                "image_path": post.image_path or "",
                "rsv_name":         rsv.requester_name if rsv else None,
                "rsv_student_id":   rsv.student_id if rsv else None,
                "rsv_qty":          rsv.quantity_reserved if rsv else None,
                "rsv_pickup_time":  rsv.estimated_pickup_time if rsv else None,
                "rsv_status":       rsv.status if rsv else None,
            }

    return {
        "other_uid":  other_uid,
        "other_name": _display(other_user),
        "me_name":    _display(me_user),
        "order_info": order_info,
        "messages":   [
            {
                "id":         m.id,
                "sender_uid": m.sender_uid,
                "content":    m.content,
                "is_read":    m.is_read,
                "created_at": m.created_at.isoformat(),
            }
            for m in msgs
        ],
    }

@app.get("/api/messages/unread/{uid}")
def get_unread_count(uid: str, db: Session = Depends(get_db)):
    """頁首用：取得未讀訊息數。"""
    count = db.query(Message).filter(
        Message.receiver_uid == uid,
        Message.is_read      == False,
    ).count()
    return {"unread": count}
