from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, MetaData, Table, Boolean, func
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy_utils import ChoiceType, EmailType

from common.constants import Role
from database import DefaultBase


class Base(DefaultBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


# metadata = MetaData()

# user = Table(
#     "users_user",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("first_name", String),
#     Column("last_name", String),
#     Column("is_staff", Boolean, default=False),
#     Column("email", EmailType, nullable=False, unique=True),
#     Column("role", ChoiceType(Role.ROLE_CHOICES), default=Role.WORKER),
#     Column("date_joined", TIMESTAMP, default=datetime.utcnow()),
#     Column("password", String),
#     Column("is_active", Boolean, default=True),
#     Column("is_superuser", Boolean, default=False),
# )
#
# message = Table(
#     "users_categoryaccess",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("user_id", ForeignKey("user.id")),
#     Column("category", ForeignKey("category.id")),
#     Column("created_at", TIMESTAMP, default=datetime.utcnow()),
#
# )


class User(Base):
    __tablename__ = "user"

    first_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(ChoiceType(Role.ROLE_CHOICES), default=Role.WORKER, nullable=False)
    email: Mapped[str] = mapped_column(EmailType(length=254), unique=True, index=True, nullable=False)
    date_joined: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
