from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import Base, BaseModel


class RefundRequest(Base, BaseModel):
    __tablename__ = "refund_requests"

    thread_id: Mapped[str] = mapped_column(String(128), nullable=False)
    order_id: Mapped[str] = mapped_column(String(64), nullable=False)
    requester_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="requested")


class RefundNotFoundLog(Base, BaseModel):
    __tablename__ = "refund_not_found_logs"

    thread_id: Mapped[str] = mapped_column(String(128), nullable=False)
    message_id: Mapped[str] = mapped_column(String(128), nullable=False)
    provided_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)


