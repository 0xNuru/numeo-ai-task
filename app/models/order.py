from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import Base, BaseModel


class Order(Base, BaseModel):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    refund_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


