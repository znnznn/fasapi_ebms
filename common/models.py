from typing import Annotated

from sqlalchemy import MetaData, CheckConstraint, Integer
from sqlalchemy.orm import DeclarativeBase, as_declarative, declared_attr, Mapped, mapped_column


POSITIVE_INT = Annotated[int, mapped_column(Integer, CheckConstraint('VALUE > 0'), default=0)]


class EBMSBase(DeclarativeBase):
    __bind_key__ = 'ebms'
    __abstract__ = True
    __table_args__ = {'extend_existing': True}

    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.upper()


@as_declarative(metadata=MetaData())
class DefaultBase:
    __bind_key__ = 'default'
    __abstract__ = True

    metadata = MetaData()
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
