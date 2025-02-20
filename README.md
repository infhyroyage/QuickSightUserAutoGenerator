# QuickSightUserAutoGenerator

## How to use

1. Prepare Activated Amazon QuickSight Account.
2. Enter CloudShell.
3. Copy `main.py`.
4. Create a `.env` file with the following variables:

   ```
   AWS_ACCOUNT_ID="your_aws_account_id"
   AWS_REGION="your_aws_region"
   EMAIL="example@yourdomain.com"
   QUICKSIGHT_DASHBOARD_IDS="dashboardID1,dashboardID2,..."
   QUICKSIGHT_PASSWORD="your_quicksight_password"
   ```

5. Create a `usernames.csv` CSV file with `UserName` column:

   ```
   UserName
   foo
   bar
   ```

6. Run the script:

   ```sh
   pip install python-dotenv selenium
   python main.py
   ```
