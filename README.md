# A Voucher App

## Quick start:

It is recommended to use a virtualenv and install everything inside:

```bash
pip install requirements.txt
```

Then to run everything

```bash
python voucher.py customers.csv vouchers.csv --limit
```

--limit - Optional integer input to filter the customers by a limit.

## Used libraries

- click (command line tooling)
- pytest
