from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    # Relationships
    storage_units = relationship("StorageUnit", back_populates="user")
    vehicles = relationship("Vehicle", back_populates="user")

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"
