#!/usr/bin/env python3
"""
This is the base_model inherited by models
contains:
    - methods:
        - save
        - delete
        - to_dict
        - __repr__
        - __str__
    - attributes:
        - id
        - created_at
        - updated_at
"""

import uuid

from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class BaseModel:
    """
    This class defines all common attributes/methods
    for other classes that would inherit it.
    """

    id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


    def __str__(self):
        """
        This method defines the property of the class in a string fmt
        Return:
            returns a string containing of class name, id and dict
        """
        return f"[{type(self).__name__}] ({self.id}) {self.__dict__}"

    def __repr__(self):
        """
        Return:
            returns a string representation of the calss

        """
        return f"[{type(self).__name__}] ({self.id}) {self.__dict__}"

    def save(self):
        """This methods updates the updated_at attribute"""
        self.updated_at = datetime.now()

    def to_dict(self):
        """
        This method creates a dictionary representation of the class

        Return:
            returns a dict rep of the class
        """

        base_dict = dict(self.__dict__)
        base_dict["__class__"] = str(type(self).__name__)
        base_dict["created_at"] = self.created_at.isoformat()
        
        base_dict["updated_at"] = self.updated_at.isoformat()

        return base_dict
