import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        session = await client.login()
        exams = await session.get_examinations()

        if not exams.reschedulable:
            print("No reschedulable examinations")
            return

        exam = exams.reschedulable[0]
        print(
            f"Rebooking: {exam.name} at {exam.data.place.display_name}, "
            f"{exam.start_date}"
        )

        # Enter rebooking flow: returns a SearchResult
        search = await exam.rebook()
        location = search.locations[0].location

        slots = await search.get_available_slots(location)
        if not slots:
            print("No available slots for rebooking")
            return

        slot = slots[0]
        print(f"New slot: {slot.date} {slot.time} — {slot.cost}")

        # Reserve the new slot
        reservation = await slot.reserve()

        # payment_info reveals rescheduling details
        info = await reservation.get_payment_info()
        print(f"Rescheduling: {info.is_rescheduling}")
        for c in info.cancellations:
            print(f"  Will cancel old: {c.name} on {c.date}")

        # Confirm the rebook
        confirmation = await reservation.confirm()
        print(f"Rebooked! New booking ID: {confirmation.booking_id}")
        for e in confirmation.confirmed_examinations:
            print(f"  Confirmed: {e.name} at {e.place.display_name}, {e.start_date}")
        for e in confirmation.cancelled_examinations:
            print(f"  Cancelled: {e.name} on {e.start_date}")


if __name__ == "__main__":
    asyncio.run(main())
