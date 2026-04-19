import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        active = await logged_in.get_active_reservations()
        reservations = active.active_reservations or []
        if not reservations:
            print("No active reservations")
            return

        first = reservations[0]
        seconds_left = await logged_in.get_reservation_time([first.reservation_expires])

        print(f"Reservation: {first.examination_name}")
        print(f"Starts at: {first.start_date.isoformat(sep=' ')}")
        print(f"Expires at: {first.reservation_expires.isoformat(sep=' ')}")
        print(f"Seconds left to finish payment/booking: {seconds_left}")


if __name__ == "__main__":
    asyncio.run(main())
