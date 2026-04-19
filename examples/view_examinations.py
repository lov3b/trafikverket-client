import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        session = await client.login()
        exams = await session.get_examinations()

        print(f"Confirmed examinations ({len(exams.confirmed)}):")
        for exam in exams.confirmed:
            print(
                f"  - {exam.name} at {exam.data.place.display_name}, "
                f"{exam.start_date}, status={exam.data.status}"
            )

        print(f"\nCompleted examinations ({len(exams.completed)}):")
        for exam in exams.completed:
            result = exam.data.result.name if exam.data.result else "N/A"
            print(
                f"  - {exam.name} at {exam.data.place.display_name}, "
                f"{exam.start_date}, result={result}"
            )


if __name__ == "__main__":
    asyncio.run(main())
