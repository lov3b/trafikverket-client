import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        licence_information = await logged_in.licence_information()
        print(f"Logged in as: {licence_information.personal_identity_number}")

        current = licence_information.current
        if current is not None:
            print(f"Current licence: {current.name} ({current.id})")

        print("Available licences:")
        for licence_ref in licence_information.all():
            print(
                f"- id={licence_ref.id} name={licence_ref.name} "
                f"category={licence_ref.category}"
            )


if __name__ == "__main__":
    asyncio.run(main())
