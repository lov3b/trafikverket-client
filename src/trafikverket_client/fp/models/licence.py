from enum import StrEnum
from typing import Iterator, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from pydantic.alias_generators import to_camel


class LicenceCategory(StrEnum):
    """Values the ``category`` field on a :class:`Licence` can take.

    Ten distinct values, each appearing as the per-licence ``category`` tag
    on the wire. ``StrEnum`` so these serialise transparently.

    See also :class:`LicenceGroup` for the outer grouping labels, which
    use a different naming scheme; :attr:`group` maps between them.
    """

    MOTORCYCLE = "Motorcycle"
    CAR = "Car"
    TRUCK = "Truck"
    BUS = "Bus"
    MOPED = "Moped"
    TRACTOR = "Tractor"
    PROFESSIONAL_KNOWLEDGE = "ProfessionalKnowledge"
    PROFESSIONAL_DRIVER = "ProfessionalDriver"
    MSB = "MSB"
    # Sits inside `LicenceGroup.SIK` on the wire — see the mapping below.
    CERT = "Cert"

    @property
    def group(self) -> "LicenceGroup":
        """The containing :class:`LicenceGroup` this category belongs to."""
        return _CATEGORY_TO_GROUP[self]


class LicenceGroup(StrEnum):
    """Values the outer ``name`` field on a licence group can take.

    These are the ``licence<Something>`` labels used to bucket related
    licences in the tree. Nine of them mirror :class:`LicenceCategory`
    with a ``licence`` prefix; ``SIK`` is the odd one (its inner
    licences have ``category="Cert"``).
    """

    MOTORCYCLE = "licenceMotorcycle"
    CAR = "licenceCar"
    TRUCK = "licenceTruck"
    BUS = "licenceBus"
    MOPED = "licenceMoped"
    TRACTOR = "licenceTractor"
    PROFESSIONAL_KNOWLEDGE = "licenceProfessionalKnowledge"
    PROFESSIONAL_DRIVER = "licenceProfessionalDriver"
    MSB = "licenceMSB"
    SIK = "licenceSIK"

    @property
    def category(self) -> LicenceCategory:
        """The :class:`LicenceCategory` value licences in this group carry."""
        return _GROUP_TO_CATEGORY[self]


# Bidirectional mapping between the two namespaces. Derived by inspection
# of the `licence-information` response — the relation is 1:1, a property
# the server currently upholds.
_GROUP_TO_CATEGORY: dict[LicenceGroup, LicenceCategory] = {
    LicenceGroup.MOTORCYCLE: LicenceCategory.MOTORCYCLE,
    LicenceGroup.CAR: LicenceCategory.CAR,
    LicenceGroup.TRUCK: LicenceCategory.TRUCK,
    LicenceGroup.BUS: LicenceCategory.BUS,
    LicenceGroup.MOPED: LicenceCategory.MOPED,
    LicenceGroup.TRACTOR: LicenceCategory.TRACTOR,
    LicenceGroup.PROFESSIONAL_KNOWLEDGE: LicenceCategory.PROFESSIONAL_KNOWLEDGE,
    LicenceGroup.PROFESSIONAL_DRIVER: LicenceCategory.PROFESSIONAL_DRIVER,
    LicenceGroup.MSB: LicenceCategory.MSB,
    LicenceGroup.SIK: LicenceCategory.CERT,
}
_CATEGORY_TO_GROUP: dict[LicenceCategory, LicenceGroup] = {
    v: k for k, v in _GROUP_TO_CATEGORY.items()
}


class Licence(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    description: str
    language_key_name: str
    language_key_description: str
    category: LicenceCategory
    icon: str
    sort_order: int


class LicenceCategoryGroup(BaseModel):
    """A named bucket of licences grouping by type (e.g. ``licenceCar``).

    The :attr:`name` is a :class:`LicenceGroup` — the outer label from the
    wire. It does not always equal the per-licence ``category`` field
    (the only current mismatch is ``licenceSIK`` ↔ ``Cert``); use
    ``name.category`` to jump between the two.
    """

    name: LicenceGroup
    licences: list[Licence]

    @property
    def category(self) -> LicenceCategory:
        """Shortcut for ``self.name.category``."""
        return self.name.category


class LicenceInformationData(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    enable_social_security_number: bool
    personal_identity_number: str = Field(alias="socialSecurityNumber")
    """I refuse to call this a social security number. It's not and it never has been"""
    licence_id: int
    licence_categories: list[LicenceCategoryGroup]

    def iter_licences(self) -> Iterator[Licence]:
        """Flat iterator over every :class:`Licence` in the tree."""
        for group in self.licence_categories:
            yield from group.licences

    def find_by_id(self, licence_id: int) -> Optional[Licence]:
        """Lookup a licence by its numeric id, or ``None`` if not present."""
        for licence in self.iter_licences():
            if licence.id == licence_id:
                return licence
        return None

    def find(
        self,
        name: Optional[str] = None,
        category: Optional[LicenceCategory] = None,
        group: Optional[LicenceGroup] = None,
    ) -> Optional[Licence]:
        """Lookup a licence by name, category, and/or containing group.

        Licence ``name`` values are **not globally unique** — e.g. ``"Buss"``
        exists as both ``ProfessionalKnowledge`` (id 29) and
        ``ProfessionalDriver`` (id 21). Pass ``category`` (or the
        equivalent ``group``) to disambiguate, or use :meth:`find_by_id`
        when you already know the numeric id.
        """
        if group is not None and category is not None:
            if group.category != category:
                # Caller passed contradictory filters; nothing can match.
                return None
        effective_category = category or (group.category if group else None)
        for licence in self.iter_licences():
            if name is not None and licence.name != name:
                continue
            if (
                effective_category is not None
                and licence.category != effective_category
            ):
                continue
            return licence
        return None

    @property
    def current_licence(self) -> Optional[Licence]:
        """The licence currently selected on the backend, if it's in the tree."""
        return self.find_by_id(self.licence_id)


class LicenceInformationResponse(BaseModel):
    data: LicenceInformationData
    status: int
    url: HttpUrl
