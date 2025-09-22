from fhir.resources.parameters import Parameters, ParametersParameter
from fhir.resources.conceptmap import ConceptMap, ConceptMapGroup, ConceptMapGroupElement, ConceptMapGroupElementTarget
from app import models

# Official and custom URIs for our code systems
SYSTEM_URIS = {
    "namaste_ayurveda": "http://nph.gov.in/namaste/ayurveda",
    "namaste_siddha": "http://nph.gov.in/namaste/siddha",
    "namaste_unani": "http://nph.gov.in/namaste/unani",
    "icd11": "http://id.who.int/icd/release/11/mms",
    "loinc": "http://loinc.org"
}

def create_lookup_parameters(term_object, system_uri: str, system_name: str) -> Parameters:
    """Creates a FHIR Parameters resource for a $lookup operation."""
    
    params = Parameters.construct()
    params.parameter = [
        ParametersParameter.construct(name="name", valueString=system_name),
        ParametersParameter.construct(name="version", valueString="2025-01"), # Example version
        ParametersParameter.construct(name="display", valueString=term_object.term),
        ParametersParameter.construct(name="designation", part=[
            ParametersParameter.construct(name="value", valueString=term_object.term)
        ])
    ]
    return params

def create_translate_conceptmap(source_term, target_term, relationship) -> ConceptMap:
    """Creates a FHIR ConceptMap resource for a $translate operation."""
    
    source_system = SYSTEM_URIS.get(f"namaste_{source_term.system}", "http://nph.gov.in/namaste")

    target = ConceptMapGroupElementTarget.construct(
        code=target_term.code,
        display=target_term.term,
        relationship=relationship
    )
    
    element = ConceptMapGroupElement.construct(
        code=source_term.code,
        display=source_term.term,
        target=[target]
    )
    
    group = ConceptMapGroup.construct(
        source=source_system,
        target=SYSTEM_URIS["icd11"],
        element=[element]
    )
    
    concept_map = ConceptMap.construct(
        url="http://your-domain.com/ConceptMap/namaste-to-icd11",
        name="NamasteToICD11",
        status="active",
        group=[group]
    )
    return concept_map