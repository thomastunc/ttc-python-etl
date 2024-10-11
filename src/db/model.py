from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FactStudentNumbers(Base):
    __tablename__ = 'fact_student_numbers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    provincie_id = Column(Integer, ForeignKey('dim_provincie.id'))
    gemeente_id = Column(Integer, ForeignKey('dim_gemeente.id'))
    instelling_id = Column(Integer, ForeignKey('dim_instelling.id'))
    opleiding_id = Column(Integer, ForeignKey('dim_opleiding.id'))
    geslacht_id = Column(String(10))

    aantal_2018 = Column(Integer)
    aantal_2019 = Column(Integer)
    aantal_2020 = Column(Integer)
    aantal_2021 = Column(Integer)
    aantal_2022 = Column(Integer)

    provincie = relationship("DimProvincie", back_populates="fact_student_numbers")
    gemeente = relationship("DimGemeente", back_populates="fact_student_numbers")
    instelling = relationship("DimInstelling", back_populates="fact_student_numbers")
    opleiding = relationship("DimOpleiding", back_populates="fact_student_numbers")


class DimProvincie(Base):
    __tablename__ = 'dim_provincie'

    id = Column(Integer, primary_key=True, autoincrement=True)
    naam = Column(String(50))

    fact_student_numbers = relationship("FactStudentNumbers", back_populates="provincie")


class DimGemeente(Base):
    __tablename__ = 'dim_gemeente'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gemeentecode = Column(String(10))
    gemeentenaam = Column(String(100))

    fact_student_numbers = relationship("FactStudentNumbers", back_populates="gemeente")


class DimInstelling(Base):
    __tablename__ = 'dim_instelling'

    id = Column(Integer, primary_key=True, autoincrement=True)
    soort_instelling = Column(String(100))
    instellingcode_actueel = Column(String(10))
    instellingsnaam_actueel = Column(String(100))
    onderdeel = Column(String(100))
    subonderdeel = Column(String(100))

    fact_student_numbers = relationship("FactStudentNumbers", back_populates="instelling")


class DimOpleiding(Base):
    __tablename__ = 'dim_opleiding'

    id = Column(Integer, primary_key=True, autoincrement=True)
    opleidingcode_actueel = Column(String(10))
    opleidingsnaam_actueel = Column(String(100))
    opleidingsvorm = Column(String(50))
    soort_diploma = Column(String(50))

    fact_student_numbers = relationship("FactStudentNumbers", back_populates="opleiding")
