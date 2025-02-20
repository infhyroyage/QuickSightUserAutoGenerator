# QuickSightUserAutoGenerator

## How to use

1. Prepare Activated Amazon QuickSight Account.
2. Enter CloudShell.
3. Install Chromium:

   ```sh
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
   sudo dnf install ./google-chrome-stable_current_x86_64.rpm
   ```

4. Copy `main.py` and `requirements.txt`.
5. Create a `.env` file with the following variables:

   ```
   AWS_ACCOUNT_ID="your_aws_account_id"
   AWS_REGION="your_aws_region"
   EMAIL="example@yourdomain.com"
   QUICKSIGHT_DASHBOARD_IDS="dashboardID1,dashboardID2,..."
   QUICKSIGHT_PASSWORD="your_quicksight_password"
   ```

6. Create a `usernames.csv` CSV file with `UserName` column:

   ```
   UserName
   foo
   bar
   ```

7. Run the script:

   ```sh
   pip install -r requirements.txt 
   python main.py
   ```
