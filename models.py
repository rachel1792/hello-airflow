import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app import db


class Xwords(db.Model):
    __tablename__ = 'xwords'

    id = sa.Column(UUID, default=lambda: uuid4().hex, primary_key=True)
    created_at = sa.Column(
        sa.TIMESTAMP(timezone=True),
        server_default=sa.func.now(),
        default=sa.func.now(),
        nullable=False
    )
    clue = sa.Column(sa.String(30), nullable=False)
    answer = sa.Column(sa.String(150), nullable=False)
    debut = sa.Column(sa.Boolean(), default=sa.false(), server_default=sa.false())
    unique = sa.Column(sa.Boolean(), default=sa.false(), server_default=sa.false())

    def __repr__(self):
        return '<clue: {}, answer: {}>'.format(self.clue, self.answer)
