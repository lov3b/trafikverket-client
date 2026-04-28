import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        session = await client.login()
        licences = await session.get_licences()
        print(f"Logged in as: {licences.personal_identity_number}")

        current = licences.current
        if current is not None:
            print(f"Current licence: {current.name} ({current.id})")

        print("Available licences:")
        for licence in licences.all():
            print(f"- id={licence.id} name={licence.name} category={licence.category}")


if __name__ == "__main__":
    asyncio.run(main())
