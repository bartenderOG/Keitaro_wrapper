from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StreamOfferSnapshot(Base):
    __tablename__ = "stream_offer_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)

    stream_id: Mapped[int] = mapped_column(
        ForeignKey("streams.id"),
        nullable=False,
    )

    offer_id: Mapped[int] = mapped_column(
        ForeignKey("offers.id"),
        nullable=False,
    )

    weight: Mapped[int] = mapped_column(nullable=False)

    is_pinned: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
