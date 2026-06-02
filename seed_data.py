"""
執行方式：python seed_data.py
會建立一個測試用戶和 4 筆示範食物，方便在本機開發時有資料可以看。
"""
from datetime import datetime, timedelta
from database import SessionLocal, engine
from models import Base, User, FoodPost, Location

Base.metadata.create_all(bind=engine)

LOCATIONS = [
    ("圓廳",    24.123333581992856, 120.67702034322001),
    ("圖書館",  24.1199573700127, 120.67426312470117),
    ("綜合大樓", 24.121791110686342, 120.6727722206923),
    ("校門口",  24.12389048472422, 120.67501567629624),
    ("社館大樓", 24.12082630722022, 120.67327236505437),
    ("應經一館", 24.12130850411645, 120.67847129402627),
    ("國農大樓", 24.12302693706504, 120.67864201785525),
    ("體育館",  24.118841419035764, 120.6757830791531),
    ("理學院",  24.121084939737727, 120.67743224563215),
    ("小禮堂",  24.12341936879321, 120.67775484359804),
    ("雲平樓",  24.119657988217455, 120.67259417750277),
    ("惠蓀堂",  24.123134041068685, 120.67559431073397),
    ("水保館",  24.121660354869405, 120.6773752975525),
    ("土木環工大樓", 24.12067958511147, 120.6781952335986),
]

def seed():
    db = SessionLocal()
    try:
        # 安全檢查：如果資料庫已有 FoodPost 資料，則不執行種子程式，避免覆蓋現有資料
        if db.query(FoodPost).count() > 0:
            print("資料庫已有資料，略過。")
            return

        # 建立地點資料
        for name, lat, lng in LOCATIONS:
            if not db.query(Location).filter(Location.name == name).first():
                db.add(Location(name=name, lat=lat, lng=lng))
        db.flush()

        # 建立測試用戶（uid 用假的，開發時用）
        demo_user = User(
            firebase_uid="demo_user_001",
            email="demo@smail.nchu.edu.tw",
            display_name="測試同學",
        )
        db.add(demo_user)
        db.flush()

        now = datetime.utcnow()
        sample_posts = [
            FoodPost(
                sharer_uid="demo_user_001",
                title="多出的黑糖珍珠鮮奶",
                category="飲料",
                emoji="🧋",
                description="全新未拆封，微糖微冰。買一送一多一杯喝不完。",
                quantity=1, quantity_left=1,
                main_location="校門口",
                detail_location="誠軒前",
                lat=24.1209, lng=120.6762,
                time_limit=120,   # 120 分鐘
                status="available",
                created_at=now - timedelta(minutes=5),
                expires_at=now + timedelta(minutes=120),
            ),
            FoodPost(
                sharer_uid="demo_user_001",
                title="會議多餘的排骨便當",
                category="便當",
                emoji="🍱",
                description="系辦中午開會多出 3 個排骨便當，皆全新未動，歡迎自取。",
                quantity=3, quantity_left=3,
                main_location="社館大樓",
                detail_location="4 樓系辦外桌上",
                lat=24.1239, lng=120.6777,
                time_limit=120,   # 120 分鐘
                status="available",
                created_at=now - timedelta(minutes=20),
                expires_at=now + timedelta(minutes=120),
            ),
            FoodPost(
                sharer_uid="demo_user_001",
                title="巧克力鮮奶油蛋糕",
                category="甜點",
                emoji="🍰",
                description="慶生切剩下的半個蛋糕，一直冰在冰箱，保存良好。",
                quantity=1, quantity_left=1,
                main_location="圖書館",
                detail_location="一樓交誼廳",
                lat=24.1218, lng=120.6769,
                time_limit=360,   # 360 分鐘 = 6 小時
                status="available",
                created_at=now - timedelta(hours=1),
                expires_at=now + timedelta(minutes=360),
            ),
            FoodPost(
                sharer_uid="demo_user_001",
                title="多買的洪瑞珍三明治",
                category="其他",
                emoji="🥪",
                description="早上不小心重複多買了，期限到今天晚上，希望有人能帶走它。",
                quantity=1, quantity_left=1,
                main_location="綜合大樓",
                detail_location="一樓大廳桌上",
                lat=24.1237, lng=120.6798,
                time_limit=720,   # 720 分鐘 = 12 小時
                status="available",
                created_at=now - timedelta(hours=2),
                expires_at=now + timedelta(minutes=720),
            ),
            FoodPost(
                sharer_uid="demo_user_001",
                title="阿蓁的高纖豆漿",
                category="飲料",
                emoji="🥤",
                description="在全家剛買的高纖豆漿，還沒喝完，想說放在冰箱裡明天再喝，結果忘了它的存在，現在想說乾脆分享給需要的人好了。",
                quantity=1, quantity_left=1,
                main_location="應經一館",
                detail_location="系學會辦公室",
                lat=24.1237, lng=120.6798,
                time_limit=720,   # 720 分鐘 = 12 小時
                status="available",
                image_path="/images/soymilk.jpg",
                created_at=now - timedelta(hours=24),
                expires_at=now + timedelta(minutes=720),
            ),
        ]
        db.add_all(sample_posts)
        db.commit()
        print("測試資料建立完成！共 5 筆食物。")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
