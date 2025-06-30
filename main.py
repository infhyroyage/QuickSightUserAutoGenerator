"""QuickSight User Auto Generator"""

import csv
import logging
import os

import boto3
from dotenv import load_dotenv
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

QUICKSIGHT_DASHBOARD_REQUIRED_ACTIONS: list[str] = [
    "quicksight:DescribeDashboard",
    "quicksight:ListDashboardVersions",
    "quicksight:QueryDashboard",
]

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    registered_names: list[str] = [user["UserName"] for user in response["UserList"]]
    return [name for name in all_names if name not in registered_names]


def register_quicksight_user(client: boto3.client, name: str) -> str:
    """Register a QuickSight Reader User whose Identity Type is QuickSight.

    Args:
        client (boto3.client): QuickSight Boto3 Client
        name (str): QuickSight User Name

    Returns:
        str: The QuickSight URL(UserInvitationUrl) to activate a QuickSight User
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


def activate_quicksight_user(driver: Chrome, url: str) -> None:
    """Activate a QuickSight User.

    Args:
        driver (selenium.webdriver.Chrome): Selenium Chrome Driver
        url (str): Return value of register_quicksight_user()
    """

    # Open UserInvitationUrl
    driver.get(url)

    # Get input#awsui-input-1 Element and Set QuickSight Password
    input_awsui_input_1 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "awsui-input-1"))
    )
    input_awsui_input_1.send_keys(os.getenv("QUICKSIGHT_PASSWORD"))

    # Get input#awsui-input-0 Element and Set QuickSight Password
    input_awsui_input_0 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "awsui-input-0"))
    )
    input_awsui_input_0.send_keys(os.getenv("QUICKSIGHT_PASSWORD"))

    # Get button with type="submit" and Click
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    submit_button.click()

    # Wait to Activate a QuickSight User Successfully
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div.awsui-alert.awsui-alert-type-success")
        )
    )


def get_quicksight_dashboard_ids() -> list[str]:
    """Get QuickSight Dashboard IDs.

    Returns:
        list[str]: QuickSight Dashboard IDs
    """

    dashboard_ids: str = os.getenv("QUICKSIGHT_DASHBOARD_IDS")
    return [d.strip() for d in dashboard_ids.split(",")] if dashboard_ids else []


def get_non_permissioned_quicksight_users(
    client: boto3.client, all_names: list[str], dashboard_id: str
) -> list[str]:
    """Get Non-permissioned QuickSight Users for a Dashboard.

    Args:
        client (boto3.client): QuickSight Boto3 Client
        all_names (list[str]): All QuickSight User Names
        dashboard_id (str): QuickSight Dashboard ID
    Returns:
        list[str]: Non-permissioned QuickSight Users for a Dashboard
    """

    response = client.describe_dashboard_permissions(
        AwsAccountId=os.getenv("AWS_ACCOUNT_ID"),
        DashboardId=dashboard_id,
    )

    permissioned_users: list[str] = []
    for user_name in all_names:
        principal: str = (
            f"arn:aws:quicksight:{os.getenv('AWS_REGION')}:"
            f"{os.getenv('AWS_ACCOUNT_ID')}:user/default/{user_name}"
        )
        for permission in response["Permissions"]:
            if permission["Principal"] == principal and set(QUICKSIGHT_DASHBOARD_REQUIRED_ACTIONS).issubset(set(permission["Actions"])):
                permissioned_users.append(user_name)
                break

    return [user_name for user_name in all_names if user_name not in permissioned_users]


def grant_dashboard_permission(
    client: boto3.client, name: str, dashboard_id: str
) -> None:
    """Grant Permissions to a QuickSight User for a Dashboard.

    Args:
        client (boto3.client): QuickSight Boto3 Client
        name (str): QuickSight User Name
        dashboard_id (str): QuickSight Dashboard ID
    """

    principal: str = (
        f"arn:aws:quicksight:{os.getenv('AWS_REGION')}:"
        f"{os.getenv('AWS_ACCOUNT_ID')}:user/default/{name}"
    )
    client.update_dashboard_permissions(
        AwsAccountId=os.getenv("AWS_ACCOUNT_ID"),
        DashboardId=dashboard_id,
        GrantPermissions=[
            {
                "Actions": QUICKSIGHT_DASHBOARD_REQUIRED_ACTIONS,
                "Principal": principal,
            }
        ],
    )


if __name__ == "__main__":
    # Create a QuickSight Boto3 Client
    quicksight_client: boto3.client = boto3.client(
        "quicksight", region_name=os.getenv("AWS_REGION")
    )

    # Read All Values of only "UserName" Column from CSV file
    with open("usernames.csv", newline="", encoding="utf-8") as file:
        usernames: list[str] = [row["UserName"] for row in csv.DictReader(file)]

    # Get Non-registered QuickSight users
    non_registered_usernames: list[str] = get_non_registered_quicksight_users(
        quicksight_client, usernames
    )
    logger.info(
        "[get_non_registered_quicksight_users] OK: %d", len(non_registered_usernames)
    )

    # Create a Selenium Chrome Driver
    options: Options = Options()
    options.add_argument("--headless")  # Headless Mode
    options.add_argument("--disable-gpu")  # Disable GPU Hardware Acceleration
    chrome_driver: Chrome = Chrome(options=options)
    try:
        for i, username in enumerate(non_registered_usernames):
            # Register a QuickSight user
            user_invitation_url: str = register_quicksight_user(
                quicksight_client,
                username,
            )
            logger.info(
                "[register_quicksight_user] OK(%d/%d): %s",
                i + 1,
                len(non_registered_usernames),
                username,
            )

            # Activate a QuickSight user
            activate_quicksight_user(chrome_driver, user_invitation_url)
            logger.info(
                "[activate_quicksight_user] OK(%d/%d): %s",
                i + 1,
                len(non_registered_usernames),
                username,
            )

        # Read QuickSight Dashboard IDs
        quicksight_dashboard_ids: list[str] = get_quicksight_dashboard_ids()

        for quicksight_dashboard_id in quicksight_dashboard_ids:
            # Get Non-permissioned QuickSight Users for each Dashboard
            non_permissioned_usernames: list[str] = get_non_permissioned_quicksight_users(
                quicksight_client, usernames, quicksight_dashboard_id
            )
            logger.info(
                "[get_non_permissioned_quicksight_users] OK(%s): %s",
                quicksight_dashboard_id,
                len(non_permissioned_usernames),
            )

            for i, username in enumerate(non_permissioned_usernames):
                # Grant Permissions to a QuickSight User for a Dashboard
                grant_dashboard_permission(
                    quicksight_client, username, quicksight_dashboard_id
                )
                logger.info(
                    "[grant_dashboard_permission] OK(%s,%d/%d): %s",
                    quicksight_dashboard_id,
                    i + 1,
                    len(non_permissioned_usernames),
                    username,
                )
    except Exception as e:
        chrome_driver.save_screenshot("error.png")
        raise e
    finally:
        # Close the Selenium Chrome Driver
        chrome_driver.quit()
