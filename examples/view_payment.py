import asyncio

from trafikverket_client.fp import Client


async def main() -> None:
    async with Client() as client:
        logged_in = await client.login()

        payment = await logged_in.get_payment_model()

        print(f"Has debt: {payment.has_debt}")
        print(f"Available balance: {payment.available_balance:.2f} SEK")
        print(f"Locked balance: {payment.locked_balance:.2f} SEK")
        print(f"Unpaid amount: {payment.unpaid_amount:.2f} SEK")

        if payment.unpaid_history_models:
            print(f"\nUnpaid items ({len(payment.unpaid_history_models)}):")
            for item in payment.unpaid_history_models:
                print(
                    f"  - {item.product_name}: {item.remaining_amount_to_pay:.2f} SEK "
                    f"(ordered {item.order_item_date_str})"
                )

        if payment.paid_history_models:
            print(f"\nPaid items ({len(payment.paid_history_models)}):")
            for item in payment.paid_history_models:
                print(
                    f"  - {item.product_name}: {item.paid_amount:.2f} SEK "
                    f"(ordered {item.order_item_date_str})"
                )


if __name__ == "__main__":
    asyncio.run(main())
