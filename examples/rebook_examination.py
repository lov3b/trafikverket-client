import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        data = await logged_in.get_examinations()

        reschedulable = [e for e in data.confirmed_examinations if e.can_reschedule]
        if not reschedulable:
            print("No reschedulable examinations")
            return

        exam = reschedulable[0]
        print(f"Rebooking: {exam.name} at {exam.place.display_name}, {exam.start_date}")

        info = await logged_in.licence_information()
        licence_ref = info.get(licence_id=exam.licence_id)

        # Search for new slots
        search = await licence_ref.search_information(
            examination_type_id=exam.examination_type_id,
        )
        location = search.locations[0].location

        bundles = await licence_ref.occasion_bundles(
            examination_type_id=exam.examination_type_id,
            location_id=location.id,
        )
        if not bundles.bundles:
            print("No available slots for rebooking")
            return

        bundle = bundles.bundles[0]
        new_occasion = bundle.occasions[0]
        print(f"New slot: {new_occasion.date} {new_occasion.time} — {bundle.cost}")

        # Reserve the new slot
        await licence_ref.create_reservation(
            examination_type_id=exam.examination_type_id,
            occasion_bundle=bundle,
        )

        # Get reservation info (will show isRescheduling=True, cancellations=[old booking])
        res_info = await licence_ref.reservation_information(
            examination_type_id=exam.examination_type_id,
        )
        print(f"Rescheduling: {res_info.is_rescheduling}")
        for c in res_info.cancellations:
            print(f"  Will cancel: {c.name} on {c.date}")

        # Confirm the rebook via invoice payment
        payment = await licence_ref.invoice_payment(
            examination_type_id=exam.examination_type_id,
            reservation_info=res_info,
        )
        print(f"Rebooked! New booking ID: {payment.booking_id}")

        result = await licence_ref.summary(payment.booking_id)
        for e in result.confirmed_examinations:
            print(f"  Confirmed: {e.name} at {e.place.display_name}, {e.start_date}")
        for e in result.cancelled_examinations:
            print(f"  Cancelled: {e.name} on {e.start_date}")


if __name__ == "__main__":
    asyncio.run(main())
