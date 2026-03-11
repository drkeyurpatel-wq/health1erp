from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID


class TenantMixin:
    """Mixin that adds facility_id to any model for multi-tenancy filtering."""

    facility_id = Column(
        UUID(as_uuid=True),
        ForeignKey("facilities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Ensure the facility_id index is named uniquely per table
        if hasattr(cls, "__tablename__"):
            idx_name = f"ix_{cls.__tablename__}_facility_id"
            # Add index via table args if not already present
            existing = getattr(cls, "__table_args__", None)
            new_idx = Index(idx_name, "facility_id")
            if existing is None:
                cls.__table_args__ = (new_idx,)
            elif isinstance(existing, tuple):
                cls.__table_args__ = (*existing, new_idx)
            elif isinstance(existing, dict):
                cls.__table_args__ = (new_idx, existing)
