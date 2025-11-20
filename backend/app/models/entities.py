"""
Domain database models for the hiking simulator backend.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DemoProfile(Base):
    """
    Temporary player profile captured after the US-03 questionnaire.
    """

    __tablename__ = "demo_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    total_xp: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    level: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    user_vector_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    genai_welcome_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    unlocked_routes_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    souvenirs: Mapped[list[Souvenir]] = relationship(
        "Souvenir",
        back_populates="demo_profile",
        cascade="all, delete-orphan",
    )
    feedback_entries: Mapped[list[ProfileFeedback]] = relationship(
        "ProfileFeedback",
        back_populates="demo_profile",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<DemoProfile id={self.id} level={self.level} total_xp={self.total_xp}>"


class Route(Base):
    """
    Core route metadata sourced from Outdooractive APIs plus custom storytelling fields.
    """

    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    length_meters: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    short_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    elevation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gpx_data_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    xp_required: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    base_xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    story_prologue_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    story_prologue_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    story_epilogue_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    breakpoints: Mapped[list[Breakpoint]] = relationship(
        "Breakpoint",
        back_populates="route",
        cascade="all, delete-orphan",
        order_by="Breakpoint.order_index",
    )
    souvenirs: Mapped[list[Souvenir]] = relationship(
        "Souvenir",
        back_populates="route",
        cascade="all, delete-orphan",
    )
    feedback_entries: Mapped[list[ProfileFeedback]] = relationship(
        "ProfileFeedback",
        back_populates="route",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Route id={self.id} title={self.title!r}>"


class Breakpoint(Base):
    """
    Route progress nodes and story chapters.
    """

    __tablename__ = "breakpoints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    poi_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    poi_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    main_quest_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    side_plot_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    route: Mapped[Route] = relationship("Route", back_populates="breakpoints")
    mini_quests: Mapped[list[MiniQuest]] = relationship(
        "MiniQuest",
        back_populates="breakpoint",
        cascade="all, delete-orphan",
        order_by="MiniQuest.id",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Breakpoint id={self.id} route_id={self.route_id} idx={self.order_index}>"


class MiniQuest(Base):
    """
    Optional mini quests that fire at a specific breakpoint.
    """

    __tablename__ = "mini_quests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    breakpoint_id: Mapped[int] = mapped_column(
        ForeignKey("breakpoints.id", ondelete="CASCADE"),
        nullable=False,
    )
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    breakpoint: Mapped[Breakpoint] = relationship("Breakpoint", back_populates="mini_quests")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<MiniQuest id={self.id} breakpoint_id={self.breakpoint_id}>"


class Souvenir(Base):
    """
    Completion record capturing XP gain and AI generated summaries.
    """

    __tablename__ = "souvenirs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    demo_profile_id: Mapped[int] = mapped_column(
        ForeignKey("demo_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    total_xp_gained: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    genai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    xp_breakdown_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    demo_profile: Mapped[DemoProfile] = relationship("DemoProfile", back_populates="souvenirs")
    route: Mapped[Route] = relationship("Route", back_populates="souvenirs")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Souvenir id={self.id} profile_id={self.demo_profile_id} route_id={self.route_id}>"


class ProfileFeedback(Base):
    """
    👎 feedback captured from US-08 to drive adaptive re-ranking.
    """

    __tablename__ = "profile_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    demo_profile_id: Mapped[int] = mapped_column(
        ForeignKey("demo_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(100), nullable=False)

    demo_profile: Mapped[DemoProfile] = relationship("DemoProfile", back_populates="feedback_entries")
    route: Mapped[Route] = relationship("Route", back_populates="feedback_entries")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<ProfileFeedback id={self.id} reason={self.reason!r}>"


