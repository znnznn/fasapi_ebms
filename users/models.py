from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, MetaData, Table, Boolean, func, Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column, Mapped, declared_attr, relationship
from sqlalchemy_utils import ChoiceType, EmailType

from common.constants import Role
from common.models import DefaultBase


class User(DefaultBase):
    first_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(ChoiceType(choices=Role.ROLE_CHOICES), default=Role.WORKER, nullable=False)
    email: Mapped[str] = mapped_column(EmailType(length=254), unique=True, index=True, nullable=False)
    date_joined: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comments = relationship("Comment", back_populates="user", innerjoin=True, primaryjoin='User.id == Comment.user_id')
    category = relationship("CategoryAccess", back_populates="user", innerjoin=True, primaryjoin='User.id == CategoryAccess.user_id')

    @hybrid_property
    def role_name(self):
        return self.role.value


class CategoryAccess(DefaultBase):
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"))
    category_autoid: Mapped[str] = mapped_column(String(100), nullable=False)
    user = relationship("User", back_populates="category")
