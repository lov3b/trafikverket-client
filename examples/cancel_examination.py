import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        data = await logged_in.get_examinations()

        cancellable = [e for e in data.confirmed_examinations if e.can_cancel]
        if not cancellable:
            print("No cancellable examinations")
            return

        exam = cancellable[0]
        print(
            f"Cancelling: {exam.name} at {exam.place.display_name}, {exam.start_date}"
        )

        # Preview what will be cancelled
        preview = await logged_in.examinations_to_cancel(exam.id)
        if preview.show_24_hour_cancellation_warning:
            print("Warning: less than 24 hours until examination!")

        for e in preview.examinations:
            print(f"  Will cancel: {e.name} (id={e.id})")

        # Confirm cancellation
        await logged_in.confirm_cancel(exam.id)
        print("Examination cancelled")


if __name__ == "__main__":
    asyncio.run(main())
