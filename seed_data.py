"""
執行方式：python seed_data.py
會建立一個測試用戶和 4 筆示範食物，方便在本機開發時有資料可以看。
"""
from datetime import datetime, timedelta
from database import SessionLocal, engine
from models import Base, User, FoodPost, Location

Base.metadata.create_all(bind=engine)

LOCATIONS = [
    ("圓廳",    24.1232, 120.6776),
    ("圖書館",  24.1218, 120.6769),
    ("綜合大樓", 24.1237, 120.6798),
    ("校門口",  24.1209, 120.6762),
    ("社館大樓", 24.1239, 120.6777),
    ("應經一館", 24.1225, 120.6771),
    ("國農大樓", 24.1244, 120.6783),
    ("體育館",  24.1220, 120.6790),
    ("理學院",  24.1228, 120.6768),
    ("小禮堂",  24.1215, 120.6781),
    ("雲平樓",  24.1230, 120.6795),
    ("惠蓀堂",  24.1222, 120.6785),
    ("水保館",  24.1248, 120.6780),
    ("農業陳列館", 24.1235, 120.6760),
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
        ]
        db.add_all(sample_posts)
        db.commit()
        print("測試資料建立完成！共 4 筆食物。")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
