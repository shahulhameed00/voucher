import pytest

import voucher

# the tests usually follow the structure:
# def test():
#     1. fixture setup
#     2. running test case
#     3. assertion


@pytest.fixture
def input_file(tmp_path):
    file_path = tmp_path / 'customers.csv'

    # write some test data
    with file_path.open('w') as fh:
        fh.writelines([
            'order_id,customer,amount_paid,purchase_date\n',
            '123,c1,10.50,2019-06-01\n',
            '124,c2,20.00,2019-06-06\n',
            '125,c1,30.00,2019-06-08\n',
        ])

    # we need to open the file here already otherwise the file handler will
    # be closed before the read_orders generator access the content.
    with file_path.open() as fh:
        yield fh


@pytest.fixture
def output_file(tmp_path):
    yield tmp_path / 'vouchers.csv'


def test_read_orders(input_file):
    orders = voucher.read_orders(input_file)

    assert next(orders) == {
        'order_id': 123,
        'customer': 'c1',
        'amount_paid': 10.50,
        'purchase_date': '2019-06-01'
    }
    assert next(orders) == {
        'order_id': 124,
        'customer': 'c2',
        'amount_paid': 20.00,
        'purchase_date': '2019-06-06'
    }
    assert next(orders) == {
        'order_id': 125,
        'customer': 'c1',
        'amount_paid': 30.00,
        'purchase_date': '2019-06-08'
    }
    with pytest.raises(StopIteration):
        next(orders)


def test_collect_customer_information():
    orders = [{
        'order_id': 123,
        'customer': 'c1',
        'amount_paid': 10.50,
        'purchase_date': '2019-06-01'
    }, {
        'order_id': 124,
        'customer': 'c2',
        'amount_paid': 20.00,
        'purchase_date': '2019-06-06'
    }, {
        'order_id': 125,
        'customer': 'c1',
        'amount_paid': 30.00,
        'purchase_date': '2019-06-08'
    }]

    customers = voucher.collect_customer_information(orders)

    assert customers[0] == {
        'name': 'c1',
        'net_worth': 40.50,
    }
    assert customers[1] == {
        'name': 'c2',
        'net_worth': 20.00,
    }


def test_calculate_vouchers_for_customers():
    customers = [{
        'name': 'c1',
        'net_worth': 40.50,
    }, {
        'name': 'c2',
        'net_worth': 20.00,
    }]

    voucher.calculate_vouchers(customers)

    assert customers[0] == {
        'name': 'c1',
        'net_worth': 40.50,
        'voucher': 12.15,
    }
    assert customers[1] == {
        'name': 'c2',
        'net_worth': 20.00,
        'voucher': 6.00,
    }


def test_export_vouchers(output_file):
    customers = [{
        'name': 'c1',
        'net_worth': 40.50,
        'voucher': 12.15,
    }, {
        'name': 'c2',
        'net_worth': 20.00,
        'voucher': 6.00,
    }]

    with output_file.open('w') as fh:
        voucher.export_vouchers(fh, customers)

    with output_file.open() as fh:
        assert fh.readlines() == [
            'customer,net_worth,voucher\n',
            'c1,40.50,12.15\n',
            'c2,20.00,6.00\n',
        ]
