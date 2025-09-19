from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, Enum as SQLAlchemyEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_model import Base, BaseModel
import enum


class EmailCategory(enum.Enum):
    question = "question"
    refund = "refund"
    other = "other"


class EmailDirection(enum.Enum):
    inbound = "inbound"
    outbound = "outbound"

class EmailImportance(enum.Enum):
        low = "low"
        medium = "medium"
        high = "high"

class Email(Base, BaseModel):
    __tablename__ = "emails"

    gmail_message_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    thread_id: Mapped[str] = mapped_column(String(128), nullable=False)
    account_email: Mapped[str] = mapped_column(String(255), nullable=False)
    from_email: Mapped[str] = mapped_column(String(255), nullable=True)
    subject: Mapped[str] = mapped_column(String(512), nullable=True)
    text_body: Mapped[str] = mapped_column(Text, nullable=True)
    html_body: Mapped[str] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Classification results
    category: Mapped[EmailCategory | None] = mapped_column(SQLAlchemyEnum(EmailCategory), nullable=True) 
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Importance after RAG
    importance: Mapped[EmailImportance | None] = mapped_column(SQLAlchemyEnum(EmailImportance), nullable=True)

    # Whether this email has been handled (answered or routed) by the system
    handled: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    # Direction of the email (incoming from user vs our sent reply)
    direction: Mapped[EmailDirection] = mapped_column(
        SQLAlchemyEnum(EmailDirection), nullable=True, default=EmailDirection.inbound
    )
 