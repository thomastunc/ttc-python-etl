from fastapi import FastAPI, HTTPException, Query
from src.db.build import get_engine
from src.db.model import FactStudentNumbers, DimProvincie, DimGemeente, DimInstelling, DimOpleiding
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.get("/")
async def main():
    return {"message": "Hello, Thomas!"}


@app.get("/provinces")
async def get_provinces():
    """
    Endpoint om alle provincies items op te halen.
    """
    try:
        Session = sessionmaker(bind=get_engine())
        with Session() as session:
            provincies = session.query(DimProvincie).all()

        if not provincies:
            raise HTTPException(status_code=404, detail="No provinces found.")

        return provincies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/province")
async def get_province(name: str = Query(..., description="De naam van de provincie")):
    """
    Endpoint om een provincie op te halen op basis van de naam.
    """
    try:
        Session = sessionmaker(bind=get_engine())
        with Session() as session:
            provincie = session.query(DimProvincie).filter(DimProvincie.naam == name).first()

        if not provincie:
            raise HTTPException(status_code=404, detail=f"Province with name '{name}' not found.")

        return provincie
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/students")
def get_students(
        limit: int = Query(
            100,
            ge=1,
            le=1000,
            description="Aantal records dat opgehaald moet worden (1-1000)"
        ),  # Validatie: minimum 1, maximum 1000
        offset: int = Query(
            0,
            ge=0,
            description="Aantal records om over te slaan (minimaal 0)"
        ),  # Validatie: minimaal 0
        provincie_naam: str = Query(
            None,
            description="De naam van de provincie"
        ),
        instelling_naam: str = Query(
            None,
            description="De naam van de instelling"
        )
):
    # Extra validatie in het geval dat Query() niet voldoende is
    if not isinstance(limit, int) or not isinstance(offset, int):
        raise HTTPException(status_code=400, detail="Limit en offset moeten gehele positieve getallen zijn.")

    Session = sessionmaker(bind=get_engine())
    with Session() as session:
        query = (
            session.query(
                FactStudentNumbers.id,
                DimProvincie.naam.label("provincie"),
                DimGemeente.gemeentenaam.label("gemeente"),
                DimInstelling.instellingsnaam_actueel.label("instelling"),
                DimOpleiding.opleidingsnaam_actueel.label("opleiding"),
                FactStudentNumbers.geslacht_id.label("geslacht"),
                FactStudentNumbers.aantal,
                FactStudentNumbers.jaar
            )
            .join(DimProvincie, FactStudentNumbers.provincie_id == DimProvincie.id)
            .join(DimGemeente, FactStudentNumbers.gemeente_id == DimGemeente.id)
            .join(DimInstelling, FactStudentNumbers.instelling_id == DimInstelling.id)
            .join(DimOpleiding, FactStudentNumbers.opleiding_id == DimOpleiding.id)
        )

        if provincie_naam:
            query = query.filter(DimProvincie.naam == provincie_naam)
        if instelling_naam:
            query = query.filter(DimInstelling.instellingsnaam_actueel == instelling_naam)

        query = query.limit(limit).offset(offset)
        results = query.all()

        students = [
            {
                "id": result.id,
                "provincie": result.provincie,
                "gemeente": result.gemeente,
                "instelling": result.instelling,
                "opleiding": result.opleiding,
                "geslacht": result.geslacht,
                "aantal": result.aantal,
                "jaar": result.jaar
            }
            for result in results
        ]

        return {"students": students, "limit": limit, "offset": offset}


@app.get("/students/summary")
def get_student_summary(
        provincie_naam: str = Query(None, description="Filter op de naam van de provincie"),  # Optioneel
        gemeente_naam: str = Query(None, description="Filter op de naam van de gemeente")  # Optioneel
):
    Session = sessionmaker(bind=get_engine())
    with (Session() as session):
        query = session.query(
            func.sum(FactStudentNumbers.aantal_2018).label("total_2018"),
            func.sum(FactStudentNumbers.aantal_2019).label("total_2019"),
            func.sum(FactStudentNumbers.aantal_2020).label("total_2020"),
            func.sum(FactStudentNumbers.aantal_2021).label("total_2021"),
            func.sum(FactStudentNumbers.aantal_2022).label("total_2022")
        )

        # Optionele filters
        if provincie_naam:
            query = query.join(
                DimProvincie, FactStudentNumbers.provincie_id == DimProvincie.id
            ).filter(DimProvincie.naam == provincie_naam)

        if gemeente_naam:
            query = query.join(
                DimGemeente, FactStudentNumbers.gemeente_id == DimGemeente.id
            ).filter(DimGemeente.gemeentenaam == gemeente_naam)

        # Query uitvoeren
        result = query.one()

        # Resultaten verwerken
        return {
            "filter": {
                "provincie": provincie_naam,
                "gemeente": gemeente_naam,
            },
            "totals": {
                "2018": result.total_2018 or 0,
                "2019": result.total_2019 or 0,
                "2020": result.total_2020 or 0,
                "2021": result.total_2021 or 0,
                "2022": result.total_2022 or 0,
            }
        }
