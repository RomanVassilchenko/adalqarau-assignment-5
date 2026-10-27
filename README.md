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

The Docker base image is pinned by digest. The `Jenkinsfile` runs tests, an
image build, and a container smoke run. The smoke stage compares output to
`testdata/expected-yearly-summary.csv` and archives the synthetic input and
verified output. The pipeline then replaces only its labeled local test
container, serves the generated summary at `http://127.0.0.1:18081/summary.csv`,
and checks that HTTP response against the same fixture. No external registry
or production server is used. The project uses Python's standard library only.

## Jenkins on every commit

Every push and pull request starts the `Jenkins pipeline` GitHub Actions
workflow. It builds a Jenkins LTS controller from `ci/jenkins/` (plugins and
the `assignment5` Pipeline job are defined as code), runs this repository's
`Jenkinsfile` for the pushed commit, and fails the GitHub check if the Jenkins
build is not `SUCCESS`. The Jenkins build record, console log, and verified
summary are uploaded as the run artifact.

The same script runs locally with Docker:

```sh
ci/run-jenkins.sh                  # build the current commit, then stop Jenkins
KEEP_JENKINS=1 ci/run-jenkins.sh   # keep the UI at http://127.0.0.1:18080/job/assignment5/
```

Only committed changes are built. The disposable controller has no login and
binds to `127.0.0.1` only; it mounts the Docker socket, so use it only with
trusted code. A long-running Jenkins can also use the `pollSCM` trigger in the
`Jenkinsfile`, which checks the repository every two minutes.
