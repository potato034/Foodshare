from sqlalchemy import Column, Integer, String, Text

from database import Base


class FoodPost(Base):
    __tablename__ = "food_posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=False)