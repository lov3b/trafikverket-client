import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        session = await client.login()
        exams = await session.get_examinations()

        if not exams.cancellable:
            print("No cancellable examinations")
            return

        exam = exams.cancellable[0]
        print(
            f"Cancelling: {exam.name} at {exam.data.place.display_name}, "
            f"{exam.start_date}"
        )

        # Preview what will be cancelled
        preview = await exam.cancel_preview()
        if preview.show_24_hour_warning:
            print("Warning: less than 24 hours until examination!")

        for e in preview.examinations:
            print(f"  Will cancel: {e.name} (id={e.id})")

        # Confirm cancellation
        await preview.confirm()
        print("Examination cancelled")


if __name__ == "__main__":
    asyncio.run(main())
