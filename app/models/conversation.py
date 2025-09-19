from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import Base, BaseModel


class Conversation(Base, BaseModel):
    __tablename__ = "conversations"

    thread_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    state_json: Mapped[str] = mapped_column(Text, nullable=False, default='{}')


