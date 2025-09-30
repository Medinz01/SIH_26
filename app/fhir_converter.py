from fhir.resources.condition import Condition
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from . import models

def create_fhir_condition(db_term: models.NamasteTerm, db_map: models.ConceptMap | None):
    """
    Creates a FHIR Condition resource from a NAMASTE term and its optional map.
    This function now purely handles formatting.
    """

    # 1. Create the primary NAMASTE coding
    namaste_coding = Coding.construct(
        system=f"http://nph.gov.in/namaste/{db_term.system}",
        code=db_term.code,
        display=db_term.term
    )
    codings = [namaste_coding]

    # 2. If a map exists and has a target ICD term, add the ICD-11 coding
    if db_map and db_map.icd_term:
        icd_coding = Coding.construct(
            system="http://id.who.int/icd/release/11/mms",
            code=db_map.icd_term.code,
            display=db_map.icd_term.term
        )
        codings.append(icd_coding)

    condition_code = CodeableConcept.construct(coding=codings, text=db_term.term)

    condition = Condition.construct(
        clinicalStatus=CodeableConcept.construct(coding=[Coding.construct(
            system="http://terminology.hl7.org/CodeSystem/condition-clinical", 
            code="active"
        )]),
        code=condition_code
        # In a real EMR, a subject (patient) reference would be added here
    )
    return condition