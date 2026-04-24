import asyncio
import webbrowser
from urllib.parse import urlencode

from trafikverket_client.fp import Client, Session


def make_bankid_autostart_url(autostart_token: str) -> str:
    query = urlencode({"autostarttoken": autostart_token, "redirect": "null"})
    return f"bankid:///?{query}"


def make_bankid_app_url(autostart_token: str) -> str:
    query = urlencode({"autostarttoken": autostart_token, "redirect": "null"})
    return f"https://app.bankid.com/?{query}"


async def main() -> None:
    async with Client() as client:
        loginable = await client.begin_login(show_qr=False)

        autostart_token = loginable.authentication_data.autostart_token
        bankid_url = make_bankid_autostart_url(autostart_token)
        fallback_url = make_bankid_app_url(autostart_token)

        print("BankID autostart URL:")
        print(bankid_url)
        print()
        print("Browser fallback URL:")
        print(fallback_url)
        print()

        try:
            opened = webbrowser.open(bankid_url)
            if not opened:
                webbrowser.open(fallback_url)
        except webbrowser.Error:
            pass

        logged_in = await loginable.wait_until_logged_in()
        session = Session(logged_in.into_context())

        licences = await session.get_licences()
        print(f"Logged in as: {licences.personal_identity_number}")


if __name__ == "__main__":
    asyncio.run(main())
