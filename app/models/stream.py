from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Stream(Base):
    __tablename__ = "streams"

    id: Mapped[int] = mapped_column(primary_key=True)

    keitaro_id: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
    )

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    position: Mapped[int] = mapped_column(
        nullable=False,
    )

    has_unpublished_changes: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
