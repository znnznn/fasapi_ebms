from datetime import datetime

from sqlalchemy import ForeignKey, TIMESTAMP, String, Integer, Boolean, DATE, TIME, select, func, case, and_, null, all_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.models import DefaultBase, POSITIVE_INT, POSITIVE_INT_OR_ZERO


class Capacity(DefaultBase):
    per_day: Mapped[POSITIVE_INT]
    category_autoid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # flows = relationship("Flow", back_populates="capacity", primaryjoin='Capacity.category_autoid == Flow.category_autoid', innerjoin=True)


class Flow(DefaultBase):
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    position: Mapped[POSITIVE_INT]
    color = mapped_column(String(100), default="#000000")
    need_manager: Mapped[bool] = mapped_column(Boolean, default=False)
    category_autoid: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    items = relationship("Item", back_populates="flow", primaryjoin='Flow.id == Item.flow_id', innerjoin=True)
    stages = relationship("Stage", back_populates="flow", primaryjoin='Flow.id == Stage.flow_id', innerjoin=True, order_by="Stage.position")
    # capacity = relationship("Capacity", back_populates="flows", primaryjoin='Flow.category_autoid == Capacity.category_autoid', innerjoin=True)


class Stage(DefaultBase):
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    position: Mapped[POSITIVE_INT]
    default: Mapped[bool] = mapped_column(Boolean, default=False)
    color: Mapped[str] = mapped_column(String(100), default="#000000")
    flow_id: Mapped[int] = mapped_column(ForeignKey('flow.id', ondelete="CASCADE"), nullable=True)
    flow = relationship("Flow", back_populates="stages")
    items = relationship("Item", back_populates="stage", primaryjoin='Stage.id == Item.stage_id', innerjoin=True)
    used_stages = relationship("UsedStage", back_populates="stage", primaryjoin='Stage.id == UsedStage.stage_id', innerjoin=True)

    @hybrid_property
    def status(self):
        return self.name

    @status.expression
    def status(cls):
        return select(Stage.name).where(Stage.id == Item.stage_id).correlate_except(Stage).scalar_subquery()

    @hybrid_property
    def item_ids(self):
        return {used_stage.item_id for used_stage in self.used_stages}


class Item(DefaultBase):
    order: Mapped[str] = mapped_column(String(100), nullable=True)
    origin_item: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    flow_id: Mapped[int] = mapped_column(Integer, ForeignKey('flow.id', ondelete="SET NULL"), nullable=True)
    priority: Mapped[POSITIVE_INT]
    production_date: Mapped[DATE] = mapped_column(DATE, nullable=True)
    time = mapped_column(TIME, nullable=True)
    packages: Mapped[POSITIVE_INT_OR_ZERO]
    location: Mapped[POSITIVE_INT_OR_ZERO]
    stage_id: Mapped[int] = mapped_column(Integer, ForeignKey('stage.id', ondelete="SET NULL"), nullable=True)
    flow = relationship("Flow", back_populates="items", primaryjoin='Flow.id == Item.flow_id', innerjoin=True)
    comments = relationship("Comment", back_populates="item", innerjoin=True, primaryjoin='Item.id == Comment.item_id', order_by="Comment.created_at")
    stage = relationship("Stage", back_populates="items")
    sales_order = relationship(
        'SalesOrder', back_populates="items", primaryjoin='Item.order == SalesOrder.order', foreign_keys=order)
    used_items = relationship("UsedStage", back_populates="item", primaryjoin='Item.id == UsedStage.item_id', innerjoin=True)

    @hybrid_property
    def over_due(self):
        return self.production_date < datetime.now().date()

    @over_due.expression
    def over_due(cls):
        return case(
            (and_(
                func.current_date() > cls.production_date, Stage.name != "Done"), True),
            else_=False
        ).label('over_due')

    @hybrid_property
    def stage_name(self):
        return self.stage.name

    @stage_name.expression
    def stage_name(cls):
        return select(Stage.name).where(Stage.id == cls.stage_id).correlate_except(Stage).scalar_subquery().label('stage_name')

    @hybrid_property
    def completed(self):
        return False

    @completed.expression
    def completed(cls):
        return select(case(
            (cls.stage_name == "Done", True),
            (cls.stage_name != "Done", False),
            (cls.stage_id == null(), False),
            else_=False
        ).label('completed')).correlate_except(Stage).scalar_subquery()

    @hybrid_property
    def count_comments(self):
        return len(self.comments)

    @count_comments.expression
    def count_comments(self):
        return select(
            func.count(Comment.id)
        ).where(
            Comment.item_id == self.id
        ).correlate_except(
            Comment
        ).scalar_subquery()

    @hybrid_property
    def is_scheduled(self):
        return self.production_date is not None

    @is_scheduled.expression
    def is_scheduled(cls):
        return case(
            (func.date(cls.production_date) != null(), True),
            else_=False
        ).label('is_scheduled')

    @hybrid_property
    def over_due(self):
        return self.production_date < datetime.now().date()

    @over_due.expression
    def over_due(cls):
        return case(
            (and_(
                func.current_date() > cls.production_date, cls.completed == False), True),
            else_=False
        ).label('over_due')


class Comment(DefaultBase):
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete="CASCADE"), nullable=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('item.id', ondelete="CASCADE"), nullable=True)
    text: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    item = relationship("Item", back_populates="comments")
    user = relationship("User", back_populates="comments", lazy="joined")


class SalesOrder(DefaultBase):
    order: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    packages: Mapped[POSITIVE_INT]
    location: Mapped[POSITIVE_INT]
    priority: Mapped[POSITIVE_INT]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    production_date: Mapped[DATE] = mapped_column(DATE, nullable=True)
    items = relationship(
        'Item', back_populates='sales_order', primaryjoin='SalesOrder.order==Item.order', foreign_keys='Item.order',
        innerjoin=True
    )

    @hybrid_property
    def completed(self):
        return False

    @completed.expression
    def completed(cls):
        return select(case(
            (and_(
                func.current_date() > SalesOrder.production_date, Item.completed == False), False),
            else_=False
        ))

    @hybrid_property
    def over_due(self):
        return self.production_date < datetime.now().date()

    @over_due.expression
    def over_due(cls):
        return case(
            (and_(
                func.current_date() > SalesOrder.production_date, cls.completed == False), True),
            else_=False
        ).label('over_due')

    @hybrid_property
    def is_scheduled(self):
        return self.production_date is not None

    @is_scheduled.expression
    def is_scheduled(cls):
        return cls.production_date != None


class UsedStage(DefaultBase):
    item_id: Mapped[int] = mapped_column(ForeignKey('item.id', ondelete="CASCADE"), nullable=True)
    stage_id: Mapped[int] = mapped_column(ForeignKey('stage.id', ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    item = relationship("Item", back_populates="used_items")
    stage = relationship("Stage", back_populates="used_stages")
