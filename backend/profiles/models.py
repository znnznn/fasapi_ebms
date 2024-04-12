from datetime import datetime

from sqlalchemy import Boolean, TIMESTAMP, ForeignKey, String, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from common.models import DefaultBase


class CompanyProfile(DefaultBase):
    working_weekend: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, onupdate=func.current_timestamp(), nullable=True)


class UserProfile(DefaultBase):
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now, onupdate=func.current_timestamp(), nullable=True)
    creator: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"))
    page: Mapped[str] = mapped_column(String(255))
    show_columns: Mapped[str] = mapped_column(String(255))
    user = relationship("User", back_populates="user_profiles")
