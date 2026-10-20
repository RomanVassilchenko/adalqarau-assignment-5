# Synthetic yearly procurement summary

A small Python standard-library example for Assignment 5. It aggregates
synthetic procurement records by year. No private AdalQarau data is included.

Input CSV has exactly these columns in this order:

```csv
contract_id,contract_date,amount_kzt
SYN-001,2024-03-12,125000
```

IDs must be nonempty and unique, dates must be valid ISO calendar dates, and
amounts must be nonnegative whole KZT values. Output rows are sorted by year
and contain record counts and summed amounts.

```sh
python3 -m unittest -v
python3 processor.py testdata/contracts.csv /tmp/yearly-summary.csv
docker build -t adalqarau-a5:local .
docker run --rm adalqarau-a5:local sh -c 'python processor.py testdata/contracts.csv /tmp/summary.csv && cat /tmp/summary.csv'
```

The Docker base image is pinned by digest. Jenkins checks SCM every two
minutes; a changed revision triggers tests, an image build, and a container
smoke run. The smoke stage compares output to
`testdata/expected-yearly-summary.csv` and archives the synthetic input and
verified output. The project uses Python's standard library only.
