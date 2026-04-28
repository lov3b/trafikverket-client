import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        session = await client.login()

        reservations = await session.get_active_reservations()
        if not reservations:
            print("No active reservations")
            return

        reservation = reservations[0]
        seconds_left = await reservation.get_seconds_remaining()

        print(f"Reservation: {reservation.examination_name}")
        print(f"Starts at: {reservation.start_date.isoformat(sep=' ')}")
        print(f"Expires at: {reservation.expires_at.isoformat(sep=' ')}")
        print(f"Seconds left to finish payment/booking: {seconds_left}")


if __name__ == "__main__":
    asyncio.run(main())
