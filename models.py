from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Float, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Panel(Base):
    __tablename__ = "panels"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    width: Mapped[float] = mapped_column(Float, default=8)
    height: Mapped[float] = mapped_column(Float, default=10)
    reservations: Mapped[list["Reservation"]] = relationship(back_populates="panel")

class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(primary_key=True)
    panel_id: Mapped[int] = mapped_column(ForeignKey("panels.id", ondelete="RESTRICT"), index=True)
    project_name: Mapped[str] = mapped_column(String(150), index=True)
    purchase_order: Mapped[str | None] = mapped_column(String(80), nullable=True)
    requester: Mapped[str] = mapped_column(String(80))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    panel: Mapped[Panel] = relationship(back_populates="reservations")
