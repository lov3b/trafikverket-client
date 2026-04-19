import asyncio

from trafikverket_client.fp import Client
from trafikverket_client.fp.models import LicenceCategory


async def main() -> None:
    async with Client() as client:
        session = await client.login()
        licences = await session.get_licences()

        # Pick the first CAR licence that has examination types available
        for licence in licences.by_category(LicenceCategory.CAR):
            search = await licence.search()
            if search.examination_types:
                break
        else:
            print("No bookable CAR licence found")
            return

        exam_type = search.examination_types[0]
        location = search.locations[0].location
        print(f"Booking {exam_type.name} at {location.name}")

        # Search for available slots
        slots = await search.get_available_slots(location)
        if not slots:
            print("No available slots found")
            return

        slot = slots[0]
        print(f"Found slot: {slot.date} {slot.time} — {slot.cost}")

        # Reserve (15 minute hold)
        reservation = await slot.reserve()
        print(f"Reserved! {await reservation.get_seconds_remaining()}s remaining")

        # Maybe you want to wait before confirming?
        delay_seconds = 30
        print(f"Waiting {delay_seconds}s before confirming...")
        await asyncio.sleep(delay_seconds)
        print(f"Still have {await reservation.get_seconds_remaining()}s")

        # Confirm with invoice payment
        confirmation = await reservation.confirm()
        print(f"Booked! ID: {confirmation.booking_id}")
        for exam in confirmation.confirmed_examinations:
            print(
                f"  Confirmed: {exam.name} at {exam.place.display_name}, "
                f"{exam.start_date}"
            )


if __name__ == "__main__":
    asyncio.run(main())
