# Question 2: Balance Sheet JSON Validation

This container runs a python script that reads the json locally and validates the json schema and the balance sheet equation.

Full disclosure, I used an AI tool to write some of the code (cursor).

## Usage

To run the project, use the following commands:

- `make build` # Build the docker container
- `make run` # Run the code

Note: you will need to have docker installed in order to run the code.
Alternatively, you can run the code using `python3 validate_balance_sheet_json.py` and venv.

I'm using uv to handle all python dependencies.

## Assumptions

- I assumed that the overall format of the json is created by the flex product code. Therefore should be relatively consistent.
- I assumed the currency of the data was consistent.
- I didn't really know how the json data was coming in. For simplicity I just read it directly. In prod it's probably not this simple.


## Approach

I used a simple approach to validate the balance sheet.
1) I used the jsonschema library to validate the json file wasn't malformed. This would validate the data types and ensure type safety downstream.

2) If the schema was valid, I then created a nested routine to validate the balance sheet equation. I suspect the third party accounting softwares allow as much nesting as you want, so I made this dynamic to handle such a case.

3) If the balance sheet equation is valid, convert the data to tabular form. Since the balance sheet equation is valid, we should no longer care about the parent nodes. Example: if all the assets balance, we can get rid of the parent node and only have account level data (with dimentions that describe the account).


## Issues I noticed with the data

- My code highlighted an issue with the current liabilities. The sum of the children did not equal the parent (current liabilities). Maybe a bug or incorrect decimal in the data.
- I also noticed that `Settle Loans Payable` had an odd account id. Should be a UUID. I would investigate this further.
- Some of the values for the accounts were wildly unexpected. I wouldn't expect a chequing account to have such a large negative value. I would want to investigate this further.
- We're not given any information about the currency of the data. It's pretty common for businesses to have multiple currencies, so this would be a good addition to the json.

## What I would do next if you had more time

In no particular order:
- I would definitely want to get feedback from others on everything I've done. I'm sure I missed a lot of things and would want to make sure I'm on the right track.
- Add more formal and flushed out documentation.
- Adding testing & CICD (lint & formatting) would make deployments more consistent and safer.
- A library like `pydantic` would be a good addition for production. Dataclasses or pandera would be a good alternatives as well.
- I would want to ingest the data into a datawarehouse in tabular form. This would allow for more flexibility in querying and analysis for downstream reporting.
- DBT downstream would be a good addition for OLAP processing and reporting. (I would use duckdb locally and then whatever datawarehouse you have)
- DBT tests on the values within dbt would be a good idea. Making sure values are within an expected range (maybe take the std of new data and then use that as a threshold). This could be done at a row level or a column level.
- I would want to clean up and normalize the tabular data where I can. Add ingestion timestamps and try to maintain state within the pipeline.
- Adding alerts and notifications would be a good idea. Pagerduty, Slack, etc. Cloudwatch, Datadog or an equivalent could be a good idea.
- I would add some accounting reporting around the data. Example: quick ratio, current ratio, etc.
- Add better logging and error handling so another user can easily understand what went wrong.