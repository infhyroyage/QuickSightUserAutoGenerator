"""QuickSight User Auto Generator"""

import csv
import os

import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_non_registered_quicksight_users(
    client: boto3.client, all_names: list[str]
) -> list[str]:
    """Get Non-registered QuickSight Users.

    Args:
        client (boto3.client): QuickSight Boto3 Client
        all_names (list[str]): All QuickSight User Names
    Returns:
        list[str]: Non-registered QuickSight Users
    """

    # Execute ListUsers API
    response = client.list_users(
        AwsAccountId=os.getenv("AWS_ACCOUNT_ID"),
        Namespace="default",
    )

    # Filter Non-registered QuickSight Users
    registered_names = [user["UserName"] for user in response["UserList"]]
    return [name for name in all_names if name not in registered_names]


def register_quicksight_user(client: boto3.client, name: str) -> str:
    """Register a QuickSight Reader User whose Identity Type is QuickSight.

    Args:
        client (boto3.client): QuickSight Boto3 Client
        name (str): QuickSight User Name

    Returns:
        str: Response value of UserInvitationUrl
    """

    # Execute RegisterUser API
    response = client.register_user(
        AwsAccountId=os.getenv("AWS_ACCOUNT_ID"),
        Namespace="default",
        IdentityType="QUICKSIGHT",
        UserRole="READER",
        Email=os.getenv("EMAIL"),
        UserName=name,
    )

    # Choose UserInvitationUrl from response
    return response["UserInvitationUrl"]


if __name__ == "__main__":
    # Create a QuickSight Boto3 Client
    quicksight_client: boto3.client = boto3.client(
        "quicksight", region_name=os.getenv("AWS_REGION")
    )

    # Read All Values of "name" Column from CSV file
    with open("usernames.csv", newline="", encoding="utf-8") as file:
        usernames: list[str] = [row["name"] for row in csv.DictReader(file)]

    # Get Non-registered QuickSight users
    non_registered_usernames: list[str] = get_non_registered_quicksight_users(
        quicksight_client, usernames
    )
    print(f"[get_non_registered_quicksight_users] OK: {len(non_registered_usernames)}")

    for username in non_registered_usernames:
        # Register a QuickSight user
        user_invitation_url = register_quicksight_user(quicksight_client, username)
        print(f"[register_quicksight_user] OK: {username}")
        print(f"UserInvitationUrl: {user_invitation_url}")  # DEBUG
