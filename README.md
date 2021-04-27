# A Simple vRealize Automation 8.x reporting tool

## What is does
This tool outputs basic information about deployments and actions, such as whether they succeeded, how requested them,
what template/catalog item they map to, etc. Each action is written to a single line in a CSV file. Using a
spreadsheet application, such as Excel, one can easily create pivot tables from this and extract all kinds of
interesting statistics.

## How to run it

### Prerequisites
* Python 3.x
* Pip 3.x
* Git

```bash
git clone https://github.com/prydin/vra-reporting
cd vra-report
pip -r requirements.txt
python report.py --lookback 30 --out myfile.csv --token BLABLABLA --url https://myvra.example.com
```

### Command line parameters
