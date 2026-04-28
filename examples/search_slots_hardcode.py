import asyncio

from trafikverket_client.fp import Client
from trafikverket_client.fp.models import LicenceCategory


async def main() -> None:
    async with Client() as client:
        print("Logging in... Please scan the code below using BankID:")
        session = await client.login()
        licences = await session.get_licences()
        licence = licences.get(name="B96", category=LicenceCategory.CAR)
        search = await licence.search()
        examination_type = search.examination_types[0]

        location = next(
            entry.location
            for entry in search.locations
            if entry.location.name == "Linköping"
        )

        slots = await search.get_available_slots(location)

        n = len(slots)
        print(
            f"Found {n} slot{'s' * (n != 1)} for {examination_type.name} at {location.name}"
        )
        for slot in slots:
            print(
                f"- {slot.date.isoformat()} {slot.time.isoformat(timespec='minutes')} "
                f"{slot.location_name} ({slot.cost})"
            )


if __name__ == "__main__":
    asyncio.run(main())
