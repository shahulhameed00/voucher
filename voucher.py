import csv

import click

_INPUT_FIELD_NAMES = ["order_id", "customer", "amount_paid", "purchase_date"]
_OUTPUT_FIELD_NAMES = ["customer", "net_worth", "voucher"]


@click.command()
@click.argument("input_file", type=click.File())
@click.argument("output_file", type=click.File(mode="w"))
@click.option("--limit", default=0, help="Number of customers", type=int)
def cli(input_file, output_file, limit):
    """Calculate vouchers for each customer

    This application will calculate vouchers for either all customers 
    (if no 'limit' option is provided) or for a specified number of customers. 
    Limit can be specified using the 'limit' option. Top customers are
    calculated by their total net worth purchases made. 
    If a customer has multiple orders, all of them are summed up
    to calculate the customer's net worth.

    A voucher is 30% of the total net worth of each customer.
    """
    orders = read_orders(input_file)

    customers = collect_customer_information(orders)
    if limit:
        # If a limit option is present, filter the customers list by it.
        customers = filter_top_n_customers(customers, limit)
    calculate_vouchers(customers)
    export_vouchers(output_file, customers)


def read_orders(input_file):
    reader = csv.DictReader(input_file, fieldnames=_INPUT_FIELD_NAMES)

    # skip the header
    next(reader)

    for record in reader:
        # generate dict and convert types
        yield {
            "order_id": int(record["order_id"]),
            "customer": record["customer"],
            "amount_paid": float(record["amount_paid"]),
            "purchase_date": record["purchase_date"],
        }


def collect_customer_information(orders):
    # we use a dict to aggregate multiple orders for one customer and
    # calculate his net worth based on all order payments
    customers = {}

    for order in orders:
        name = order["customer"]

        try:
            customer = customers[name]
        except KeyError:
            default_data = {"name": name, "net_worth": 0}
            customer = customers.setdefault(name, default_data)

        customer["net_worth"] += order["amount_paid"]

    # as the customers are already aggregated we can just return them
    # as a simple list
    return list(customers.values())


def filter_top_n_customers(customers, limit):
    """
    Order the customers list by the total net worth of
    purchases made by the customers and slice it
    by the 'limit' value to return top customers. 
    """
    top_n_customers = sorted(customers, key=lambda i: i["net_worth"], reverse=True)[
        :limit
    ]
    return top_n_customers


def calculate_vouchers(customers):
    """Calculate voucher per customer based on his net worth"""
    for customer in customers:
        customer["voucher"] = customer["net_worth"] * 0.3


def export_vouchers(output_file, customers):
    writer = csv.DictWriter(output_file, fieldnames=_OUTPUT_FIELD_NAMES)
    writer.writeheader()
    writer.writerows([serialize_record(customer) for customer in customers])


def serialize_record(customer):
    return {
        "customer": customer["name"],
        # for simplicity reasons we just cut off remaining digits
        "net_worth": f'{customer["net_worth"]:.2f}',
        "voucher": f'{customer["voucher"]:.2f}',
    }


if __name__ == "__main__":
    cli()
