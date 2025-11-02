from database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Todos(Base):
  __tablename__ = 'todos'

  id = mapped_column(Integer, primary_key=True, index=True)
  title = mapped_column(String)
  description = mapped_column(String)
  priority = mapped_column(Integer)
  complete = mapped_column(Boolean, default=False)


