"""QuickSight User Auto Generator"""

import csv
import os

import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def register_quicksight_user(client: boto3.client, username: str) -> str:
    """Register a QuickSight Reader User with QuickSight Identity Type.

    Args:
        client (boto3.client): QuickSight Boto3 Client
        username (str): QuickSight User Name

    Returns:
        str: Response value of UserInvitationUrl
    """

    response = client.register_user(
        AwsAccountId=os.getenv("AWS_ACCOUNT_ID"),
        Namespace="default",
        IdentityType="QUICKSIGHT",
        UserRole="READER",
        Email=os.getenv("EMAIL"),
        UserName=username,
    )
    return response["UserInvitationUrl"]


if __name__ == "__main__":
    # Create a QuickSight Boto3 Client
    quicksight_client: boto3.client = boto3.client(
        "quicksight", region_name=os.getenv("AWS_REGION")
    )

    # Read usernames from CSV file
    with open("usernames.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Register a QuickSight user
            user_invitation_url = register_quicksight_user(
                quicksight_client, row["name"]
            )
            print(f"[register_quicksight_user] OK: {row['name']}")
            print(f"UserInvitationUrl: {user_invitation_url}")  # DEBUG
