from database import SessionLocal
from models import FoodPost

def seed_food_posts():
    db = SessionLocal()

    try:
        # 避免重複新增測試資料
        existing_count = db.query(FoodPost).count()

        if existing_count > 0:
            print("資料庫已有資料，未新增測試資料。")
            return

        sample_posts = [
            FoodPost(
                title="即期麵包",
                description="今天晚上前可領取，地點在校門附近。",
                image_path="/images/sample_bread.jpg"
            ),
            FoodPost(
                title="便當一份",
                description="未拆封，下午五點前可領取。",
                image_path="/images/sample_bento.jpg"
            ),
            FoodPost(
                title="水果盒",
                description="包含蘋果與芭樂，冷藏保存。",
                image_path="/images/sample_fruit.jpg"
            ),
        ]

        db.add_all(sample_posts)
        db.commit()

        print("測試資料新增成功。")

    finally:
        db.close()


if __name__ == "__main__":
    seed_food_posts()