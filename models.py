from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Location(Base):
    """校園地點與對應 GPS 座標。"""
    __tablename__ = "locations"

    id   = Column(Integer,    primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    lat  = Column(Float,      nullable=False)
    lng  = Column(Float,      nullable=False)


class User(Base):
    """Firebase 登入的使用者，用 firebase_uid 當主鍵。"""
    __tablename__ = "users"

    firebase_uid     = Column(String(128), primary_key=True)
    email            = Column(String(255), nullable=False)
    display_name     = Column(String(100), nullable=True)
    # 取貨率統計
    total_reservations = Column(Integer, nullable=False, default=0)
    no_show_count      = Column(Integer, nullable=False, default=0)

    food_posts   = relationship("FoodPost",    back_populates="sharer",    foreign_keys="FoodPost.sharer_uid")
    reservations = relationship("Reservation", back_populates="requester", foreign_keys="Reservation.requester_uid")


class FoodPost(Base):
    """一筆食物分享貼文。"""
    __tablename__ = "food_posts"

    id              = Column(Integer,     primary_key=True, autoincrement=True)
    sharer_uid      = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False)

    title           = Column(String(100), nullable=False)
    category        = Column(String(20),  nullable=False)
    emoji           = Column(String(10),  nullable=False, default="🍱")
    description     = Column(Text,        nullable=True)
    quantity        = Column(Integer,     nullable=True)   # 總份數
    quantity_left   = Column(Integer,     nullable=True)   # 剩餘份數（預約後扣除）

    main_location   = Column(String(50),  nullable=False)
    detail_location = Column(String(100), nullable=True)
    lat             = Column(Float,       nullable=True)
    lng             = Column(Float,       nullable=True)

    time_limit      = Column(Integer,     nullable=False, default=120)  # 單位：分鐘
    status          = Column(String(20),  nullable=False, default="available")
    # available → completed / expired

    image_path      = Column(String(255), nullable=True)
    created_at      = Column(DateTime,    nullable=False, default=datetime.utcnow)
    expires_at      = Column(DateTime,    nullable=True)

    sharer       = relationship("User",        back_populates="food_posts", foreign_keys=[sharer_uid])
    reservations = relationship("Reservation", back_populates="food_post")


class Reservation(Base):
    """某位使用者預約某一筆食物分享。"""
    __tablename__ = "reservations"

    id                    = Column(Integer,     primary_key=True, autoincrement=True)
    food_post_id          = Column(Integer,     ForeignKey("food_posts.id"),      nullable=False)
    requester_uid         = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False)
    status                = Column(String(20),  nullable=False, default="pending")
    # pending → completed / cancelled / no_show

    quantity_reserved     = Column(Integer,     nullable=False, default=1)
    requester_name        = Column(String(50),  nullable=True)   # 姓名
    student_id            = Column(String(20),  nullable=True)   # 學號
    estimated_pickup_time = Column(String(50),  nullable=True)   # 預計領取時間（文字描述）

    created_at            = Column(DateTime,    nullable=False, default=datetime.utcnow)

    food_post = relationship("FoodPost",  back_populates="reservations")
    requester = relationship("User",      back_populates="reservations", foreign_keys=[requester_uid])


class Message(Base):
    """兩個使用者之間的私訊，可選擇性關聯到一筆食物貼文。"""
    __tablename__ = "messages"

    id           = Column(Integer,     primary_key=True, autoincrement=True)
    sender_uid   = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False)
    receiver_uid = Column(String(128), ForeignKey("users.firebase_uid"), nullable=False)
    food_post_id = Column(Integer,     ForeignKey("food_posts.id"), nullable=True)
    content      = Column(Text,        nullable=False)
    is_read      = Column(Boolean,     nullable=False, default=False)
    created_at   = Column(DateTime,    nullable=False, default=datetime.utcnow)

    sender    = relationship("User",     foreign_keys=[sender_uid])
    receiver  = relationship("User",     foreign_keys=[receiver_uid])
    food_post = relationship("FoodPost", foreign_keys=[food_post_id])


class Feedback(Base):
    """使用者提交的意見回饋。"""
    __tablename__ = "feedbacks"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    name       = Column(String(100), nullable=True)
    email      = Column(String(255), nullable=True)
    content    = Column(Text,        nullable=False)
    created_at = Column(DateTime,    nullable=False, default=datetime.utcnow)
