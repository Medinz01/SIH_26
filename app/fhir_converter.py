# Replace the contents of app/fhir_converter.py
from fhir.resources.condition import Condition
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from sqlalchemy.orm import Session

from . import schemas, crud

def create_fhir_condition(db: Session, db_term: schemas.NamasteTerm) -> Condition:
    mapped_icd = crud.get_mapping_for_namaste_code(db, namaste_code=db_term.code)

    condition = Condition.construct()
    condition.clinicalStatus = CodeableConcept(
        coding=[Coding(system="http://terminology.hl7.org/CodeSystem/condition-clinical", code="active")]
    )

    namaste_coding = Coding(
        system="https://www.namaste-ayush.in/codes",
        code=db_term.code,
        display=db_term.term
    )

    codings = [namaste_coding]

    if mapped_icd:
        icd_coding = Coding(
            system="http://id.who.int/icd/release/11/mms",
            code=mapped_icd.icd_code,
            display=mapped_icd.icd_display
        )
        codings.append(icd_coding)

    condition.code = CodeableConcept(coding=codings, text=db_term.term)
    condition.subject = Reference(reference="Patient/123", display="Test Patient")

    return condition