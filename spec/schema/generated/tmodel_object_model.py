from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.12.0"
version = "0.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'annotations': {'accepts': {'tag': 'accepts', 'value': 'DEC-001a'},
                     'federation': {'tag': 'federation',
                                    'value': 'out of scope; mappings are DEC-002 / '
                                             '#9'},
                     'normative': {'tag': 'normative', 'value': 'false'},
                     'proposes': {'tag': 'proposes', 'value': 'DEC-001b'},
                     'source_proposal': {'tag': 'source_proposal',
                                         'value': 'ARCH-0001-PROPOSAL-v0.2.0'},
                     'source_sections': {'tag': 'source_sections',
                                         'value': '§2, §2a, §2b, §3, §3b, §3c, §4, '
                                                  '§5, §10, §13'}},
     'default_prefix': 'tmodel',
     'default_range': 'string',
     'description': 'First-cut LinkML IDL for the ThreatRadar tmodel object model. '
                    'Source is ARCH-0001-PROPOSAL v0.2.0 §13 (classes) with edges '
                    'named in §§2–4, §10 and §3c. Core type system ACCEPTED '
                    '(DEC-001a, ADR-0010); governed/program layer proposes '
                    'DEC-001b. ADR-0004 is the accepted storage/edges pin (files '
                    'in git, stable IDs, typed edges); this schema does not close '
                    'DEC-002 or DEC-004.',
     'id': 'https://threat-radar.github.io/tmodel/schema/object-model',
     'imports': ['linkml:types'],
     'name': 'TmodelObjectModel',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'prov': {'prefix_prefix': 'prov',
                           'prefix_reference': 'http://www.w3.org/ns/prov#'},
                  'stix': {'prefix_prefix': 'stix',
                           'prefix_reference': 'https://docs.oasis-open.org/cti/stix/v2.1/'},
                  'tmodel': {'prefix_prefix': 'tmodel',
                             'prefix_reference': 'https://threat-radar.github.io/tmodel/schema/object-model/'}},
     'source_file': 'spec/schema/tmodel-object-model.linkml.yaml',
     'status': 'draft',
     'title': 'ThreatRadar tmodel object model (draft)'} )

class PartyKind(str, Enum):
    """
    Party is an organization or a person (§2b).
    """
    organization = "organization"
    person = "person"


class MethodFacet(str, Enum):
    """
    Method that proposed a ThreatInstance (§2). Only STRIDE is in MVP.
    """
    stride = "stride"
    """
    Per-element DFD classification. Not an AttackPattern field.
    """
    linddun = "linddun"
    """
    Privacy facet. Post-MVP; library record not pinned (§2).
    """
    maestro = "maestro"
    """
    Agentic-AI facet (#12). Post-MVP; library record not pinned (§2).
    """


class AttackGate(str, Enum):
    """
    How an AttackStep combines (§2a).
    """
    and_gate = "and_gate"
    """
    Proposal text "AND" (§2a). All predecessors required. Post-MVP per-step feasibility would take min.
    """
    or_gate = "or_gate"
    """
    Proposal text "OR" (§2a). Any predecessor suffices. Post-MVP per-step feasibility would take max.
    """


class FeasibilityLevel(str, Enum):
    """
    ISO/SAE 21434 path-level 4-point scale (§3, Table 1). Human-rated at MVP. Not a Common Criteria score and not a CVSS exploitability number.
    """
    high = "high"
    medium = "medium"
    low = "low"
    very_low = "very_low"


class ImpactSeverity(str, Enum):
    """
    ISO 21434 impact ordinal per S/F/O/P category (§3, RQ-15-04/05).
    """
    severe = "severe"
    major = "major"
    moderate = "moderate"
    negligible = "negligible"


class MitigationStatus(str, Enum):
    """
    Mitigation lifecycle (§3 R-045). Refined later by DEC-009.
    """
    planned = "planned"
    in_progress = "in_progress"
    """
    Proposal text says "in-progress".
    """
    complete = "complete"
    accepted_risk = "accepted_risk"
    """
    Proposal text says "accepted-risk".
    """
    not_applicable = "not_applicable"
    """
    Proposal text says "n-a".
    """


class LifecyclePhaseCode(str, Enum):
    """
    LifecyclePhase vocabulary (§3b), aligned to ISO/SAE 21434 + ISO 26262. Returns/refurbish/resale/dispose are called out as future phase tags; they are not given codes here because §3b says the returns branch is post-MVP.
    """
    concept = "concept"
    architecture = "architecture"
    design = "design"
    implementation = "implementation"
    verification_validation = "verification_validation"
    """
    Proposal text "verification/validation".
    """
    production = "production"
    """
    Proposal text "production/manufacturing".
    """
    distribution = "distribution"
    deployment = "deployment"
    """
    Proposal text "deployment/commissioning".
    """
    operation = "operation"
    """
    Proposal text "operation/use". Runtime exposure is Environment, not this code (§3b).
    """
    maintenance = "maintenance"
    """
    Proposal text "maintenance/update".
    """
    end_of_support = "end_of_support"
    decommission = "decommission"
    """
    Proposal text "decommission/disposal".
    """


class RedundancyRelation(str, Enum):
    """
    Edge names inside a RedundancyGroup (§3).
    """
    replica_of = "replica_of"
    redundant_with = "redundant_with"


class ViewProjection(str, Enum):
    """
    Named projections over one graph (§10). Matrix, compare, saved views are post-MVP.
    """
    graph = "graph"
    threat_mitigation_matrix = "threat_mitigation_matrix"
    attack_path = "attack_path"
    dfd = "dfd"
    timeline = "timeline"
    provenance = "provenance"
    compare = "compare"


class GateStatus(str, Enum):
    """
    Passage status of an SDL program node — Gate / Milestone / Checkpoint (§3c R-041).
    """
    planned = "planned"
    in_progress = "in_progress"
    """
    Proposal text "in-progress".
    """
    passed = "passed"
    failed = "failed"
    waived = "waived"
    """
    Passage waived by an approved exception (a Review verdict, §4/§5).
    """
    blocked = "blocked"


class ThreatModelStatus(str, Enum):
    """
    Lifecycle of a governed snapshot (§3c R-043). Named for the ThreatModel case; the same lifecycle is reused by SecurityProgram and GovernedView.
    """
    draft = "draft"
    in_review = "in_review"
    """
    Proposal text "in-review".
    """
    approved = "approved"
    superseded = "superseded"


class ApprovalStatus(str, Enum):
    """
    Standing of a governed artifact's sign-off, read from its approving Review(s) (§4 spine). Distinct from ThreatModelStatus (the content lifecycle).
    """
    pending = "pending"
    approved = "approved"
    changes_requested = "changes_requested"
    rejected = "rejected"
    withdrawn = "withdrawn"


class RequirementConformanceStatus(str, Enum):
    """
    Automatable R-042 conformance verdict for a Requirement — linkage + approval, NOT adequacy (the human cybersecurity-assessment role remains, CLAUDE.md).
    """
    conformant = "conformant"
    """
    An approved, evidenced Mitigation satisfies the requirement.
    """
    nonconformant = "nonconformant"
    partial = "partial"
    not_applicable = "not_applicable"
    """
    Out of scope for this product/profile, with a recorded reason.
    """
    not_assessed = "not_assessed"


class Normativity(str, Enum):
    """
    How binding a Requirement is (§3c R-044). A MAP-0001 cell means different things per framework (hard requirement vs maturity activity vs recommendation).
    """
    mandatory = "mandatory"
    recommended = "recommended"
    optional = "optional"
    informative = "informative"
    conditional = "conditional"
    """
    Applies only when a stated condition holds.
    """



class Node(ConfiguredBaseModel):
    """
    Shared identity for every §13 class. `id` is the stable object id ADR-0004 requires across file, LPG, and RDF encodings. Not itself a §13 class.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Product(Node):
    """
    A product design (structural layer, §1). Recursive composition is `composed_of` Components (§3). Relational party roles are edges (§2b).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    composed_of: Optional[list[str]] = Field(default=None, description="""Recursive structural composition (§3). Inlined as references, not as nested trees.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'Component']} })
    manufactured_by: Optional[str] = Field(default=None, description="""Relational role edge (§2b), not a classification on Party.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product']} })
    supplied_by: Optional[str] = Field(default=None, description="""Relational role edge (§2b). The same Party may supply one product and consume another.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product']} })
    owned_by: Optional[str] = Field(default=None, description="""Proposal attaches owned_by to Asset (§2b, §3). Asset is not a §13 class; the slot is on Product, ProductInstance, and Component as the structural stand-in. It selects whose business_impact would apply. The business_impact axis itself is post-MVP and has no slot.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'ProductInstance', 'Component']} })
    identifiers: Optional[list[str]] = Field(default=None, description="""Opaque external / instance-identity strings for a structural node — Product, ProductInstance, or Component (§1). This is ADR-0002's per-type instance identity (\"software = a build/commit/hash/SBOM; hardware = firmware + buses + cores (HBOM)\") and the generic↔instance half of DEC-009, which the §13 classes otherwise could not carry: `catalog_ref` names a GENERIC catalog entry (CWE/CVE/CAPEC), not the concrete artifact. Scheme-prefixed and OPAQUE, like `catalog_ref` / `external_refs` — a CPE, a package URL (purl), a SWID/SBOM ref, a build/commit hash, or a firmware-image digest. The scheme is NOT pinned and no CPE/SBOM schema is imported (ADR-0004 substrate-neutrality). Additive DRAFT slot (DEC-001 open); not a new §13 class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'ProductInstance', 'Component'],
         'examples': [{'value': 'pkg:npm/lodash@4.17.20'},
                      {'value': 'cpe:2.3:a:openssl:openssl:3.0.2:*:*:*:*:*:*:*'},
                      {'value': 'swid:acme-ecu-fw-2.4.1'},
                      {'value': 'sha256:9f2c1a7e...firmware-image-digest'}]} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class ProductInstance(Node):
    """
    A versioned, identity-bearing instance of a Product (§1, §3b). Lifecycle *state* sits here (with valid_from/valid_to), not on Product or Component. A refurbished unit can share a firmware hash and still carry a new phase, Deployment, and owner. The firmware image digest / build hash is an opaque `identifiers` string (ADR-0002 per-type instance identity), not a pinned slot.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    of_product: str = Field(default=..., description="""The Product this ProductInstance instantiates (§1).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProductInstance']} })
    current_phase: Optional[str] = Field(default=None, description="""Lifecycle state of this ProductInstance at valid_from/valid_to (§3b).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProductInstance']} })
    valid_from: Optional[datetime ] = Field(default=None, description="""Start of the (ProductInstance, time) state interval (§3b). Temporal axis was flagged as still-missing; included here because §3b says to add it with lifecycle state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProductInstance']} })
    valid_to: Optional[datetime ] = Field(default=None, description="""End of the (ProductInstance, time) state interval (§3b). Open-ended if absent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProductInstance']} })
    owned_by: Optional[str] = Field(default=None, description="""Proposal attaches owned_by to Asset (§2b, §3). Asset is not a §13 class; the slot is on Product, ProductInstance, and Component as the structural stand-in. It selects whose business_impact would apply. The business_impact axis itself is post-MVP and has no slot.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'ProductInstance', 'Component']} })
    identifiers: Optional[list[str]] = Field(default=None, description="""Opaque external / instance-identity strings for a structural node — Product, ProductInstance, or Component (§1). This is ADR-0002's per-type instance identity (\"software = a build/commit/hash/SBOM; hardware = firmware + buses + cores (HBOM)\") and the generic↔instance half of DEC-009, which the §13 classes otherwise could not carry: `catalog_ref` names a GENERIC catalog entry (CWE/CVE/CAPEC), not the concrete artifact. Scheme-prefixed and OPAQUE, like `catalog_ref` / `external_refs` — a CPE, a package URL (purl), a SWID/SBOM ref, a build/commit hash, or a firmware-image digest. The scheme is NOT pinned and no CPE/SBOM schema is imported (ADR-0004 substrate-neutrality). Additive DRAFT slot (DEC-001 open); not a new §13 class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'ProductInstance', 'Component'],
         'examples': [{'value': 'pkg:npm/lodash@4.17.20'},
                      {'value': 'cpe:2.3:a:openssl:openssl:3.0.2:*:*:*:*:*:*:*'},
                      {'value': 'swid:acme-ecu-fw-2.4.1'},
                      {'value': 'sha256:9f2c1a7e...firmware-image-digest'}]} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Component(Node):
    """
    Authoritative deployed artifact (service, container, dependency, chip, core) — not an OTM diagram node (§0). `uses_component` / `composed_of` are the propagation paths for vulnerabilities (§5).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    composed_of: Optional[list[str]] = Field(default=None, description="""Recursive structural composition (§3). Inlined as references, not as nested trees.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'Component']} })
    depends_on: Optional[list[str]] = Field(default=None, description="""Dependency edge, including DNS/service-style depends_on (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Component']} })
    uses_component: Optional[list[str]] = Field(default=None, description="""Use edge along which vuln/finding propagation is sound (§5).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Component']} })
    owned_by: Optional[str] = Field(default=None, description="""Proposal attaches owned_by to Asset (§2b, §3). Asset is not a §13 class; the slot is on Product, ProductInstance, and Component as the structural stand-in. It selects whose business_impact would apply. The business_impact axis itself is post-MVP and has no slot.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'ProductInstance', 'Component']} })
    identifiers: Optional[list[str]] = Field(default=None, description="""Opaque external / instance-identity strings for a structural node — Product, ProductInstance, or Component (§1). This is ADR-0002's per-type instance identity (\"software = a build/commit/hash/SBOM; hardware = firmware + buses + cores (HBOM)\") and the generic↔instance half of DEC-009, which the §13 classes otherwise could not carry: `catalog_ref` names a GENERIC catalog entry (CWE/CVE/CAPEC), not the concrete artifact. Scheme-prefixed and OPAQUE, like `catalog_ref` / `external_refs` — a CPE, a package URL (purl), a SWID/SBOM ref, a build/commit hash, or a firmware-image digest. The scheme is NOT pinned and no CPE/SBOM schema is imported (ADR-0004 substrate-neutrality). Additive DRAFT slot (DEC-001 open); not a new §13 class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Product', 'ProductInstance', 'Component'],
         'examples': [{'value': 'pkg:npm/lodash@4.17.20'},
                      {'value': 'cpe:2.3:a:openssl:openssl:3.0.2:*:*:*:*:*:*:*'},
                      {'value': 'swid:acme-ecu-fw-2.4.1'},
                      {'value': 'sha256:9f2c1a7e...firmware-image-digest'}]} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Party(Node):
    """
    One reusable identity for an organization or a person (§2b). ThreatActor and PROV Agent are facets of this identity, not separate §13 classes. Only intrinsic classifications live on the node; supplier/owner/vendor-of are edges.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    party_kind: Optional[PartyKind] = Field(default=None, description="""Organization or person (§2b).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Party']} })
    classifications: Optional[list[str]] = Field(default=None, description="""Intrinsic classifications only, e.g. standards-body, cna (§2b).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Party'],
         'examples': [{'value': 'standards-body'}, {'value': 'cna'}]} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Weakness(Node):
    """
    Generic weakness, catalogued as CWE (§1 layer 3). The CWE↔CAPEC link is a human-reviewed mapping (an Assertion), not a facet property (§2) — no hard edge to AttackPattern in this cut.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    catalog_ref: Optional[str] = Field(default=None, description="""External catalog identifier when the proposal names one (CWE, CAPEC, ATT&CK, CVE, D3FEND). The identifier scheme is not pinned in §13.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Weakness', 'Vulnerability', 'AttackPattern', 'Mitigation']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Vulnerability(Node):
    """
    A finding/vulnerability (CVE/NVD-shaped) that `affects` a Product (§2b). Propagation along uses_component/composed_of and the per-instance VEX override are Assertions plus Reviews (§5), not extra classes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    catalog_ref: Optional[str] = Field(default=None, description="""External catalog identifier when the proposal names one (CWE, CAPEC, ATT&CK, CVE, D3FEND). The identifier scheme is not pinned in §13.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Weakness', 'Vulnerability', 'AttackPattern', 'Mitigation']} })
    affects: Optional[list[str]] = Field(default=None, description="""Vulnerability/Finding affects a vendor Product (§2b).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Vulnerability']} })
    reported_by: Optional[str] = Field(default=None, description="""Reporter (§2b).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Vulnerability']} })
    assigned_by: Optional[str] = Field(default=None, description="""Assigning CNA (§2b). Party.classifications should include cna when this is set; not enforced here.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Vulnerability']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class AttackPattern(Node):
    """
    Generic attack pattern (CAPEC / ATT&CK technique = *what*, §1, §2a). STRIDE is not a property of this class (§2). Kill-chain phase is on AttackStep, not here.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    catalog_ref: Optional[str] = Field(default=None, description="""External catalog identifier when the proposal names one (CWE, CAPEC, ATT&CK, CVE, D3FEND). The identifier scheme is not pinned in §13.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Weakness', 'Vulnerability', 'AttackPattern', 'Mitigation']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class ThreatInstance(Node):
    """
    A threat in a model, not the generic catalog entry (§1). Carries the method facet (STRIDE and, post-MVP, LINDDUN/MAESTRO) and `realizes` a DamageScenario. Phase scope is `applies_in_phase` (§3b), distinct from Environment.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    realizes_damage: Optional[str] = Field(default=None, description="""ThreatInstance realizes a DamageScenario (§1).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatInstance']} })
    method_facet: Optional[list[MethodFacet]] = Field(default=None, description="""Which method classified this threat (§2). STRIDE is a facet, not an AttackPattern property. Facets beyond STRIDE are post-MVP.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatInstance']} })
    source_method: Optional[str] = Field(default=None, description="""Which method proposed this ThreatInstance (§2).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatInstance']} })
    violates_property: Optional[str] = Field(default=None, description="""Security property the facet says is violated (§2). STRIDE sketch, not a closed enum: S authentication, T integrity, R non-repudiation, I confidentiality, D availability, E authorization.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatInstance']} })
    applies_in_phase: Optional[list[str]] = Field(default=None, description="""Coarse lifecycle stage a threat or mitigation belongs to (§3b). Not a substitute for Environment. One threat uses the axis that fits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatInstance', 'Mitigation']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class AttackStep(Node):
    """
    A step in an attack graph (§2a): AND/OR `gate`, explicit `precedes` order, shareable across paths. Optional kill-chain phase is coarse order, not the ATT&CK technique. Pre/postconditions are not given a schema shape in §2a.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    gate: Optional[AttackGate] = Field(default=None, description="""AND/OR combination of this step with its predecessors (§2a, R-031).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AttackStep']} })
    precedes: Optional[list[str]] = Field(default=None, description="""Explicit ordering edge (§2a). Steps may be shared across paths.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AttackStep']} })
    kill_chain_phase: Optional[str] = Field(default=None, description="""Optional coarse order tag (§2a). Distinct from the ATT&CK technique. The Lockheed kill-chain record is not pinned; do not rely on a fixed vocabulary.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AttackStep']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class AttackPath(Node):
    """
    An ordered set of AttackSteps realising a ThreatInstance (§2a, §3). Feasibility is rated here, at path level (human-rated at MVP). Feasibility METHOD is ISO/SAE 21434 Table-1 (§3, DL-0011), human-rated at MVP; Common Criteria is display-only (numbers + label). No per-step aggregation at MVP. DEC-003 is open; ADR-0005 was dropped, not accepted.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    steps: Optional[list[str]] = Field(default=None, description="""AttackSteps in this path (§2a). Order is the `precedes` edges, not list position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AttackPath']} })
    realizes_threat: Optional[str] = Field(default=None, description="""This path realises the threat scenario (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AttackPath']} })
    attack_feasibility: Optional[FeasibilityLevel] = Field(default=None, description="""Path-level feasibility, ISO 21434 4-point scale, human-rated at MVP (§3, Table 1 / RQ-15-10). Not CVSS. Not per-step min/max (that is post-MVP).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AttackPath']} })
    pivots_to: Optional[list[str]] = Field(default=None, description="""Path-level pivot across a reachability substrate (§1). Reachability's other two levels (connected_via, step preconditions) are not classes in §13.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AttackPath']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class DamageScenario(Node):
    """
    The damage a ThreatInstance realizes (§1). Impact categories are recorded on RiskScore, not collapsed here (§3).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Mitigation(Node):
    """
    A mitigation/control (catalog example D3FEND, §1). §5 instance fields (implementation owner, external work-item refs, status) are on this class until a separate MitigationInstance class is accepted. Status is also surfaced as RiskScore.mitigation_status (R-045) — a peer of the derived risk, not an input to it.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    catalog_ref: Optional[str] = Field(default=None, description="""External catalog identifier when the proposal names one (CWE, CAPEC, ATT&CK, CVE, D3FEND). The identifier scheme is not pinned in §13.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Weakness', 'Vulnerability', 'AttackPattern', 'Mitigation']} })
    mitigates: Optional[list[str]] = Field(default=None, description="""Threats this mitigation addresses (§5). Phase binding is applies_in_phase.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Mitigation']} })
    applies_in_phase: Optional[list[str]] = Field(default=None, description="""Coarse lifecycle stage a threat or mitigation belongs to (§3b). Not a substitute for Environment. One threat uses the axis that fits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatInstance', 'Mitigation']} })
    implementation_owner: Optional[str] = Field(default=None, description="""Who implements the mitigation (§5).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Mitigation']} })
    external_refs: Optional[list[str]] = Field(default=None, description="""Linked work items, e.g. a Jira key (§5). Opaque strings; no tracker schema.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Mitigation']} })
    mitigation_status: Optional[MitigationStatus] = Field(default=None, description="""Lifecycle of the mitigation (§3 R-045, §5): planned / in-progress / complete / accepted-risk / n-a. Vocabulary may be refined by DEC-009. On RiskScore this is a peer column of feasibility and impact, not folded into `risk`.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Mitigation', 'RiskScore']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class RiskScore(Node):
    """
    Composite risk vector (sponsor round, proposed.10 / DL-0011; DEC-003 OPEN — ADR-0005 was dropped, not accepted). Peer slots: feasibility (ISO 21434 Table-1 method; Common Criteria display-only — numbers, label, and a colored indicator in table views), impact (from attack damage; 21434 S/F/O/P), mitigation_status, and derived risk. Shown alongside its inputs, never instead of them. Not a single CVSS score. More components only with a further sponsor decision. MVP: one stakeholder; business_impact is post-MVP and intentionally has no slot.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    threat: str = Field(default=..., description="""Threat scenario this score is about (§3, RQ-15-15/16).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RiskScore']} })
    attack_paths: Optional[list[str]] = Field(default=None, description="""Paths whose feasibilities feed this score. Reduction across paths is worst-path (§3); this schema stores the set, not the fold function.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RiskScore']} })
    damage_scenario: Optional[str] = Field(default=None, description="""Damage scenario whose impact feeds M(I, F) (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RiskScore']} })
    for_stakeholder: Optional[str] = Field(default=None, description="""Owner this score is reported for, when a path crosses assets with different owners (§3). MVP assumes one stakeholder; omit unless needed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RiskScore']} })
    feasibility: Optional[FeasibilityLevel] = Field(default=None, description="""Vector component (§3, DL-0011). Copied or reduced from AttackPath.attack_feasibility (worst path). Method is ISO 21434 Table-1, not Common Criteria.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RiskScore']} })
    impact: Optional[ImpactVector] = Field(default=None, description="""Per-category S/F/O/P vector (§3). Human-supplied. Do not replace this object with a single severity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RiskScore']} })
    mitigation_status: Optional[MitigationStatus] = Field(default=None, description="""Lifecycle of the mitigation (§3 R-045, §5): planned / in-progress / complete / accepted-risk / n-a. Vocabulary may be refined by DEC-009. On RiskScore this is a peer column of feasibility and impact, not folded into `risk`.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Mitigation', 'RiskScore']} })
    risk: Optional[str] = Field(default=None, description="""Derived Risk = M(Impact, Feasibility) (§3). ISO 21434 wants one value 1–5 per (threat-scenario, impact-category), and per stakeholder when owners differ. Stored as text because the aggregation function is not fixed until a DEC-003 ADR. Not a CVSS base score. Display may add a colour and a feasibility label; that styling is not a slot.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RiskScore']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Review(Node):
    """
    Human verdict on an Assertion (§4, §5). Kept separate from the proposal. Carries status, priority, and justification. STIX Opinion/Note is a future mapping (DEC-002 / #9), not a parent class.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    reviews: str = Field(default=..., description="""The Assertion this Review judges (§4).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Review']} })
    reviewer: Optional[str] = Field(default=None, description="""Human (or, later, an agent facet of a Party) who issued the verdict (§4).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Review']} })
    review_status: Optional[str] = Field(default=None, description="""Verdict status (§5). Kept open: proposal does not enumerate the values.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Review']} })
    priority: Optional[str] = Field(default=None, description="""Review priority (§5). Scale not specified in the proposal.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Review']} })
    justification: Optional[str] = Field(default=None, description="""Why the verdict was reached (§5). Separate from the Assertion text.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Review']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Assertion(Node):
    """
    Reified edge (§4): subject / predicate / object, so a Review, confidence, and provenance can point at the statement. Substrate-neutral logical node; RDF-star, named graphs, and LPG edge-properties are storage lowerings (ADR-0004) and are not chosen here. Promoting a reviewed edge to this node narrows DEC-004 (no pure edge-property-only form for reviewed assertions). The acceptance gate (provenance + review before status=accepted) is a hand-written constraint, not something gen-shacl emits (§13).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    subject: str = Field(default=..., description="""Subject of the reified statement (§4).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Assertion']} })
    predicate: str = Field(default=..., description="""Edge type name (§4), e.g. composed_of, affects, realizes, owned_by. Not a closed enum: reviewed edges that are not first-class slots still reify here (including the human-reviewed CWE↔CAPEC mapping, §2).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Assertion']} })
    object: str = Field(default=..., description="""Object of the reified statement (§4).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Assertion']} })
    confidence: Optional[str] = Field(default=None, description="""Confidence attached to the Assertion (§4). Scale is not fixed in the proposal.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Assertion']} })
    assertion_status: Optional[str] = Field(default=None, description="""Proposal status of the Assertion (§4). Must not be `accepted` until provenance and a review are present. That gate is not encoded as a LinkML cardinality rule (§13).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Assertion']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Deployment(Node):
    """
    A placement of one ProductInstance (§3). Many Deployments per instance; each points at one Environment. Single deployment is the MVP assumption; deployment-relative risk (R-023) is post-MVP.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    product_instance: str = Field(default=..., description="""The instance this Deployment places (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Deployment']} })
    environment: str = Field(default=..., description="""The one Environment for this Deployment (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Deployment']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Environment(Node):
    """
    Reusable operational exposure of a running deployment (§3, F9): physical security, connectivity, operational context. Parameterises feasibility's exploitability side only — never impact CIA (F5). Distinct from LifecyclePhase (§3b). The MVP metric runs without requiring this node.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    physical_security: Optional[str] = Field(default=None, description="""Environment facet (§3). Feeds feasibility exploitability only, post-MVP.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Environment']} })
    connectivity: Optional[str] = Field(default=None, description="""Environment facet (§3). Feeds attack vector / reachability / window, not impact.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Environment']} })
    operational_context: Optional[str] = Field(default=None, description="""Environment facet (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Environment']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class LifecyclePhase(Node):
    """
    Coarse lifecycle stage (§3b). The vocabulary is LifecyclePhaseCode (concept through decommission/disposal, ISO 21434 + ISO 26262 aligned). Reverse-logistics transitions and custody provenance are post-MVP and are not modeled. `name` is the human label; `code` is the enum.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    code: LifecyclePhaseCode = Field(default=..., description="""Controlled phase code (§3b).""", json_schema_extra = { "linkml_meta": {'domain_of': ['LifecyclePhase']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class RedundancyGroup(Node):
    """
    Marks Deployments (or whole build/review systems) as replicas (§3, §10): `replica_of` / `redundant_with`. Supports common-mode risk and per-replica mitigation divergence. Post-MVP (R-034).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    replicas: Optional[list[str]] = Field(default=None, description="""Deployments in this redundancy group (§3, §10).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RedundancyGroup']} })
    redundancy_relation: Optional[RedundancyRelation] = Field(default=None, description="""replica_of or redundant_with (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RedundancyGroup']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class View(Node):
    """
    Derived presentation lens (§10): query/filter + projection. Not domain truth and never written back onto domain nodes. Saved views may be persisted; rendered geometry is transient and out of this schema. One graph projection is MVP; other projections are post-MVP.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    projection: Optional[ViewProjection] = Field(default=None, description="""Which derived projection this View spec names (§10).""", json_schema_extra = { "linkml_meta": {'domain_of': ['View']} })
    focus_query: Optional[str] = Field(default=None, description="""Bounded query / filter that defines the view (§10, R-033). Opaque to this schema (not a committed query language — DEC-004 is open).""", json_schema_extra = { "linkml_meta": {'domain_of': ['View']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class ThreatModel(Node):
    """
    A GOVERNED, VERSIONED view/snapshot over the KG-as-SoT (§3c R-043). NOT domain truth re-stated: a reviewed LENS whose membership and verdicts are tracked across review cycles. Scope is either a bounded `scope_query` or an explicit `members` set (in-scope ThreatInstances / AttackPaths / Components / Products). Governance is the shared governed-view facet: `owner` (a Party ROLE, §2b — not a new actor type), `revision`, approval through the existing Review spine (`approved_by`) pinned to an `approval_digest` so sign-off is REPRODUCIBLE against KG state at a point in time, `governance_status` (draft/in-review/approved/superseded), and `supersedes` the prior revision. ARCH-0001 has no ThreatModel class; this is the scope node for \"the threat model itself\" (RPT-0013-OM §2). Post-MVP as an SDL object (the threat content it scopes is MVP).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model',
         'slot_usage': {'supersedes': {'description': 'The prior revision of this '
                                                      'threat-model snapshot it '
                                                      'replaces (§3c R-043).',
                                       'name': 'supersedes',
                                       'range': 'ThreatModel'}}})

    scope_query: Optional[str] = Field(default=None, description="""Bounded query/filter defining a ThreatModel snapshot's membership (§3c R-043). Opaque to this schema (DEC-004 open), like View.focus_query. Use `members` for an explicit set instead.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel']} })
    members: Optional[list[str]] = Field(default=None, description="""Explicit in-scope members of a ThreatModel snapshot (§3c R-043): ThreatInstances, AttackPaths, Components, Products. References, not copies — membership is a reviewed lens over the KG, never domain truth re-stated.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel']} })
    owner: Optional[str] = Field(default=None, description="""Owner/approver of a governed artifact (§3c R-043). A Party ROLE (§2b — one identity, many facets), NOT a new actor type (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'ProgramNode', 'GovernedView']} })
    revision: Optional[str] = Field(default=None, description="""Monotonic revision/version of a governed snapshot (§3c R-043). This is the saved view's \"version\"; ThreatModel and SecurityProgram name the same field `revision`. Tracked across review cycles via `supersedes`.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approved_by: Optional[list[str]] = Field(default=None, description="""Approving Review(s) of a governed artifact (§3c R-043). Approval runs through the existing Review + Assertion spine (§4) — NOT a parallel provenance mechanism (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approval_digest: Optional[str] = Field(default=None, description="""Commit/content digest the approval is pinned to, so the sign-off is REPRODUCIBLE against KG state at a point in time (§3c R-043; SysML v2 View/Viewpoint, OMG SACM, OSCAL→Word prior art). Opaque string; digest scheme not pinned here.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approval_status: Optional[ApprovalStatus] = Field(default=None, description="""Standing of the current sign-off, read from the approving Review(s) (§4 spine). Distinct from `governance_status` (where the snapshot is in its life): this tracks the verdict of its review cycle. Denormalized convenience — the authoritative verdict is the Review, not this field.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    governance_status: Optional[ThreatModelStatus] = Field(default=None, description="""Lifecycle of a governed snapshot (§3c R-043): draft → in-review → approved → superseded. The shared governed-view lifecycle (named for the ThreatModel case; reused by SecurityProgram and GovernedView).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    supersedes: Optional[str] = Field(default=None, description="""The prior revision of this threat-model snapshot it replaces (§3c R-043).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    created: Optional[datetime ] = Field(default=None, description="""When the governed artifact was created (§3c R-043 change tracking).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    updated: Optional[datetime ] = Field(default=None, description="""When the governed artifact was last updated (§3c R-043 change tracking).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class SecurityProgram(Node):
    """
    The SDL as a first-class, GOVERNED, VERSIONED object (§3c R-041). An ordered, named, dated program `governs` a Product / ProductInstance / ProductFamily and is composed of `program_nodes` (Gate / Milestone / Checkpoint) mapped onto the LifecyclePhase axis (§3b, each node's `at_phase`). It `incorporates` the Requirements it enforces; its gates run the conformance check (R-042). Full program management lives on the program nodes (owner, planned/actual dates, status per node). It is itself a governed view (owner / revision / approved_by + approval_digest / governance_status / supersedes), reconciling §10 \"views are transient\": the SDL plan is a named, versioned, signed-off snapshot over the one SoT, iterating across review cycles. Post-MVP.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model',
         'slot_usage': {'supersedes': {'description': 'The prior revision of this SDL '
                                                      'program it replaces (§3c '
                                                      'R-041/R-043).',
                                       'name': 'supersedes',
                                       'range': 'SecurityProgram'}}})

    governs: Optional[str] = Field(default=None, description="""The Product / ProductInstance / ProductFamily a SecurityProgram is attached to (§3c R-041). Range Node: ProductFamily is not a §13 class.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SecurityProgram']} })
    program_nodes: Optional[list[str]] = Field(default=None, description="""Ordered Gate / Milestone / Checkpoint nodes of a SecurityProgram (§3c R-041). Order is each node's `order`, not list position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SecurityProgram']} })
    incorporates: Optional[list[str]] = Field(default=None, description="""Requirements a SecurityProgram enforces (§3c R-041/R-044).""", json_schema_extra = { "linkml_meta": {'domain_of': ['SecurityProgram']} })
    owner: Optional[str] = Field(default=None, description="""Owner/approver of a governed artifact (§3c R-043). A Party ROLE (§2b — one identity, many facets), NOT a new actor type (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'ProgramNode', 'GovernedView']} })
    revision: Optional[str] = Field(default=None, description="""Monotonic revision/version of a governed snapshot (§3c R-043). This is the saved view's \"version\"; ThreatModel and SecurityProgram name the same field `revision`. Tracked across review cycles via `supersedes`.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approved_by: Optional[list[str]] = Field(default=None, description="""Approving Review(s) of a governed artifact (§3c R-043). Approval runs through the existing Review + Assertion spine (§4) — NOT a parallel provenance mechanism (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approval_digest: Optional[str] = Field(default=None, description="""Commit/content digest the approval is pinned to, so the sign-off is REPRODUCIBLE against KG state at a point in time (§3c R-043; SysML v2 View/Viewpoint, OMG SACM, OSCAL→Word prior art). Opaque string; digest scheme not pinned here.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approval_status: Optional[ApprovalStatus] = Field(default=None, description="""Standing of the current sign-off, read from the approving Review(s) (§4 spine). Distinct from `governance_status` (where the snapshot is in its life): this tracks the verdict of its review cycle. Denormalized convenience — the authoritative verdict is the Review, not this field.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    governance_status: Optional[ThreatModelStatus] = Field(default=None, description="""Lifecycle of a governed snapshot (§3c R-043): draft → in-review → approved → superseded. The shared governed-view lifecycle (named for the ThreatModel case; reused by SecurityProgram and GovernedView).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    supersedes: Optional[str] = Field(default=None, description="""The prior revision of this SDL program it replaces (§3c R-041/R-043).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    created: Optional[datetime ] = Field(default=None, description="""When the governed artifact was created (§3c R-043 change tracking).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    updated: Optional[datetime ] = Field(default=None, description="""When the governed artifact was last updated (§3c R-043 change tracking).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class ProgramNode(Node):
    """
    Shared shape for an SDL program node (§3c R-041): a named, `order`-ed, dated governance point on a SecurityProgram, mapped onto the LifecyclePhase axis (§3b, `at_phase`). Carries program-management fields — `order`, `planned_date` vs `actual_date`, `gate_status`, `owner` (Party ROLE, §2b), the Requirements that gate passage (`gated_by`), the Reviews that decide it (`decided_by` — the §4 human-review spine, not a parallel mechanism), and node dependencies / entry criteria (`depends_on_node`). Corporate gate-naming varies, so `name` is the local label and `at_phase` the canonical mapping (MAP-0001 gate crosswalk). Not instantiated directly; use Gate / Milestone / Checkpoint.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    order: Optional[int] = Field(default=None, description="""Position of a program node within its SecurityProgram (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    planned_date: Optional[date] = Field(default=None, description="""Planned date of a program node (§3c R-041 program management).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    actual_date: Optional[date] = Field(default=None, description="""Actual date a program node occurred (§3c R-041). Open if not yet reached.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gate_status: Optional[GateStatus] = Field(default=None, description="""Passage status of a program node (§3c R-041): planned / in-progress / passed / failed / waived / blocked.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    owner: Optional[str] = Field(default=None, description="""Owner/approver of a governed artifact (§3c R-043). A Party ROLE (§2b — one identity, many facets), NOT a new actor type (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'ProgramNode', 'GovernedView']} })
    at_phase: Optional[str] = Field(default=None, description="""Canonical LifecyclePhase a program node maps onto (§3b/§3c R-041). Gates are the governance points between phases; `name` is the local corporate label (MAP-0001 gate crosswalk).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gated_by: Optional[list[str]] = Field(default=None, description="""Requirements whose conformance gates passage of this program node (§3c R-041/R-042).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    decided_by: Optional[list[str]] = Field(default=None, description="""Reviews that decide a program node's passage (§3c R-041). The §4 human-review spine — not a parallel approval mechanism.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    depends_on_node: Optional[list[str]] = Field(default=None, description="""Entry-criteria / dependency edges between program nodes (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Gate(ProgramNode):
    """
    A named, ordered, dated DECISION point with exit criteria and an approving Review (§3c R-041). Its exit criterion runs the conformance check (`validates_conformance_of` a ThreatModel): a model is conformant when every in-scope ThreatInstance has an approved, evidenced Mitigation (R-042). The check PROVES linkage + approval, NOT adequacy — the human cybersecurity-assessment judgement stays a human input (CLAUDE.md).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    validates_conformance_of: Optional[str] = Field(default=None, description="""The ThreatModel whose conformance this Gate's exit criterion checks (§3c R-042): every in-scope ThreatInstance has an approved, evidenced Mitigation. Proves linkage + approval, NOT adequacy (CLAUDE.md human-judgement rule).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Gate']} })
    order: Optional[int] = Field(default=None, description="""Position of a program node within its SecurityProgram (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    planned_date: Optional[date] = Field(default=None, description="""Planned date of a program node (§3c R-041 program management).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    actual_date: Optional[date] = Field(default=None, description="""Actual date a program node occurred (§3c R-041). Open if not yet reached.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gate_status: Optional[GateStatus] = Field(default=None, description="""Passage status of a program node (§3c R-041): planned / in-progress / passed / failed / waived / blocked.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    owner: Optional[str] = Field(default=None, description="""Owner/approver of a governed artifact (§3c R-043). A Party ROLE (§2b — one identity, many facets), NOT a new actor type (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'ProgramNode', 'GovernedView']} })
    at_phase: Optional[str] = Field(default=None, description="""Canonical LifecyclePhase a program node maps onto (§3b/§3c R-041). Gates are the governance points between phases; `name` is the local corporate label (MAP-0001 gate crosswalk).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gated_by: Optional[list[str]] = Field(default=None, description="""Requirements whose conformance gates passage of this program node (§3c R-041/R-042).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    decided_by: Optional[list[str]] = Field(default=None, description="""Reviews that decide a program node's passage (§3c R-041). The §4 human-review spine — not a parallel approval mechanism.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    depends_on_node: Optional[list[str]] = Field(default=None, description="""Entry-criteria / dependency edges between program nodes (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Checkpoint(ProgramNode):
    """
    A lighter, recurring review point on a SecurityProgram (§3c R-041) — a ProgramNode with no extra shape; it reuses `gated_by` / `decided_by` / `at_phase`. Corporate SDLs name these variously (checkpoint, review, stage).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    order: Optional[int] = Field(default=None, description="""Position of a program node within its SecurityProgram (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    planned_date: Optional[date] = Field(default=None, description="""Planned date of a program node (§3c R-041 program management).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    actual_date: Optional[date] = Field(default=None, description="""Actual date a program node occurred (§3c R-041). Open if not yet reached.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gate_status: Optional[GateStatus] = Field(default=None, description="""Passage status of a program node (§3c R-041): planned / in-progress / passed / failed / waived / blocked.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    owner: Optional[str] = Field(default=None, description="""Owner/approver of a governed artifact (§3c R-043). A Party ROLE (§2b — one identity, many facets), NOT a new actor type (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'ProgramNode', 'GovernedView']} })
    at_phase: Optional[str] = Field(default=None, description="""Canonical LifecyclePhase a program node maps onto (§3b/§3c R-041). Gates are the governance points between phases; `name` is the local corporate label (MAP-0001 gate crosswalk).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gated_by: Optional[list[str]] = Field(default=None, description="""Requirements whose conformance gates passage of this program node (§3c R-041/R-042).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    decided_by: Optional[list[str]] = Field(default=None, description="""Reviews that decide a program node's passage (§3c R-041). The §4 human-review spine — not a parallel approval mechanism.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    depends_on_node: Optional[list[str]] = Field(default=None, description="""Entry-criteria / dependency edges between program nodes (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Milestone(ProgramNode):
    """
    A dated, owned deliverable point on a SecurityProgram (§3c R-041), optionally dated relative to another node (`offset_from`). May serve as a gate entry condition via another node's `depends_on_node`.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    offset_from: Optional[str] = Field(default=None, description="""Another program node this Milestone is dated relative to (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Milestone']} })
    order: Optional[int] = Field(default=None, description="""Position of a program node within its SecurityProgram (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    planned_date: Optional[date] = Field(default=None, description="""Planned date of a program node (§3c R-041 program management).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    actual_date: Optional[date] = Field(default=None, description="""Actual date a program node occurred (§3c R-041). Open if not yet reached.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gate_status: Optional[GateStatus] = Field(default=None, description="""Passage status of a program node (§3c R-041): planned / in-progress / passed / failed / waived / blocked.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    owner: Optional[str] = Field(default=None, description="""Owner/approver of a governed artifact (§3c R-043). A Party ROLE (§2b — one identity, many facets), NOT a new actor type (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'ProgramNode', 'GovernedView']} })
    at_phase: Optional[str] = Field(default=None, description="""Canonical LifecyclePhase a program node maps onto (§3b/§3c R-041). Gates are the governance points between phases; `name` is the local corporate label (MAP-0001 gate crosswalk).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    gated_by: Optional[list[str]] = Field(default=None, description="""Requirements whose conformance gates passage of this program node (§3c R-041/R-042).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    decided_by: Optional[list[str]] = Field(default=None, description="""Reviews that decide a program node's passage (§3c R-041). The §4 human-review spine — not a parallel approval mechanism.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    depends_on_node: Optional[list[str]] = Field(default=None, description="""Entry-criteria / dependency edges between program nodes (§3c R-041).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ProgramNode']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class Requirement(Node):
    """
    A normative statement from a spec, satisfied through the SDL (§3c R-044). Its `text` is the normative statement and `normativity` says how binding it is. `source_ref` is an OPAQUE uriorcurie into the library requirement record (Threat-Radar/library) — tmodel aligns by reference ONLY; it does not import or depend on the library schema. `maps_to` carries the MAP-0001 cross-spec crosswalk (how SSDF ↔ MS SDL ↔ SAMM ↔ 21434 … overlap; reviewed mappings reify as Assertions, §4). `satisfied_by` links the Mitigation(s) that discharge it; `conformance_status` is the automatable R-042 verdict — it proves linkage + approval, NOT adequacy. ARCH lists audit (Requirement/WorkProduct) as post-MVP (#19); not yet a §13 class. Post-MVP.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    text: Optional[str] = Field(default=None, description="""The normative statement of a Requirement (§3c R-044). Distinct from `description`.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Requirement']} })
    normativity: Optional[Normativity] = Field(default=None, description="""How binding a Requirement is (§3c R-044): mandatory / recommended / optional / informative / conditional. MAP-0001 shows a cell means different things per framework (hard requirement vs maturity activity vs recommendation).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Requirement']} })
    source_ref: Optional[str] = Field(default=None, description="""OPAQUE reference to a library requirement record (Threat-Radar/library), by uriorcurie id only (§3c R-044, §2b). tmodel aligns by reference — it does NOT import or depend on the library schema.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Requirement']} })
    maps_to: Optional[list[str]] = Field(default=None, description="""Cross-spec crosswalk edges (§3c R-044) = the MAP-0001 overlap. Reviewed mappings reify as Assertions (§4) so they can carry provenance + a Review.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Requirement']} })
    satisfied_by: Optional[list[str]] = Field(default=None, description="""Mitigation(s) that discharge this Requirement (§3c R-042).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Requirement']} })
    conformance_status: Optional[RequirementConformanceStatus] = Field(default=None, description="""Automatable R-042 conformance verdict for a Requirement: whether it has an approved, evidenced mitigation. Proves linkage + approval, NOT adequacy.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Requirement']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class GovernedView(View):
    """
    The governed, persisted subtype of View (§3c R-043). The existing `View` stays the TRANSIENT lens (query/projection, never written back); a GovernedView is the TRACKED artifact — an owned / approved / reproducible snapshot. It keeps View's `projection`/`focus_query` and adds governance: `owner` (Party ROLE, §2b), `revision` (the saved view's version), approval via the Review spine (`approved_by`) pinned to an `approval_digest` so the sign-off is reproducible against KG state at a point in time (SysML v2 View/Viewpoint, OMG SACM, OSCAL→Word prior art), `governance_status`, and `supersedes`. `renders` the KG scope it materializes (e.g. a ThreatModel or SecurityProgram). Post-MVP.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model',
         'slot_usage': {'supersedes': {'description': 'The prior revision of this '
                                                      'governed snapshot it replaces '
                                                      '(§3c R-043).',
                                       'name': 'supersedes',
                                       'range': 'GovernedView'}}})

    renders: Optional[list[str]] = Field(default=None, description="""The KG scope a GovernedView materializes (§3c R-043) — e.g. a ThreatModel or SecurityProgram. Content derives from KG state; never written back.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GovernedView']} })
    owner: Optional[str] = Field(default=None, description="""Owner/approver of a governed artifact (§3c R-043). A Party ROLE (§2b — one identity, many facets), NOT a new actor type (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'ProgramNode', 'GovernedView']} })
    revision: Optional[str] = Field(default=None, description="""Monotonic revision/version of a governed snapshot (§3c R-043). This is the saved view's \"version\"; ThreatModel and SecurityProgram name the same field `revision`. Tracked across review cycles via `supersedes`.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approved_by: Optional[list[str]] = Field(default=None, description="""Approving Review(s) of a governed artifact (§3c R-043). Approval runs through the existing Review + Assertion spine (§4) — NOT a parallel provenance mechanism (iteration-7 guardrail, DL-0010).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approval_digest: Optional[str] = Field(default=None, description="""Commit/content digest the approval is pinned to, so the sign-off is REPRODUCIBLE against KG state at a point in time (§3c R-043; SysML v2 View/Viewpoint, OMG SACM, OSCAL→Word prior art). Opaque string; digest scheme not pinned here.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    approval_status: Optional[ApprovalStatus] = Field(default=None, description="""Standing of the current sign-off, read from the approving Review(s) (§4 spine). Distinct from `governance_status` (where the snapshot is in its life): this tracks the verdict of its review cycle. Denormalized convenience — the authoritative verdict is the Review, not this field.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    governance_status: Optional[ThreatModelStatus] = Field(default=None, description="""Lifecycle of a governed snapshot (§3c R-043): draft → in-review → approved → superseded. The shared governed-view lifecycle (named for the ThreatModel case; reused by SecurityProgram and GovernedView).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    supersedes: Optional[str] = Field(default=None, description="""The prior revision of this governed snapshot it replaces (§3c R-043).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    created: Optional[datetime ] = Field(default=None, description="""When the governed artifact was created (§3c R-043 change tracking).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    updated: Optional[datetime ] = Field(default=None, description="""When the governed artifact was last updated (§3c R-043 change tracking).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ThreatModel', 'SecurityProgram', 'GovernedView']} })
    projection: Optional[ViewProjection] = Field(default=None, description="""Which derived projection this View spec names (§10).""", json_schema_extra = { "linkml_meta": {'domain_of': ['View']} })
    focus_query: Optional[str] = Field(default=None, description="""Bounded query / filter that defines the view (§10, R-033). Opaque to this schema (not a committed query language — DEC-004 is open).""", json_schema_extra = { "linkml_meta": {'domain_of': ['View']} })
    id: str = Field(default=..., description="""Stable object id (ADR-0004). Adapters must not renumber it.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    name: Optional[str] = Field(default=None, description="""Human-readable name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })
    description: Optional[str] = Field(default=None, description="""Short prose description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Node']} })


class ImpactVector(ConfiguredBaseModel):
    """
    Inlined value object for RiskScore.impact (§3). ISO 21434 safety / financial / operational / privacy, each severe|major|moderate|negligible. Keeping the four categories is the method; collapsing to one number is display-only. Not a §13 domain class. business_impact is a different post-MVP axis and is not a field here.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://threat-radar.github.io/tmodel/schema/object-model'})

    safety: Optional[ImpactSeverity] = Field(default=None, description="""Safety impact; ISO 26262-informed (§3, RQ-15-06).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ImpactVector']} })
    financial: Optional[ImpactSeverity] = Field(default=None, description="""Financial impact on the end-beneficiary, not the owner's P&L (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ImpactVector']} })
    operational: Optional[ImpactSeverity] = Field(default=None, description="""Operational impact (§3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ImpactVector']} })
    privacy: Optional[ImpactSeverity] = Field(default=None, description="""Privacy impact (§3). Not re-indexed by asset owner.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ImpactVector']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Node.model_rebuild()
Product.model_rebuild()
ProductInstance.model_rebuild()
Component.model_rebuild()
Party.model_rebuild()
Weakness.model_rebuild()
Vulnerability.model_rebuild()
AttackPattern.model_rebuild()
ThreatInstance.model_rebuild()
AttackStep.model_rebuild()
AttackPath.model_rebuild()
DamageScenario.model_rebuild()
Mitigation.model_rebuild()
RiskScore.model_rebuild()
Review.model_rebuild()
Assertion.model_rebuild()
Deployment.model_rebuild()
Environment.model_rebuild()
LifecyclePhase.model_rebuild()
RedundancyGroup.model_rebuild()
View.model_rebuild()
ThreatModel.model_rebuild()
SecurityProgram.model_rebuild()
ProgramNode.model_rebuild()
Gate.model_rebuild()
Checkpoint.model_rebuild()
Milestone.model_rebuild()
Requirement.model_rebuild()
GovernedView.model_rebuild()
ImpactVector.model_rebuild()
