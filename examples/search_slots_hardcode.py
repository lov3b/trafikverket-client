import asyncio
from datetime import datetime, timedelta, timezone

from trafikverket_client.fp import Client, ShowQr
from trafikverket_client.fp.models import LicenceCategory


async def main() -> None:
    async with Client() as client:
        print("Logging in... Please scan the code below using BankID:")
        logged_in = await client.login(show_qr=ShowQr.ALWAYS)
        licence_information = await logged_in.licence_information()
        licence = licence_information.get(name="B96", category=LicenceCategory.CAR)
        search = await licence.search_information()
        examination_type = search.examination_types[0]

        location = next(
            entry.location
            for entry in search.locations
            if entry.location.name == "Linköping"
        )

        bundles = await licence.occasion_bundles(
            examination_type_id=examination_type.id,
            location_id=location.id,
            start_date=datetime.now(timezone.utc) + timedelta(days=1),
        )

        n = len(bundles.bundles)
        print(
            f"Found {n} bundle{'s' * (n != 1)} for {examination_type.name} at {location.name}"
        )
        for bundle in bundles.bundles:
            occasion = bundle.occasions[0]
            print(
                f"- {occasion.date.isoformat()} {occasion.time.isoformat(timespec='minutes')} "
                f"{occasion.location_name} ({bundle.cost})"
            )


if __name__ == "__main__":
    asyncio.run(main())
