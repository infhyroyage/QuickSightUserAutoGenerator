# QuickSightUserAutoGenerator

Prepare Activated Amazon QuickSight Account.
Enter CloudShell.
Copy `main.py`.
Create a `.env` file with the following variables:

```
AWS_ACCOUNT_ID="your_aws_account_id"
AWS_REGION="your_aws_region"
EMAIL="example@yourdomain.com"
QUICKSIGHT_PASSWORD="your_quicksight_password"
```

Create a `usernames.csv` CSV file with `name` column:

```
name
foo
bar
```

Run the script:

```sh
pip install python-dotenv selenium
python main.py
```
