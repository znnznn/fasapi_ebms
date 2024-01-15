from datetime import datetime

from sqlalchemy import ForeignKey, TIMESTAMP, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import DefaultBase


class Base(DefaultBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Capacity(DefaultBase):
    __tablename__ = "capacity"

    per_day: Mapped[int] = mapped_column()
    category_autoid: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)


class Flow(Base):
    __tablename__ = "flow"

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    position: Mapped[int] = mapped_column(Integer)
    color = mapped_column(String(100), default="#000000")
    need_manager: Mapped[bool] = mapped_column(Boolean)
    category_autoid: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    items = relationship("Item", back_populates="flow")
    stages = relationship("Stage", back_populates="flow")


class Stage(Base):
    __tablename__ = "stage"

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000))
    position: Mapped[int] = mapped_column(Integer)
    default: Mapped[bool] = mapped_column(Boolean)
    color: Mapped[str] = mapped_column(String(100), default="#000000")
    flow_id: Mapped[int] = mapped_column(ForeignKey('flow.id'))
    flow = relationship("Flow", back_populates="stages", innerjoin=True, primaryjoin='Stage.flow_id == Flow.id')


class Item(Base):
    __tablename__ = "item"

    order: Mapped[str] = mapped_column(String(100))
    origin_item: Mapped[str] = mapped_column(String(100))
    flow_id: Mapped[int] = mapped_column(Integer, ForeignKey('flow.id'))
    priority: Mapped[int] = mapped_column(Integer)
    production_date: Mapped[datetime] = mapped_column(TIMESTAMP)
    stage: Mapped[int] = mapped_column(Integer, ForeignKey('stages_stage.id'))
    flow = relationship("Flow", back_populates="items")
    comments = relationship("Comment", back_populates="item")


class Comment(Base):
    __tablename__ = "comment"

    user: Mapped[int] = mapped_column(ForeignKey('user.id'))
    item_id: Mapped[int] = mapped_column(ForeignKey('item.id'))
    text: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    item = relationship("Item", backref="comments")
