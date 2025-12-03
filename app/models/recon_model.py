from sqlalchemy import Column, Integer, String, Float, DateTime
from utils.database import Base

class ReconResult(Base):
    __tablename__ = "recon_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tran_id = Column(String(255))
    source_amount = Column(Float)
    target_amount = Column(Float)
    status = Column(String(50))        # MATCHED / UNMATCHED / PENDING
    reason = Column(String(500))
