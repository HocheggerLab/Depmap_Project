from datetime import datetime

from marshmallow_sqlalchemy import fields

from config import db, ma
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("gene.id"))
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class NoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Note
        load_instance = True
        sqla_session = db.session
        include_fk = True

class Gene(db.Model):
    __tablename__ = "gene"
    id = db.Column(db.Integer, primary_key=True)
    gene = db.Column(db.String(32), unique=True)
    corr_gene = db.Column(db.String(32))
    pearson_r = db.Column(db.Float)
    spearman_r = db.Column(db.Float)
    mean_diff = db.Column(db.Float)
    pearson_p = db.Column(db.Float)
    spearman_p = db.Column(db.Float)
    mean_diff_p = db.Column(db.Float)
    largest_comm = db.Column(db.Boolean)
    type = db.Column(db.String(64))
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    notes = db.relationship(
        "Note",
        backref="gene",
        cascade="all, delete, delete-orphan",
        single_parent=True,
        order_by="desc(Note.timestamp)",
    )

class GeneSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Gene
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    notes = ma.Nested(NoteSchema, many=True)

note_schema = NoteSchema()
gene_schema = GeneSchema()
genes_schema = GeneSchema(many=True)
