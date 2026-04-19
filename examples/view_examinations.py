import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        data = await logged_in.get_examinations()

        print(f"Confirmed examinations ({len(data.confirmed_examinations)}):")
        for exam in data.confirmed_examinations:
            print(
                f"  - {exam.name} at {exam.place.display_name}, "
                f"{exam.start_date}, status={exam.status}"
            )

        print(f"\nCompleted examinations ({len(data.completed_examinations)}):")
        for exam in data.completed_examinations:
            result = exam.result.name if exam.result else "N/A"
            print(
                f"  - {exam.name} at {exam.place.display_name}, "
                f"{exam.start_date}, result={result}"
            )


if __name__ == "__main__":
    asyncio.run(main())
