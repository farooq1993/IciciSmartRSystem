from sqlalchemy import Column, Integer, String, Float, DateTime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from  utils.extension import db

# db = SQLAlchemy()

# Base = db.Model   # <-- use Flask's model base

class CreateChannel(db.Model):
    __tablename__ = "channel"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_name = Column(String, nullable=False)
    channel_type = Column(String, nullable=False)
    channel_source_path = Column(String, nullable=True)
    channel_file_type = Column(String, nullable=False)
    channel_username = Column(String, nullable=False)
    channel_polling_freq = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow,nullable=True)


class DataStructureField(db.Model):
    __tablename__ = "data_structure_fields"

    id = db.Column(db.Integer, primary_key=True)

    field_name = db.Column(db.String(255), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)
    format = db.Column(db.String(100))
    min_length = db.Column(db.Integer, default=0)
    max_length = db.Column(db.Integer, default=255)
    mandatory = db.Column(db.Boolean, default=False)
    primary_key = db.Column(db.Boolean, default=False)
    regex = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



    
    