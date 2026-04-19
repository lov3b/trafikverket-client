import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        info = await logged_in.get_aspirant_information()
        aspirant = info.aspirant

        print(f"Name: {aspirant.name}")
        print(f"Personal identity number: {aspirant.personal_identity_number}")
        print(f"Age: {aspirant.age}")
        print(
            f"Address: {aspirant.address.street_address1}, {aspirant.address.zip_code} {aspirant.address.city}"
        )
        print(f"Email: {aspirant.email or 'N/A'}")
        print(f"Phone: {aspirant.phone or 'N/A'}")
        print(f"Protected identity: {aspirant.has_protected_identity}")


if __name__ == "__main__":
    asyncio.run(main())
