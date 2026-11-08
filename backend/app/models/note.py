from sqlalchemy import Table, Column, String, Text, Boolean, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
from app.extensions import db

# Junction Table for Many-to-Many Note <-> Tag Relationship
note_tag_association = Table(
    "note_tag_association",
    db.Model.metadata,
    Column("note_id", String(36), ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("note_tags.id", ondelete="CASCADE"), primary_key=True),
)


class NoteTag(BaseModel):
    """Categorical tags for knowledge base notes."""
    __tablename__ = "note_tags"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    color_hex: Mapped[str] = mapped_column(
        String(10),
        default="#6C63FF",
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="note_tags")
    notes: Mapped[list["Note"]] = relationship(
        "Note",
        secondary=note_tag_association,
        back_populates="tags"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_note_tag_user_name"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "color_hex": self.color_hex,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Note(BaseModel):
    """Personal knowledge base entries and markdown notes."""
    __tablename__ = "notes"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False
    )
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notes")
    tags: Mapped[list[NoteTag]] = relationship(
        "NoteTag",
        secondary=note_tag_association,
        back_populates="notes"
    )

    __table_args__ = (
        Index("ix_notes_user_pinned", "user_id", "is_pinned"),
        Index("ix_notes_user_archived", "user_id", "is_archived"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "is_pinned": self.is_pinned,
            "is_archived": self.is_archived,
            "tags": [t.to_dict() for t in self.tags] if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

