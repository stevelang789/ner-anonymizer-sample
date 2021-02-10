# ner-anonymizer-sample

## Overview

- Objective: to replace names of people in a DB table with 'XYZ'
- Platform: Windows 10
- Database: SQL Server 2016
- Tech stack: Python 3
- Tool: NER Anonymizer (https://pypi.org/project/ner-anonymizer/)

## Installation

Python 3.7.9 recommended. Doesn't work with Python >= 3.9 as at 9 Feb 2021.

```
pip torchvision===0.6.0 -f https://download.pytorch.org/whl/torch_stable.html
pip install ner_anonymizer
pip install pandas
pip install pyodbc
pip install sqlalchemy
```

## Usage

First, modify the connection string parameters, table name and column names as appropriate in `anonymize.py`.

At a Command Prompt:

```
anonymize.cmd
```

## How it works

- Loads records from a DB table into a pandas dataframe
- Replaces people's names with hashes (this is what ner_anonymizer does)
- Replaces the hashes with 'XYZ'
- Appends rows from the pandas dataframe into another DB table
- Does all these 1000 records at a time
- Sends 100 insert statements to the DB at a time

## Limitations

- Not obvious how to use different models
- The default model doesn't work with lowercase names
- Doesn't look for whole words, e.g., anonymizes 'Jillian' as 'a26e174e330476756d2601ea5368aec3an' (note the 'an' at the end)
