import pandas as pd
import click
from sqlalchemy.orm import sessionmaker
from src.db.build import get_engine
from src.db.model import DimGemeente, DimProvincie, DimOpleiding, DimInstelling, FactStudentNumbers


def run_etl(path):
    """Leest het Parquet-bestand en voert het ETL-proces uit."""
    df = pd.read_parquet(path)

    # Maak een sessie aan voor de database
    Session = sessionmaker(bind=get_engine())
    session = Session()

    try:
        for index, row in df.iterrows():
            # Zoek of maak de provincie
            provincie = session.query(DimProvincie).filter_by(naam=row['PROVINCIE']).first()
            if not provincie:
                provincie = DimProvincie(
                    naam=row['PROVINCIE']
                )
                session.add(provincie)
                session.commit()  # Commit zodat de id beschikbaar is

            # Zoek of maak de gemeente
            gemeente = session.query(DimGemeente).filter_by(gemeentecode=row['GEMEENTENUMMER']).first()
            if not gemeente:
                gemeente = DimGemeente(
                    gemeentecode=row['GEMEENTENUMMER'],
                    gemeentenaam=row['GEMEENTENAAM']
                )
                session.add(gemeente)
                session.commit()

            # Zoek of maak de instelling
            instelling = session.query(DimInstelling).filter_by(
                instellingcode_actueel=row['INSTELLINGSCODE ACTUEEL']).first()
            if not instelling:
                instelling = DimInstelling(
                    instellingcode_actueel=row['INSTELLINGSCODE ACTUEEL'],
                    instellingsnaam_actueel=row['INSTELLINGSNAAM ACTUEEL'],
                    soort_instelling=row['SOORT INSTELLING'],
                    onderdeel=row['ONDERDEEL'],
                    subonderdeel=row['SUBONDERDEEL']
                )
                session.add(instelling)
                session.commit()

            # Zoek of maak de opleiding
            opleiding = session.query(DimOpleiding).filter_by(
                opleidingcode_actueel=row['OPLEIDINGSCODE ACTUEEL']).first()
            if not opleiding:
                opleiding = DimOpleiding(
                    opleidingcode_actueel=row['OPLEIDINGSCODE ACTUEEL'],
                    opleidingsnaam_actueel=row['OPLEIDINGSNAAM ACTUEEL'],
                    opleidingsvorm=row['OPLEIDINGSVORM'],
                    soort_diploma=row['SOORT DIPLOMA']
                )
                session.add(opleiding)
                session.commit()

            # Converteer de waarden voor aantal_2018 tot aantal_2022 naar integers
            for year in range(2018, 2023):
                fact = FactStudentNumbers(
                    provincie_id=provincie.id,
                    gemeente_id=gemeente.id,
                    instelling_id=instelling.id,
                    opleiding_id=opleiding.id,
                    geslacht_id=row['GESLACHT'],
                    aantal=convert_to_int(row[str(year)]),
                    jaar=year
                )
                session.add(fact)

            if int(index) % 1000 == 0:
                session.commit()

        # Commit de transactie voor alle facts
        session.commit()
        click.echo("ETL-proces voltooid en data succesvol naar de database weggeschreven.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def convert_to_int(value):
    """Converteer de waarde naar een integer, vervang '<5' door None of een logische waarde."""
    if isinstance(value, str) and '<' in value:
        return 0  # Of gebruik een andere logische waarde zoals None of 4
    try:
        return int(value)
    except ValueError:
        return None  # Als de conversie naar int mislukt, geef None terug
