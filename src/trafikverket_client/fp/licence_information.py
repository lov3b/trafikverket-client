from typing import TYPE_CHECKING, Optional

from .models import (
    LicenceCategory,
    LicenceGroup,
    LicenceInformationData,
)
from .exceptions import LicenceNotFoundError
from .licence_ref import LicenceRef

if TYPE_CHECKING:
    from .logged_in_client import LoggedinClient


class LicenceInformation:
    """Populated, queryable view over :class:`LicenceInformationData`."""

    def __init__(self, client: "LoggedinClient", data: LicenceInformationData) -> None:
        self._client = client
        self._data = data

    @property
    def data(self) -> LicenceInformationData:
        return self._data

    @property
    def personal_identity_number(self) -> str:
        return self._data.personal_identity_number

    @property
    def current(self) -> Optional[LicenceRef]:
        licence = self._data.current_licence
        if licence is None:
            return None
        return LicenceRef(self._client, licence.id, licence=licence)

    def all(self) -> list[LicenceRef]:
        return [
            LicenceRef(self._client, lic.id, licence=lic)
            for lic in self._data.iter_licences()
        ]

    def by_category(self, category: LicenceCategory) -> list[LicenceRef]:
        return [
            LicenceRef(self._client, license.id, licence=license)
            for license in self._data.iter_licences()
            if license.category == category
        ]

    def by_group(self, group: LicenceGroup) -> list[LicenceRef]:
        return self.by_category(group.category)

    def get(
        self,
        name: Optional[str] = None,
        category: Optional[LicenceCategory] = None,
        group: Optional[LicenceGroup] = None,
        licence_id: Optional[int] = None,
    ) -> LicenceRef:
        if licence_id is not None:
            licence = self._data.find_by_id(licence_id)
            if licence is None:
                raise LicenceNotFoundError(f"No licence with id={licence_id}")
            return LicenceRef(self._client, licence.id, licence=licence)

        if group is not None and category is not None and group.category != category:
            raise ValueError(
                f"Contradictory filters: group={group!r} implies "
                f"category={group.category!r}, but category={category!r} was given"
            )
        effective_category = category or (group.category if group else None)

        if name is None and effective_category is None:
            raise ValueError(
                "Pass licence_id, or name, or category/group (or a name+category pair)"
            )

        matches = [
            lic
            for lic in self._data.iter_licences()
            if (name is None or lic.name == name)
            and (effective_category is None or lic.category == effective_category)
        ]
        if not matches:
            raise LicenceNotFoundError(
                f"No licence matches name={name!r} category={effective_category!r}"
            )
        if len(matches) > 1:
            ids = [m.id for m in matches]
            raise ValueError(
                f"Ambiguous: {len(matches)} licences match name={name!r} "
                f"category={effective_category!r} (ids={ids}) - add the missing filter"
            )
        [licence] = matches
        return LicenceRef(self._client, licence.id, licence=licence)
