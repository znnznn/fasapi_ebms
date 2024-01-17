from datetime import datetime

from sqlalchemy import ForeignKey, TIMESTAMP, String, Integer, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.models import DefaultBase, POSITIVE_INT


class Capacity(DefaultBase):
    per_day: Mapped[POSITIVE_INT]
    category_autoid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class Flow(DefaultBase):
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    position: Mapped[POSITIVE_INT]
    color = mapped_column(String(100), default="#000000")
    need_manager: Mapped[bool] = mapped_column(Boolean)
    category_autoid: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    items = relationship("Item", back_populates="flow", primaryjoin='Flow.id == Item.flow_id', innerjoin=True)
    stages = relationship("Stage", back_populates="flow", primaryjoin='Flow.id == Stage.flow_id', innerjoin=True)


class Stage(DefaultBase):
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    position: Mapped[POSITIVE_INT]
    default: Mapped[bool] = mapped_column(Boolean)
    color: Mapped[str] = mapped_column(String(100), default="#000000")
    flow_id: Mapped[int] = mapped_column(ForeignKey('flow.id', ondelete="CASCADE"))
    flow = relationship("Flow", back_populates="stages")


class Item(DefaultBase):
    order: Mapped[str] = mapped_column(String(100))
    origin_item: Mapped[str] = mapped_column(String(100))
    flow_id: Mapped[int] = mapped_column(Integer, ForeignKey('flow.id'))
    priority: Mapped[POSITIVE_INT]
    production_date: Mapped[datetime] = mapped_column(TIMESTAMP)
    stage: Mapped[int] = mapped_column(Integer, ForeignKey('stage.id', ondelete="SET NULL"))
    flow = relationship("Flow", back_populates="items")
    comments = relationship("Comment", back_populates="item", innerjoin=True, primaryjoin='Item.id == Comment.item_id')


class Comment(DefaultBase):
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"))
    item_id: Mapped[int] = mapped_column(ForeignKey('item.id'))
    text: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    item = relationship("Item", back_populates="comments")


class SalesOrder(DefaultBase):
    order: Mapped[str] = mapped_column(String(100))
    packages: Mapped[POSITIVE_INT]
    location: Mapped[POSITIVE_INT]
    priority: Mapped[POSITIVE_INT]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    production_date: Mapped[datetime] = mapped_column(TIMESTAMP)
