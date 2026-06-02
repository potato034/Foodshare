"""
執行方式：python seed_data.py
會建立一個測試用戶和 4 筆示範食物，方便在本機開發時有資料可以看。
"""
from datetime import datetime, timedelta
from database import SessionLocal, engine
from models import Base, User, FoodPost, Location, Feedback, UserMap

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
    ("女宿門口",24.123637321954288, 120.68018289570077),
    ("森林系二館",24.122373951354714, 120.67764835676105),
    ("生物產業機電大樓",24.119951588379713, 120.67841844754982),
    ("機械館",24.12009980002414, 120.67728171996379),
    ("化學系館",24.120540199311467, 120.67681774951343),
    ("作物科學大樓",24.120540199311467, 120.67681774951343),
    ("農環大樓",24.121238906614042, 120.67543511760267),
    ("中興湖",24.121299646503104, 120.67438358726238),
    ("萬年樓",24.12287519150871, 120.67279452413733),
    ("行政大樓",24.12234277849381, 120.67427324445136),
    ("化工暨材料大樓",24.122582905780533, 120.67540974027844),
    ("電機大樓",24.122477753307198, 120.67628824458723),
    ("資訊科學大樓",24.121249007593324, 120.67709323708483),
    ("動科大樓",24.11870675937772, 120.67847788698842),
    ("排球場",24.117937633716803, 120.67470074748017),
    ("中興奶茶",24.11885857607826, 120.67395262114684),
    ("中興舊男宿",24.11894522217568, 120.67271348401464),
    ("操場",24.118115241249566, 120.67326809782078),
    ("籃球場",24.118625999386357, 120.67450723494352),
    ("人文大樓",24.12336119987608, 120.67276883881863)
]

def seed():
    db = SessionLocal()
    try:
        # 建立測試回饋資料 (即便已有食物資料也執行，確保回饋表存在並有測試資料)
        if db.query(Feedback).count() == 0:
            db.add_all([
                Feedback(name="張同學", email="s109012345@smail.nchu.edu.tw", content="這個食物共享平台真的太棒了，省了好多餐費！"),
                Feedback(name="李同學", email="s110054321@smail.nchu.edu.tw", content="希望可以新增地圖篩選類別的功能，謝謝組員！")
            ])
            db.commit()
            print("回饋測試資料建立完成！共 2 筆回饋。")

        # 建立測試用戶的 UserMap 對照 (即便已有食物資料也執行，確保對照表存在並有測試資料)
        if db.query(UserMap).count() == 0:
            db.add(UserMap(firebase_uid="demo_user_001", ordered_id="demo_user_001"))
            db.commit()
            print("使用者對照測試資料建立完成！")

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
                quantity=2, quantity_left=1,
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
