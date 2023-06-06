from db import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    # The lazy says that we won't fetch them until we need to pull them
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic")
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
