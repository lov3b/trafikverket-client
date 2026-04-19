import asyncio

from trafikverket_client.fp import Client
from trafikverket_client.fp.models import LicenceCategory


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        info = await logged_in.licence_information()

        # Pick the first CAR licence that has examination types available
        for licence_ref in info.by_category(LicenceCategory.CAR):
            search = await licence_ref.search_information()
            if search.examination_types:
                break
        else:
            print("No bookable CAR licence found")
            return

        exam_type = search.examination_types[0]
        location = search.locations[0].location
        print(f"Booking {exam_type.name} at {location.name}")

        # Search for available occasions
        bundles = await licence_ref.occasion_bundles(
            examination_type_id=exam_type.id,
            location_id=location.id,
        )
        if not bundles.bundles:
            print("No available occasions found")
            return

        bundle = bundles.bundles[0]
        occasion = bundle.occasions[0]
        print(f"Found slot: {occasion.date} {occasion.time} — {bundle.cost}")

        # Create a temporary reservation (15 minute hold)
        await licence_ref.create_reservation(
            examination_type_id=exam_type.id,
            occasion_bundle=bundle,
        )
        print("Reservation created (15 min hold)")

        # Optional: wait before confirming (e.g. to let a human review)
        delay_seconds = 0
        if delay_seconds > 0:
            print(f"Waiting {delay_seconds}s before confirming...")
            await asyncio.sleep(delay_seconds)

        # Check remaining time
        active = await logged_in.get_active_reservations()
        reservations = active.active_reservations or []
        if reservations:
            seconds_left = await logged_in.get_reservation_time(
                [r.reservation_expires for r in reservations]
            )
            print(f"Reservation timer: {seconds_left}s remaining")

        # Get reservation details for payment
        res_info = await licence_ref.reservation_information(
            examination_type_id=exam_type.id,
        )
        print(f"Cost: {res_info.amount_to_pay_invoice}")

        # Confirm with invoice payment
        payment = await licence_ref.invoice_payment(
            examination_type_id=exam_type.id,
            reservation_info=res_info,
        )
        print(f"Booking confirmed! ID: {payment.booking_id}")

        # Fetch summary
        result = await licence_ref.summary(payment.booking_id)
        for exam in result.confirmed_examinations:
            print(
                f"  Confirmed: {exam.name} at {exam.place.display_name}, {exam.start_date}"
            )


if __name__ == "__main__":
    asyncio.run(main())
