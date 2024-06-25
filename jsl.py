import getpass
import os
import sys
import json
import argparse
import logging
from jira import JIRA
from dotenv import load_dotenv
import csv
from requests.auth import HTTPBasicAuth
from jira.exceptions import JIRAError
from datetime import datetime
import blessed
from blessed import Terminal
import logging
from jira import JIRAError
import requests


def load_dotenv():
    """
    Load environment variables from a .env file.
    """
    # Implementation of load_dotenv() function goes here


def load_credentials(file_path):
    """
    Load credentials from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing credentials.

    Returns:
        dict: A dictionary containing the loaded credentials.
    """
    with open(file_path, "r") as f:
        credentials = json.load(f)
    return credentials


def set_environment_variables(credentials):
    """
    Set environment variables from credentials.

    Args:
        credentials (dict): A dictionary containing the credentials.

    """
    os.environ["JIRA_URL"] = credentials["jira_url"]
    os.environ["API_TOKEN"] = credentials["api_token"]
    os.environ["USER"] = credentials["user"]


def initialize(config_file):
    """
    Initialize the application by loading credentials and setting environment variables.

    Args:
        config_file (str): Path to the configuration file.

    """
    if os.path.exists(config_file):
        credentials = load_credentials(config_file)
        set_environment_variables(credentials)
    else:
        jira_url, username, api_token = get_user_credentials()
        save_config = input(
            "Do you want to save these credentials for future use? (y/n): "
        )
        if save_config.lower() == "y":
            save_credentials_to_config(config_file, jira_url, username, api_token)
        set_environment_variables(
            {"jira_url": jira_url, "user": username, "api_token": api_token}
        )


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)




def read_config(filename):
    """
    Read configuration from a JSON file.

    Args:
        filename (str): Path to the configuration file.

    Returns:
        dict: A dictionary containing the configuration.
    """
    with open(filename, "r") as f:
        config = json.load(f)
    return config


def get_user_credentials():
    """
    Prompt the user to enter Jira URL, username, and API token.

    Returns:
        tuple: A tuple containing Jira URL, username, and API token.
    """
    jira_url = input("Enter Jira URL: ")
    username = input("Enter username: ")
    api_token = input("Enter API token: ")
    return jira_url, username, api_token


def save_credentials_to_config(config_file, jira_url, username, api_token):
    """
    Saves the provided Jira credentials to a specified configuration file.

    Args:
        config_file (str): The path to the configuration file where credentials will be saved.
        jira_url (str): The Jira URL.
        username (str): The username.
        api_token (str): The API token.
    """
    config_data = {"jira_url": jira_url, "user": username, "api_token": api_token}
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    logging.info(f"Credentials saved to {config_file}")


def create_jira_connection(jira_url, username, api_token):
    """
    Establishes a connection to the Jira server using the provided credentials.

    Args:
        jira_url (str): The URL of the Jira server.
        username (str): The username for Jira authentication.
        api_token (str): The API token for Jira authentication.

    Returns:
        JIRA: An instance of the JIRA client.

    Raises:
        ValueError: If any of the inputs (jira_url, username, api_token) are missing.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not (jira_url and username and api_token):
        logging.error("Missing username, API token, or Jira URL")
        raise ValueError("Missing username, API token, or Jira URL")

    try:
        jira = JIRA(basic_auth=(username, api_token), options={"server": jira_url})
        logging.info("Jira connection established successfully.")
        return jira
    except JIRAError as je:
        logging.error(f"JiraError: {je}")
        raise
    except Exception as e:
        logging.error(f"Error creating Jira connection: {e}")
        raise


def create_jira_project(jira, project_name, project_key):
    """
    Creates a new project in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_name (str): The name of the new project.
        project_key (str): The key for the new project.

    Returns:
        dict or None: The newly created project if successful, None if there was an error.

    Raises:
        ValueError: If jira, project_name, or project_key are not provided.
        JIRAError: If there is an error specific to the Jira API.
    """
    if not (jira and project_name and project_key):
        logging.error(
            "Failed to create project: Jira connection, project name, or project key not provided."
        )
        raise ValueError(
            "Jira connection, project name, and project key must be provided."
        )

    try:
        project = jira.create_project(project_key, project_name)
        logging.info(
            f"Project '{project_name}' created successfully with key '{project_key}'."
        )
        return project
    except JIRAError as e:
        logging.error(f"Error creating project: {e}")
        raise


def update_jira_project(jira, project_key, new_name=None, new_key=None):
    """
    Updates the name or key of an existing project in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_key (str): The key of the project to update.
        new_name (str, optional): The new name for the project.
        new_key (str, optional): The new key for the project.

    Returns:
        bool: True if the update was successful, False otherwise.

    Raises:
        ValueError: If jira or project_key are not provided, or if neither new_name nor new_key are provided.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not jira:
        logging.error("Failed to update project: Jira connection not established.")
        raise ValueError("Jira connection must be provided.")

    if not project_key:
        logging.error("Failed to update project: Project key not provided.")
        raise ValueError("Project key must be provided.")

    if not new_name and not new_key:
        logging.error("Failed to update project: No new name or key provided.")
        raise ValueError("Either new_name or new_key must be provided.")

    try:
        project = jira.project(project_key)
        if not project:
            logging.error(f"Project with key '{project_key}' does not exist.")
            return False
    except JIRAError as e:
        logging.error(f"Error retrieving project: {e}")
        return False

    try:
        if new_name:
            project.update(name=new_name)
            logging.info(f"Project name updated to '{new_name}' successfully.")
        if new_key:
            project.update(key=new_key)
            logging.info(f"Project key updated to '{new_key}' successfully.")
        return True
    except JIRAError as e:
        logging.error(f"Error updating project: {e}")
        raise
    except Exception as e:
        logging.error(f"Error updating project: {e}")
        raise


def list_projects(jira):
    """
    Lists all projects in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.

    Returns:
        list: A list of projects if successful, an empty list if there was an error.

    Raises:
        ValueError: If jira connection is not provided.
        JIRAError: If there is an error specific to the Jira API.
    """
    if not jira:
        logging.error("Failed to list projects: Jira connection not established.")
        raise ValueError("Jira connection must be provided.")

    try:
        projects = jira.projects()
        for project in projects:
            logging.info(f"Project Key: {project.key}, Name: {project.name}")
        return projects
    except JIRAError as e:
        logging.error(f"Error listing projects: {e}")
        return []
    
    

def delete_project(jira, project_key, auto_confirm=False):
    """
    Deletes a specific project in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_key (str): The key of the project to delete.
        auto_confirm (bool): If True, skips the confirmation prompt and deletes the project directly.

    Returns:
        bool: True if the project was deleted successfully, False otherwise.

    Raises:
        ValueError: If jira connection or project_key is not provided.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not jira:
        logging.error("Failed to delete project: Jira connection not established.")
        raise ValueError("Jira connection must be provided.")

    if not project_key:
        logging.error("Failed to delete project: Project key not provided.")
        raise ValueError("Project key must be provided.")

    if not auto_confirm:
        confirmation = (
            input(f"Do you really want to delete project {project_key}? [y/n]: ")
            .strip()
            .lower()
        )
        if confirmation != "y":
            logging.info(f"Project {project_key} deletion cancelled by user.")
            return False

    try:
        # Delete project
        jira.delete_project(project_key)
        logging.info(f"Project {project_key} deleted successfully.")
        return True
    except JIRAError as e:
        error_message = f"Error deleting project {project_key}: {e.response.text}"
        logging.error(error_message)
        raise JIRAError(error_message) from e
    except Exception as e:
        error_message = f"Unexpected error deleting project {project_key}: {e}"
        logging.error(error_message)
        raise Exception(error_message) from e

def list_stories_for_project(jira, project_key):
    """
    Lists all stories, tasks, and bugs for a specific project in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_key (str): The key of the project to list stories for.

    Returns:
        list: A list of dictionaries containing issue details, or None if an error occurs.

    Raises:
        ValueError: If jira connection or project_key is not provided.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not jira:
        logging.error("Failed to list stories: Jira connection not established.")
        raise ValueError("Jira connection must be provided.")

    if not project_key:
        logging.error("Failed to list stories: Project key not provided.")
        raise ValueError("Project key must be provided.")

    try:
        jql_query = f"project = {project_key} AND issuetype in (Bug, Task, Story)"
        issues = jira.search_issues(jql_query)
        stories = [
            {
                "Issue Type": issue.fields.issuetype.name,
                "Issue Key": issue.key,
                "Status": issue.fields.status.name,
                "Assignee": (
                    issue.fields.assignee.displayName if issue.fields.assignee else None
                ),
                "Summary": issue.fields.summary,
            }
            for issue in issues
        ]
        return stories
    except JIRAError as e:
        logging.error(f"Error retrieving stories for project: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error retrieving stories for project: {e}")
        raise


def create_story(jira, project_key, summary, description):
    """
    Creates a new story in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_key (str): The key of the project where the story will be created.
        summary (str): The summary of the story.
        description (str): The description of the story.

    Returns:
        Issue: The created Jira issue if successful, None otherwise.

    Raises:
        ValueError: If jira connection, project_key, summary, or description is not provided.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not jira:
        logging.error("Failed to create story: Jira connection not established.")
        raise ValueError("Jira connection must be provided.")

    if not project_key:
        logging.error("Failed to create story: Project key not provided.")
        raise ValueError("Project key must be provided.")

    if not summary:
        logging.error("Failed to create story: Summary not provided.")
        raise ValueError("Summary must be provided.")

    if not description:
        logging.error("Failed to create story: Description not provided.")
        raise ValueError("Description must be provided.")

    try:
        new_story = jira.create_issue(
            project=project_key,
            summary=summary,
            description=description,
            issuetype={"name": "Task"},
        )
        logging.info(f"Story created successfully. Story Key: {new_story.key}")
        return new_story
    except JIRAError as e:
        logging.error(f"Error creating story: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error creating story: {e}")
        raise


def update_story_status(jira, issue_key, new_status, print_info=True):
    """
    Updates the status of a specific story in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the story to update.
        new_status (str): The new status to set for the story.
        print_info (bool): Whether to print info on successful update.

    Returns:
        bool: True if the status was updated successfully, False otherwise.

    Raises:
        ValueError: If jira connection or issue_key/new_status is not provided.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not jira:
        logging.error("Failed to update story status: Jira connection not established.")
        raise ValueError("Jira connection must be provided.")

    if not issue_key:
        logging.error("Failed to update story status: Story key not provided.")
        raise ValueError("Story key must be provided.")

    if not new_status:
        logging.error("Failed to update story status: New status not provided.")
        raise ValueError("New status must be provided.")

    try:
        issue = jira.issue(issue_key)
        transitions = jira.transitions(issue)
        for transition in transitions:
            if transition["to"]["name"] == new_status:
                jira.transition_issue(issue, transition["id"])
                if print_info:
                    logging.info(f"Story status updated successfully. Key: {issue_key}")
                return True
        logging.error(f"Invalid status: {new_status}")
        return False
    except JIRAError as e:
        logging.error(f"Error updating story status: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error updating story status: {e}")
        raise


def update_story_summary(jira, issue_key, new_summary):
    """
    Updates the summary of a specific story in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the story to update.
        new_summary (str): The new summary to set for the story.

    Returns:
        Issue: The updated Jira issue if successful, None otherwise.

    Raises:
        ValueError: If jira connection or issue_key/new_summary is not provided.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not jira:
        logging.error(
            "Failed to update story summary: Jira connection not established."
        )
        raise ValueError("Jira connection must be provided.")

    if not issue_key:
        logging.error("Failed to update story summary: Story key not provided.")
        raise ValueError("Story key must be provided.")

    if not new_summary:
        logging.error("Failed to update story summary: New summary not provided.")
        raise ValueError("New summary must be provided.")

    try:
        story = jira.issue(issue_key)
        story.update(summary=new_summary)
        logging.info(f"Story summary updated successfully. Key: {issue_key}")
        return story
    except JIRAError as e:
        logging.error(f"Error updating story summary: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error updating story summary: {e}")
        raise


def update_story_description(jira, issue_key, new_description):
    """
    Updates the description of a specific story in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the story to update.
        new_description (str): The new description to set for the story.

    Returns:
        Issue: The updated Jira issue if successful, None otherwise.

    Raises:
        ValueError: If jira connection or issue_key/new_description is not provided.
        JIRAError: If there is an error specific to the Jira API.
        Exception: For any other exceptions that may occur.
    """
    if not jira:
        logging.error(
            "Failed to update story description: Jira connection not established."
        )
        raise ValueError("Jira connection must be provided.")

    if not issue_key:
        logging.error("Failed to update story description: Story key not provided.")
        raise ValueError("Story key must be provided.")

    if not new_description:
        logging.error(
            "Failed to update story description: New description not provided."
        )
        raise ValueError("New description must be provided.")

    try:
        story = jira.issue(issue_key)
        story.update(description=new_description)
        logging.info(f"Story description updated successfully. Key: {issue_key}")
        return story
    except JIRAError as e:
        logging.error(f"Error updating story description: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error updating story description: {e}")
        raise


def update_story_assignee(jira, issue_key, username):
    """
    Updates the assignee of a specific Jira story.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the story to update.
        username (str): The username of the new assignee.

    Returns:
        bool: True if the assignee was updated successfully, False otherwise.

    Raises:
        ValueError: If jira connection, issue_key, or username is not provided.
        JIRAError: If there is an error specific to the Jira API.
        requests.exceptions.RequestException: If there is an error with the HTTP request.
    """
    if not jira:
        logging.error("Failed to update assignee: Jira connection not established.")
        raise ValueError("Jira connection must be provided.")

    if not issue_key:
        logging.error("Failed to update assignee: Story key not provided.")
        raise ValueError("Story key must be provided.")

    if not username:
        logging.error("Failed to update assignee: Username not provided.")
        raise ValueError("Username must be provided.")

    # Check if user exists
    user_account_id = get_user_account_id(jira, username)
    if not user_account_id:
        logging.error(f"Failed to fetch account ID for username: {username}")
        return False

    try:
        # Check if story exists
        story = jira.issue(issue_key)
    except JIRAError as e:
        logging.error(f"Error fetching story: {e}")
        return False

    url = f"https://jirasimplelib.atlassian.net/rest/api/2/issue/{issue_key}/assignee"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = json.dumps({"accountId": user_account_id})

    try:
        response = requests.put(
            url, data=payload, headers=headers, auth=jira._session.auth
        )
        if response.status_code == 204:
            logging.info(f"Issue {issue_key} assigned successfully to {username}.")
            return True
        else:
            logging.error(
                f"Failed to assign issue {issue_key}. Status Code: {response.status_code}"
            )
            logging.error(
                f"Response: {json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(',', ': '))}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while trying to assign the issue: {e}")
        raise


def get_assignee(jira, issue_key):
    """
    View the assignee of a specific Jira issue.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the issue to view.

    Returns:
        None
    """
    try:
        issue = jira.issue(issue_key)
        assignee = issue.fields.assignee

        if assignee is not None:
            logging.info(
                f"The assignee of issue {issue_key} is: {assignee.displayName}"
            )
        else:
            logging.info(f"Issue {issue_key} is currently unassigned.")
    except JIRAError as e:
        logging.error(f"Error viewing assignee: {e}")

def delete_story(jira, issue_key, auto_confirm=True):
    """
    Delete a specific Jira story.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the story to delete.
        auto_confirm (bool): If True, skips the confirmation prompt and deletes the story directly.

    Returns:
        bool: True if the story was deleted successfully, False otherwise.
    """
    try:
        issue = jira.issue(issue_key)
        if issue:
            if not auto_confirm:
                confirmation = (
                    input(f"Do you really want to delete the story with key {issue_key}? [y/n]: ")
                    .strip()
                    .lower()
                )
                if confirmation != "y":
                    logging.info(f"Story deletion cancelled by user. Key: {issue_key}")
                    return False

            issue.delete()
            logging.info(f"Story deleted successfully. Key: {issue_key}")
            return True
        else:
            logging.error(f"Story with key {issue_key} does not exist.")
            return False
    except JIRAError as e:
        if e.status_code == 403:
            logging.error(f"Permission denied: You do not have permission to delete the story with key {issue_key}. Response text: {e.text}")
        else:
            logging.error(f"Error deleting story: {e}. Response text: {e.text}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False


def add_comment(jira, issue_key, comment_body):
    """
    Add a comment to a specific Jira issue.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the issue to add the comment to.
        comment_body (str): The body of the comment to add.

    Returns:
        int: 1 if the comment was added successfully, 0 otherwise.
    """
    try:
        issue = jira.issue(issue_key)
        if issue:
            jira.add_comment(issue, comment_body)
            logging.info(f"Comment added to issue {issue_key}")
            return 1
        else:
            logging.error(f"Issue with key {issue_key} does not exist.")
            return 0
    except JIRAError as e:
        logging.error(f"Error adding comment to issue {issue_key}: {e}")
        return 0


def get_story_details(jira, issue_key):
    """
    Read the details of a specific Jira story.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the story to read.

    Returns:
        None
    """
    try:
        story = jira.issue(issue_key)
        if story:
            logging.info(f"Key: {story.key}")
            logging.info(f"Summary: {story.fields.summary}")
            logging.info(f"Description: {story.fields.description}")
            logging.info(f"Status: {story.fields.status.name}")
            if story.fields.assignee:
                logging.info(f"Assignee: {story.fields.assignee.displayName}")
            else:
                logging.info("Assignee: Unassigned")
            if story.fields.reporter:
                logging.info(f"Reporter: {story.fields.reporter.displayName}")
            else:
                logging.info("Reporter: Unassigned")
            logging.info(f"Created: {story.fields.created}")
            logging.info(f"Updated: {story.fields.updated}")
        else:
            logging.error(f"Story with key {issue_key} does not exist.")
    except JIRAError as e:
        logging.error(f"Error reading story details: {e}")


def create_epic(jira, project_key, epic_name, epic_summary):
    """
    Create a new Epic in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_key (str): The key of the project to create the Epic in.
        epic_name (str): The name of the Epic.
        epic_summary (str): The summary of the Epic.

    Returns:
        new_epic (Issue): The newly created Epic issue, or None if creation fails.
    """
    try:
        new_epic = jira.create_issue(
            project=project_key,
            summary=epic_summary,
            issuetype={"name": "Epic"},
            # customfield_10000=epic_name  # Replace with the appropriate custom field ID for Epic name
        )
        logging.info(f"Epic created successfully. Epic Key: {new_epic.key}")
        return new_epic
    except JIRAError as e:
        logging.error(f"Error creating epic: {e}")
        return None


def list_epics(jira, project_key):
    """
    List all Epics in a project.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_key (str): The key of the project to list Epics from.

    Returns:
        epics (list): A list of all Epics in the project, or None if listing fails.
    """
    try:
        jql_query = f"project = {project_key} AND issuetype = Epic"
        epics = jira.search_issues(jql_query)
        return epics
    except Exception as e:
        logging.error(f"Error listing epics: {e}")
        return None


def update_epic(jira, epic_key, new_summary, new_description):
    """
    Update the details of an Epic in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        epic_key (str): The key of the Epic to update.
        new_summary (str): The new summary for the Epic.
        new_description (str): The new description for the Epic.

    Returns:
        epic (Issue): The updated Epic issue, or None if update fails.
    """
    try:
        epic = jira.issue(epic_key)
        epic.update(
            summary=new_summary,
            description=new_description,
        )
        logging.info(f"Epic updated successfully. Key: {epic_key}")
        return epic
    except JIRAError as e:
        logging.error(f"Error updating epic: {e}")
        return None


def get_epic_details(jira, epic_key):
    """
    Read the details of an Epic in Jira, including associated stories.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        epic_key (str): The key of the Epic to read.

    Returns:
        None
    """
    try:
        epic = jira.issue(epic_key)
        logging.info(f"Epic Key: {epic.key}")
        logging.info(f"Summary: {epic.fields.summary}")

        # Read stories in the epic
        stories = jira.search_issues(f"'Epic Link' = {epic_key}")
        if stories:
            logging.info("Stories in the Epic:")
            for story in stories:
                logging.info(f"Story Key: {story.key}")
                logging.info(f"Summary: {story.fields.summary}")
                logging.info(f"Status: {story.fields.status}")
                logging.info(f"Assignee: {story.fields.assignee}")
                logging.info(f"Due Date: {story.fields.duedate}")
                logging.info(
                    f"Start Date: {story.fields.customfield_10015}"
                )  # Replace 'xxxxx' with the custom field ID for start date
        else:
            logging.info("No stories found in the Epic.")

    except JIRAError as e:
        logging.error(f"Error reading epic: {e}")


def add_issues_to_epic(jira, epic_key, issue_keys):
    """
    Add one or multiple issues to an Epic in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        epic_key (str): The key of the Epic to add the issues to.
        issue_keys (str or list): The key or list of keys of the issues to add to the Epic.

    Returns:
        bool: True if the issues were added to the Epic successfully, False otherwise.
    """
    try:
        # Check if the epic exists
        epic = jira.issue(epic_key)
        if not epic:
            logging.error(f"Epic with key {epic_key} does not exist.")
            return False

        # Check if the issue keys exist
        if isinstance(issue_keys, str):
            issue_keys = [issue_keys]
        for issue_key in issue_keys:
            issue = jira.issue(issue_key)
            if not issue:
                logging.error(f"Issue with key {issue_key} does not exist.")
                return False

        # Add issues to the epic
        for issue_key in issue_keys:
            issue = jira.issue(issue_key)
            jira.add_issues_to_epic(epic.id, [issue.id])
            logging.info(f"Issue {issue_key} added to Epic {epic_key}")
        return True
    except JIRAError as e:
        logging.error(f"Error adding issues to epic: {e}")
        return False


def unlink_story_from_epic(jira, issue_key):
    """
    Unlink a Story from an Epic in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        issue_key (str): The key of the story to unlink from its Epic.

    Returns:
        bool: True if the story was successfully unlinked from its Epic, False otherwise.
    """
    try:
        story = jira.issue(issue_key)

        # Update the 'Epic Link' custom field of the story to remove its association with the epic
        story.update(
            fields={"customfield_10014": None}
        )  # Replace 'customfield_123456' with the actual Epic Link field ID

        logging.info(f"Story {issue_key} unlinked from its Epic")
        return True
    except JIRAError as e:
        logging.error(f"Error unlinking story from epic: {e}")
        return False


def delete_epic(jira, epic_key, auto_confirm=False):
    """
    Delete an Epic in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        epic_key (str): The key of the Epic to delete.
        auto_confirm (bool): If True, skips the confirmation prompt and deletes the Epic directly.

    Returns:
        bool: True if the Epic was deleted successfully, False otherwise.
    """
    try:
        issue = jira.issue(epic_key)
        if issue:
            if not auto_confirm:
                confirmation = (
                    input(
                        f"Do you really want to delete the epic with key {epic_key}? [y/n]: "
                    )
                    .strip()
                    .lower()
                )
                if confirmation != "y":
                    logging.info(f"Epic deletion cancelled by user. Key: {epic_key}")
                    return False

            issue.delete()
            logging.info(f"Epic deleted successfully. Key: {epic_key}")
            return True
        else:
            logging.error(f"Epic with key {epic_key} does not exist.")
            return False
    except JIRAError as e:
        logging.error(f"Error deleting epic: {e}")
        return False


def create_sprint(jira, board_id, sprint_name):
    """
    Create a Sprint in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        board_id (int): The ID of the board associated with the Sprint.
        sprint_name (str): The name of the Sprint to create.

    Returns:
        sprint_id (int): The ID of the newly created Sprint, or None if creation fails.
    """
    create_sprint_api_url = f"{jira._options['server']}/rest/agile/1.0/sprint"
    sprint_data = {
        "name": sprint_name,
        "originBoardId": board_id,
    }
    response_create_sprint = requests.post(
        create_sprint_api_url, json=sprint_data, auth=jira._session.auth
    )
    if response_create_sprint.status_code == 201:
        created_sprint_data = response_create_sprint.json()
        sprint_id = created_sprint_data.get("id")
        logging.info(f"New Sprint created with ID: {sprint_id}")
        return sprint_id
    else:
        logging.error(
            f"Failed to create a new Sprint. Status code: {response_create_sprint.status_code}, Error: {response_create_sprint.text}"
        )
        return None


def list_sprints(jira, board_id):
    """
    List all sprints associated with a board in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        board_id (int): The ID of the board.

    Returns:
        list: List of sprint objects associated with the board, or None if an error occurs.
    """
    try:
        sprints = jira.sprints(board_id)
        return sprints
    except Exception as e:
        logging.error(f"Error retrieving sprints for board: {e}")
        return None


def start_sprint(jira, sprint_id, new_summary, start_date, end_date):
    """
    Start a Sprint in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        sprint_id (int): The ID of the Sprint to start.
        new_summary (str): The new summary for the Sprint.
        start_date (str): The start date of the Sprint (format: 'YYYY-MM-DD').
        end_date (str): The end date of the Sprint (format: 'YYYY-MM-DD').

    Returns:
        sprint: The updated Sprint object if started successfully, None otherwise.
    """
    try:
        sprint = jira.sprint(sprint_id)
        if sprint.state == "CLOSED":
            logging.warning(
                f"Sprint {sprint_id} is already closed. You cannot restart it."
            )
            return "Sprint is closed"
        elif sprint.state == "ACTIVE":
            logging.warning(f"Sprint {sprint_id} is already active. No action taken.")
            return sprint
        else:
            sprint.update(
                name=new_summary, state="active", startDate=start_date, endDate=end_date
            )
            logging.info(f"Sprint {sprint_id} started successfully.")
            return sprint
    except JIRAError as e:
        logging.error(f"Error starting sprint {sprint_id}: {e}")
        return None


def list_stories_in_sprint(jira, sprint_id, print_info=False):
    """
    List all stories in a sprint in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        sprint_id (int): The ID of the sprint.
        print_info (bool, optional): Whether to print retrieved story keys. Defaults to False.

    Returns:
        list: List of story keys in the sprint, or None if an error occurs.
    """
    try:
        # Construct JQL to search for issues in the given sprint
        jql = f"sprint = {sprint_id} AND issuetype = Task"

        # Search for issues using the constructed JQL
        issues = jira.search_issues(jql)

        # Extract issue keys from the search result
        issue_keys = [issue.key for issue in issues]

        if print_info:
            logging.info(f"Retrieved {len(issue_keys)} stories in sprint {sprint_id}")
            for key in issue_keys:
                logging.info(f"Story Key: {key}")

        return issue_keys
    except JIRAError as e:
        logging.error(f"Error retrieving stories in sprint: {e}")
        return None


def complete_stories_in_sprint(jira, sprint_id, print_info=False):
    """
    Mark all stories in a sprint as completed in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        sprint_id (int): The ID of the sprint.
        print_info (bool, optional): Whether to print completion info. Defaults to False.

    Returns:
        bool: True if all stories are marked completed, False otherwise.
    """
    try:
        # Get the list of stories in the sprint
        issue_keys = list_stories_in_sprint(jira, sprint_id, print_info)

        if not issue_keys:
            logging.error("No stories found in the sprint.")
            return False

        # Iterate through each story and update its status to "Done"
        for issue_key in issue_keys:
            update_story_status(jira, issue_key, "Done", print_info)
            logging.info(f"All stories in sprint {sprint_id} marked as completed.")
            return True
    except Exception as e:
        logging.error(f"Error completing stories in sprint: {e}")
        return False


def complete_sprint(jira, sprint_id, start_date, end_date):
    """
    Complete a sprint in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        sprint_id (int): The ID of the sprint to complete.
        start_date (str): The start date of the sprint (format: 'YYYY-MM-DD').
        end_date (str): The end date of the sprint (format: 'YYYY-MM-DD').

    Returns:
        bool: True if the sprint is completed successfully, False otherwise.
    """
    try:
        sprint = jira.sprint(sprint_id)
        sprint_name = sprint.name
        sprint.update(
            name=sprint_name, state="closed", startDate=start_date, endDate=end_date
        )
        logging.info(f"Sprint '{sprint_name}' ({sprint_id}) has been completed.")
        return True
    except JIRAError as e:
        logging.error(f"Error completing sprint: {e}")
        return False


def update_sprint_summary(jira, sprint_id, new_summary):
    """
    Update the summary of a sprint in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        sprint_id (int): The ID of the sprint to update.
        new_summary (str): The new summary for the sprint.

    Returns:
        bool: True if the sprint summary is updated successfully, False otherwise.
    """
    try:
        current_sprint = jira.sprint(sprint_id)
        current_state = current_sprint.state
        jira.update_sprint(sprint_id, name=new_summary, state=current_state)
        logging.info(f"Sprint summary updated successfully. ID: {sprint_id}")
        return True
    except JIRAError as e:
        logging.error(f"Error updating sprint summary: {e}")
        return False



def get_sprint_details(jira, sprint_id, project_key):
    """
    Generate a report for a sprint in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        sprint_id (int): The ID of the sprint to generate the report for.
        project_key (str): The key of the project associated with the sprint.

    Returns:
        None
    """
    try:
        # Get detailed information about the sprint
        sprint_info = jira.sprint(sprint_id)
        if not sprint_info:
            logging.info(f"Sprint with ID {sprint_id} not found.")
            return

        # Print all details of the sprint
        logging.info("Sprint Details:")
        for key, value in sprint_info.raw.items():
            logging.info(f"{key}: {value}")

        # Define the JQL query to search for issues of type 'Story' in the sprint
        jql_query = (
            f"project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}"
        )

        # Search for issues using the JQL query
        issues = jira.search_issues(jql_query)

        # Count issue statuses
        status_counts = {"To Do": 0, "In Progress": 0, "Done": 0}
        for issue in issues:
            status = issue.fields.status.name
            if status in status_counts:
                status_counts[status] += 1

        # Print issue status distribution
        logging.info("Issue Status Distribution in Sprint:")
        for status, count in status_counts.items():
            logging.info(f"{status}: {count}")

    except JIRAError as e:
        logging.error(f"Error generating sprint report: {e}")


def delete_sprint(jira, sprint_id, auto_confirm=False):
    """
    Delete a sprint in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        sprint_id (int): The ID of the sprint to delete.
        auto_confirm (bool): If True, skips the confirmation prompt and deletes the sprint directly.

    Returns:
        bool: True if the sprint is deleted successfully, False otherwise.
    """
    try:
        sprint = jira.sprint(sprint_id)
        if sprint:
            if not auto_confirm:
                confirmation = (
                    input(
                        f"Do you really want to delete the sprint with ID {sprint_id}? [y/n]: "
                    )
                    .strip()
                    .lower()
                )
                if confirmation != "y":
                    logging.info(f"Sprint deletion cancelled by user. ID: {sprint_id}")
                    return False

            sprint.delete()
            logging.info(f"Sprint with ID {sprint_id} deleted successfully.")
            return True
        else:
            logging.error(f"Sprint with ID {sprint_id} does not exist.")
            return False
    except JIRAError as e:
        logging.error(f"Error deleting sprint: {e}")
        return False


def delete_all_sprints(jira, board_id, auto_confirm=False):
    """
    Delete all sprints associated with a board in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        board_id (int): The ID of the board containing the sprints to be deleted.
        auto_confirm (bool): If True, skips the confirmation prompt and deletes the sprints directly.

    Returns:
        bool: True if all sprints are deleted successfully, False otherwise.
    """
    try:
        # Retrieve all sprints in the board
        sprints = jira.sprints(board_id)

        if not auto_confirm:
            confirmation = (
                input(
                    f"Do you really want to delete all sprints for board ID {board_id}? [y/n]: "
                )
                .strip()
                .lower()
            )
            if confirmation != "y":
                logging.info(
                    f"Deletion of all sprints cancelled by user. Board ID: {board_id}"
                )
                return False

        # Delete each sprint
        for sprint in sprints:
            sprint.delete()
            logging.info(f"Sprint deleted successfully. ID: {sprint.id}")

        logging.info("All sprints have been deleted.")
        return True
    except JIRAError as e:
        logging.error(f"Error deleting sprints: {e}")
        return False


def get_board_id(jira, board_name):
    """
    Get the ID of a board by its name in Jira.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        board_name (str): The name of the board to retrieve the ID for.

    Returns:
        int or None: The ID of the board if found, None otherwise.
    """
    try:
        # Make a GET request to retrieve the list of boards
        response = jira._session.get(f'{jira._options["server"]}/rest/agile/1.0/board')
        if response.status_code == 200:
            boards = response.json()["values"]
            for board in boards:
                if board["name"] == board_name:
                    return board["id"]
            logging.info(f"Board '{board_name}' not found.")
            return None
        else:
            logging.error(
                f"Failed to retrieve boards. Status code: {response.status_code}"
            )
            return None
    except Exception as e:
        logging.error(f"Error retrieving board ID: {e}")
        return None

def my_stories(jira, project_key, user):
    """
    Retrieve and print stories assigned to a specific user in a project.

    Args:
        jira (JIRA): An authenticated JIRA client instance.
        project_key (str): The key of the project containing the stories.
        user (str): The username of the user to retrieve stories for.

    Returns:
        None
    """
    try:
        # Construct JQL query to search for issues assigned to the user in the project with specific statuses
        jql_query = (
            f"project = {project_key} AND assignee = '{user}' "
            f"AND issuetype = Task AND status IN ('To Do', 'In Progress', 'In Review')"
        )

        # Search for issues using the constructed JQL query
        issues = jira.search_issues(jql_query)

        # Print issue key, summary, and status from the search result
        for issue in issues:
            print(f"Key: {issue.key}, Summary: {issue.fields.summary}, Status: {issue.fields.status.name}")

    except JIRAError as e:
        logging.error(f"Error retrieving stories for user: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")



def render_tui(issues, fetching_data=False):
    """
    Render a text-based user interface (TUI) for displaying Jira issues.

    Args:
        issues (list): List of dictionaries representing Jira issues.
        fetching_data (bool, optional): Flag indicating whether data is being fetched. Defaults to False.
    """
    term = blessed.Terminal()
    headers = ["Issue Type", "Issue Key", "Status", "Assignee", "Summary"]

    # Initialize max_lengths list with lengths of header names
    max_lengths = [len(header) for header in headers]

    # Update max_lengths with the lengths of the longest entries in each column for each row
    for issue in issues:
        for i, header in enumerate(headers):
            entry_length = len(str(issue.get(header, "")))
            max_lengths[i] = max(max_lengths[i], entry_length)

    # Adjust the length of the "Summary" header based on the longest entry in the "Summary" column
    max_summary_length = max(len(str(issue.get("Summary", ""))) for issue in issues)
    max_lengths[headers.index("Summary")] = max(
        max_lengths[headers.index("Summary")], max_summary_length
    )

    def print_row(row):
        formatted_row = []
        for i, field in enumerate(row):
            if field is None:
                formatted_row.append(" " * max_lengths[i])
            else:
                formatted_row.append(f"{field:<{max_lengths[i]}}")  # No color for rows
        print(f"| {' | '.join(formatted_row)} |")

    def print_boundary():
        boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
        logging.info(term.green(boundary))  # Green boundary

    try:
        # Print header with green background and bold text
        print_boundary()
        print_row([header for header in headers])  # Green background and bold text
        print_boundary()

        # Print rows with alternating colors
        for i, issue in enumerate(issues):
            row = [
                issue.get("Issue Type", ""),  # Green text for issue type
                issue.get("Issue Key", ""),  # Dark pink text for issue key
                issue.get("Status", ""),  # Blue text for status
                issue.get("Assignee", ""),  # Cyan text for assignee
                issue.get("Summary", ""),
            ]
            print_row(row)  # Reverse colors for alternating rows
            print_boundary()
    except blessed.BlessedError as be:
        logging.error(f"Blessed library error: {be}")
    except Exception as e:
        logging.error(f"An error occurred while rendering TUI: {e}")


def get_story_details_tui(jira, issue_key):
    """
    Render a text-based user interface (TUI) to display details of a Jira story.

    Args:
        jira: JIRA connection object.
        issue_key (str): Key of the Jira story to display details for.
    """
    try:
        term = blessed.Terminal()
        story = jira.issue(issue_key)

        headers = ["Field", "Value"]

        data = [
            ("Key", story.key),
            ("Summary", story.fields.summary),
            ("Description", story.fields.description),
            ("Status", story.fields.status.name),
            (
                "Assignee",
                (
                    story.fields.assignee.displayName
                    if story.fields.assignee
                    else "Unassigned"
                ),
            ),
            (
                "Reporter",
                (
                    story.fields.reporter.displayName
                    if story.fields.reporter
                    else "Unassigned"
                ),
            ),
            ("Created", story.fields.created),
            ("Updated", story.fields.updated),
        ]

        # Calculate maximum lengths for columns
        max_lengths = [len(header) for header in headers]
        for row in data:
            for i, value in enumerate(row):
                max_lengths[i] = max(max_lengths[i], len(str(value)))

        def print_row(row):
            """Print a formatted row."""
            formatted_row = [
                f"{field:<{max_lengths[i]}}" for i, field in enumerate(row)
            ]
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            """Print a boundary line."""
            boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
            print(term.green(boundary))

        # Print header
        print(term.bold("Story Details:"))
        print_boundary()
        print_row(headers)
        print_boundary()

        # Print data rows
        for row in data:
            print_row(row)
            print_boundary()

    except JIRAError as e:
        logging.error(f"Error reading story: {e}")


def list_epics_tui(jira, project_key):
    """
    Render a text-based user interface (TUI) to display a list of epics in a project.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project to list epics for.
    """
    try:
        term = blessed.Terminal()
        jql_query = f"project = {project_key} AND issuetype = Epic"
        epics = jira.search_issues(jql_query)

        headers = ["Epic Key", "Summary"]

        data = [(epic.key, epic.fields.summary) for epic in epics]

        max_lengths = [len(header) for header in headers]
        for row in data:
            for i, value in enumerate(row):
                max_lengths[i] = max(max_lengths[i], len(str(value)))

        def print_row(row):
            """Print a formatted row."""
            formatted_row = [
                f"{field:<{max_lengths[i]}}" for i, field in enumerate(row)
            ]
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            """Print a boundary line."""
            boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
            print(term.green(boundary))

        # Print header
        print(term.bold("List of Epics:"))
        print_boundary()
        print_row(headers)
        print_boundary()

        # Print data rows
        for row in data:
            print_row(row)
            print_boundary()
    except JIRAError as e:
        logging.error(f"Error listing epics: {e}")
    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")


def list_projects_tui(jira):
    """
    Render a text-based user interface (TUI) to display a list of projects.

    Args:
        jira: JIRA connection object.
    """
    try:
        term = blessed.Terminal()
        projects = jira.projects()

        # Define headers for the table
        headers = ["Project Key", "Project Name"]

        # Get project data
        data = [(project.key, project.name) for project in projects]

        # Calculate maximum lengths for formatting
        max_lengths = [len(header) for header in headers]
        for row in data:
            for i, value in enumerate(row):
                max_lengths[i] = max(max_lengths[i], len(str(value)))

        # Function to print a row in the table
        def print_row(row):
            """Print a formatted row."""
            formatted_row = [
                f"{value:<{max_lengths[i]}}" for i, value in enumerate(row)
            ]
            print(f"| {' | '.join(formatted_row)} |")

        # Function to print the boundary of the table
        def print_boundary():
            """Print a boundary line."""
            boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
            print(term.green(boundary))

        # Print table header
        print(term.bold("List of Projects:"))
        print_boundary()
        print_row(headers)
        print_boundary()

        # Print project data
        for row in data:
            print_row(row)
            print_boundary()

        return projects
    except JIRAError as e:
        logging.error(f"Error listing projects: {e}")
        return None


def get_epic_details_tui(jira, epic_key):
    """
    Render a text-based user interface (TUI) to display details of an epic and stories linked with it.

    Args:
        jira: JIRA connection object.
        epic_key (str): Key of the epic to retrieve details for.
    """
    try:
        term = blessed.Terminal()
        epic = jira.issue(epic_key)

        epic_headers = ["Field", "Value"]
        story_headers = ["Issue Type", "Issue Key", "Status", "Assignee", "Summary"]

        epic_data = [("Epic Key", epic.key), ("Summary", epic.fields.summary)]

        stories = jira.search_issues(f"'Epic Link' = {epic_key}")
        story_data = []
        if stories:
            for story in stories:
                story_data.append(
                    (
                        story.fields.issuetype.name,
                        story.key,
                        story.fields.status.name,
                        (
                            story.fields.assignee.displayName
                            if story.fields.assignee
                            else "Unassigned"
                        ),
                        story.fields.summary,
                    )
                )
        else:
            story_data.append(("No stories found in the Epic.", "", "", "", ""))

        epic_max_lengths = [len(header) for header in epic_headers]
        story_max_lengths = [len(header) for header in story_headers]

        for row in epic_data:
            for i, value in enumerate(row):
                epic_max_lengths[i] = max(epic_max_lengths[i], len(str(value)))

        for row in story_data:
            for i, value in enumerate(row):
                story_max_lengths[i] = max(story_max_lengths[i], len(str(value)))

        def print_table(data, headers, max_lengths, table_title):
            """Print a table."""
            print(term.bold(table_title))
            print(
                term.green(
                    "+" + "+".join(["-" * (length + 2) for length in max_lengths]) + "+"
                )
            )
            print(
                term.green(
                    f"| {' | '.join([header.center(max_lengths[i] + 2) for i, header in enumerate(headers)])} |"
                )
            )
            print(
                term.green(
                    "+" + "+".join(["-" * (length + 2) for length in max_lengths]) + "+"
                )
            )
            for row in data:
                print(
                    f"| {' | '.join([str(value).ljust(max_lengths[i]) for i, value in enumerate(row)])} |"
                )

                print(
                    "+" + "+".join(["-" * (length + 2) for length in max_lengths]) + "+"
                )

        print_table(epic_data, epic_headers, epic_max_lengths, "Epic Details:")
        print_table(
            story_data, story_headers, story_max_lengths, "Stories Linked with Epic:"
        )

    except JIRAError as e:
        logging.error(f"Error reading epic: {e}")


def list_sprints_for_board_tui(jira, board_id):
    """
    Render a text-based user interface (TUI) to display sprints for a board.

    Args:
        jira: JIRA connection object.
        board_id (str): ID of the board to retrieve sprints for.
    """
    try:
        term = blessed.Terminal()
        sprints = jira.sprints(board_id)

        headers = ["ID", "Name", "State"]

        sprint_data = [(sprint.id, sprint.name, sprint.state) for sprint in sprints]

        max_lengths = [len(header) for header in headers]
        for row in sprint_data:
            for i, value in enumerate(row):
                max_lengths[i] = max(max_lengths[i], len(str(value)))

        def print_row(row):
            formatted_row = []
            for i, field in enumerate(row):
                formatted_row.append(f"{field:<{max_lengths[i]}}")
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
            print(term.green(boundary))

        print(term.bold("Sprints for Board:"))
        print_boundary()
        print_row(headers)
        print_boundary()
        for row in sprint_data:
            print_row(row)
            print_boundary()
    except Exception as e:
        logging.error(f"Error retrieving sprints for board: {e}")


def get_sprint_details_tui(jira, sprint_id, project_key):
    """
    Render a text-based user interface (TUI) to display a sprint report.

    Args:
        jira: JIRA connection object.
        sprint_id (str): ID of the sprint to generate the report for.
        project_key (str): Key of the project associated with the sprint.
    """
    try:
        term = blessed.Terminal()
        sprint_info = jira.sprint(sprint_id)

        if not sprint_info:
            logging.error(f"Sprint with ID {sprint_id} not found.")
            return

        print(term.bold("Sprint Details:"))
        print(f"ID: {sprint_info.id}")
        print(f"Name: {sprint_info.name}")
        print(f"State: {sprint_info.state}")
        print(f"Start Date: {sprint_info.startDate}")
        print(f"End Date: {sprint_info.endDate}")

        jql_query = (
            f"project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}"
        )
        issues = jira.search_issues(jql_query)

        status_counts = {"To Do": 0, "In Progress": 0, "Done": 0}
        for issue in issues:
            status = issue.fields.status.name
            if status in status_counts:
                status_counts[status] += 1

        print(term.bold("\nIssue Status Distribution in Sprint:"))
        for status, count in status_counts.items():
            print(f"{status}: {count}")

    except Exception as e:
        logging.error(f"Error generating sprint report: {e}")


def move_single_issue_to_sprint_tui(jira, issue_key, target_sprint_id):
    """
    Render a text-based user interface (TUI) to move a single issue to a specified sprint.

    Args:
        jira: JIRA connection object.
        issue_key (str): Key of the issue to be moved.
        target_sprint_id (str): ID of the target sprint to move the issue to.
    """
    try:
        term = blessed.Terminal()
        headers = ["Issue Key", "Status", "Info"]

        def print_row(row):
            formatted_row = []
            for i, field in enumerate(row):
                if i == 2:
                    formatted_row.append(f"{field:<20}")
                elif i == 3:
                    formatted_row.append(f"{field:<20}")
                else:
                    formatted_row.append(f"{field:<10}")
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            boundary = "+-" + "-+-".join("-" * 30 for _ in range(2)) + "-+"
            print(term.green(boundary))

        print(term.bold("Moving Single Issue to Sprint:"))
        print_boundary()
        print_row(headers)
        print_boundary()

        issue = jira.issue(issue_key)
        jira.add_issues_to_sprint(target_sprint_id, [issue.key])
        print_row(
            [
                issue.key,
                "Moved",
                f"Issue {issue_key} moved to Sprint {target_sprint_id}",
            ]
        )
        print_boundary()
    except Exception as e:
        logging.error(f"Error moving issue {issue_key} to Sprint: {e}")


def move_issues_in_range_to_sprint_tui(
    jira, project_key, start_issue_key, end_issue_key, target_sprint_id
):
    """
    Render a text-based user interface (TUI) to move issues within a range to a specified sprint.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project containing the issues.
        start_issue_key (str): Key of the first issue in the range.
        end_issue_key (str): Key of the last issue in the range.
        target_sprint_id (str): ID of the target sprint to move the issues to.
    """
    try:
        term = blessed.Terminal()
        headers = ["Issue Key", "Status", "Info"]

        def print_row(row):
            formatted_row = []
            for i, field in enumerate(row):
                if i == 2:
                    formatted_row.append(f"{field:<20}")
                elif i == 3:
                    formatted_row.append(f"{field:<20}")
                else:
                    formatted_row.append(f"{field:<10}")
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            boundary = "+-" + "-+-".join("-" * 30 for _ in range(2)) + "-+"
            print(term.green(boundary))

        print(term.bold("Moving Issues in Range to Sprint:"))
        print_boundary()
        print_row(headers)
        print_boundary()

        start_issue_number = int(start_issue_key.split("-")[1])
        end_issue_number = int(end_issue_key.split("-")[1])

        for i in range(start_issue_number, end_issue_number + 1):
            issue_key = f"{project_key}-{i}"
            try:
                issue = jira.issue(issue_key)
                jira.add_issues_to_sprint(target_sprint_id, [issue.key])
                print_row(
                    [
                        issue.key,
                        "Moved",
                        f"Issue {issue_key} moved to Sprint {target_sprint_id}",
                    ]
                )
                print_boundary()
            except Exception as e:
                print_row([issue_key, f"Error: {e}", ""])
                print_boundary()
                logging.error(f"Error moving issue {issue_key} to Sprint: {e}")
    except Exception as e:
        logging.error(f"Error moving issues in range to Sprint: {e}")


def move_all_issues_to_sprint_tui(jira, project_key, target_sprint_id):
    """
    Render a text-based user interface (TUI) to move all issues in a project to a specified sprint.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project containing the issues.
        target_sprint_id (str): ID of the target sprint to move the issues to.
    """
    try:
        term = blessed.Terminal()
        headers = ["Issue Key", "Status", "Info"]

        def print_row(row):
            formatted_row = []
            for i, field in enumerate(row):
                if i == 2:
                    formatted_row.append(f"{field:<20}")
                elif i == 3:
                    formatted_row.append(f"{field:<20}")
                else:
                    formatted_row.append(f"{field:<10}")
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            boundary = "+-" + "-+-".join("-" * 30 for _ in range(2)) + "-+"
            print(term.green(boundary))

        print(term.bold("Moving All Issues to Sprint:"))
        print_boundary()
        print_row(headers)
        print_boundary()

        issues = jira.search_issues(f"project={project_key}")
        for issue in issues:
            try:
                jira.add_issues_to_sprint(target_sprint_id, [issue.key])
                print_row(
                    [
                        issue.key,
                        "Moved",
                        f"Issue {issue.key} moved to Sprint {target_sprint_id}",
                    ]
                )
                print_boundary()
            except Exception as e:
                print_row([issue.key, f"Error: {e}", ""])
                print_boundary()
                logging.error(f"Error moving issue {issue.key} to Sprint: {e}")
    except Exception as e:
        logging.error(f"Error moving all issues to Sprint: {e}")


def list_stories_in_sprint_tui(jira, sprint_id):
    """
    Render a text-based user interface (TUI) to list all stories in a specified sprint.

    Args:
        jira: JIRA connection object.
        sprint_id (str): ID of the sprint containing the stories.
    Returns:
        list: A list of dictionaries containing information about each story.
    """
    try:
        term = blessed.Terminal()

        # Construct JQL to search for issues in the given sprint
        jql = f"sprint = {sprint_id} AND issuetype = Task"

        # Search for issues using the constructed JQL
        issues = jira.search_issues(jql)

        # Extract issue keys and summaries from the search result
        story_info = [
            {"key": issue.key, "summary": issue.fields.summary} for issue in issues
        ]

        def print_row(row):
            term = blessed.Terminal()
            formatted_row = [f"{field:<30}" for field in row]  # Adjust width as needed
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            term = blessed.Terminal()
            boundary = "+-" + "-+-".join("-" * 40 for _ in range(2)) + "-+"
            print(term.green(boundary))

        print(term.bold(f"Stories in Sprint {sprint_id}:"))
        print_boundary()
        print_row(["Issue Key", "Summary"])
        print_boundary()

        for story in story_info:
            print_row([story["key"], story["summary"]])

        print_boundary()
        logging.info(f"Retrieved {len(story_info)} stories in sprint {sprint_id}")

        return story_info  # Return list of dictionaries
    except JIRAError as e:
        logging.error(f"Error retrieving stories in sprint: {e}")
        return None


def my_stories_tui(jira, project_key, user):
    """
    Retrieve and display stories assigned to a specific user with TUI formatting.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project.
        user (str): Username of the user.

    Returns:
        list: List of dictionaries containing story keys, summaries, and statuses.
    """
    try:
        term = Terminal()

        # Construct JQL query to retrieve stories for the user with specific statuses
        jql_query = (
            f"project = '{project_key}' AND assignee = '{user}' "
            f"AND issuetype = Task AND status IN ('To Do', 'In Progress', 'In Review')"
        )

        # Search for issues using the JQL query
        issues = jira.search_issues(jql_query)

        # Check if any issues are found
        if not issues:
            print(term.bold_red(f"No stories found assigned to {user}."))
            return None

        # Print user stories with TUI formatting
        print(term.bold(f"Stories assigned to {user}:"))
        print_boundary(term)
        print_row(term, ["Key", "Summary", "Status"])
        print_boundary(term)

        stories = []
        for issue in issues:
            key = issue.key
            summary = issue.fields.summary
            status = issue.fields.status.name
            stories.append({"key": key, "summary": summary, "status": status})
            print_row(term, [key, summary, status])

        print_boundary(term)

        # Return the list of user stories
        return stories

    except Exception as e:
        logging.error(f"Error retrieving stories for user: {e}")
        return None

def print_boundary(term):
    print(term.bold('+' + '-'*48 + '+'))

def print_row(term, columns):
    print(term.bold('| {0: <10} | {1: <30} | {2: <5} |'.format(*columns)))



# def print_row(term, row):
#     """
#     Print a row of data with TUI formatting.

#     Args:
#         term: blessed.Terminal object.
#         row (list): List of fields to print in the row.

#     Returns:
#         None
#     """
#     formatted_row = [f"{field:<30}" for field in row]  # Adjust width as needed
#     print(f"| {' | '.join(formatted_row)} |")


# def print_boundary(term):
#     """
#     Print a boundary line with TUI formatting.

#     Args:
#         term: blessed.Terminal object.

#     Returns:
#         None
#     """
#     boundary = "+-" + "-+-".join("-" * 40 for _ in range(2)) + "-+"
#     print(term.green(boundary))


def list_members(jira, project_key):
    """
    Retrieve the unique user names assigned to issues in a project.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project.

    Returns:
        list or None: List of unique user names if successful, otherwise None.
    """
    try:
        # Construct JQL query to search for issues in the project
        jql_query = f'project="{project_key}"'

        # Search for issues in the project
        issues = jira.search_issues(jql_query, maxResults=False)

        # Extract unique user names from the issues' assignees
        user_names = set(
            issue.fields.assignee.displayName
            for issue in issues
            if issue.fields.assignee
        )

        # Log the user names
        logging.info(f"Users in project {project_key}: {', '.join(user_names)}")

        return list(user_names)
    except Exception as e:
        # Log any exceptions that occur during the process
        logging.error(f"Error fetching users for project {project_key}: {e}")
        return None


def list_members_tui(jira, project_key):
    """
    Retrieve and display unique user names assigned to issues in a project with TUI formatting.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project.

    Returns:
        list or None: List of unique user names if successful, otherwise None.
    """
    try:
        term = blessed.Terminal()

        # Construct JQL query to search for issues in the project
        jql_query = f'project="{project_key}"'

        # Search for issues in the project
        issues = jira.search_issues(jql_query, maxResults=False)

        # Extract unique user names from the issues' assignees
        user_names = set(
            issue.fields.assignee.displayName
            for issue in issues
            if issue.fields.assignee
        )

        # Check if any users are found
        if not user_names:
            print(f"No members found in project {project_key}")
            return None

        # Print members with TUI formatting
        print(term.bold(f"Members in project {project_key}:"))
        print_boundary(term)
        for user in user_names:
            print_row(term, [user])
        print_boundary(term)
        return list(user_names)

    except Exception as e:
        # Log any exceptions that occur during the process
        logging.error(f"Error fetching users for project {project_key}: {e}")
        return None


def print_row(term, row):
    """
    Print a row with TUI formatting.

    Args:
        term: Blessed Terminal object.
        row (list): List of items to be printed as a row.

    Returns:
        None
    """
    formatted_row = [f"{field:<30}" for field in row]  # Adjust width as needed
    print(f"| {' | '.join(formatted_row)} |")


def print_boundary(term):
    """
    Print a boundary line with TUI formatting.

    Args:
        term: Blessed Terminal object.

    Returns:
        None
    """
    boundary = "+-" + "-+-".join("-" * 30 for _ in range(1)) + "-+"
    print(term.green(boundary))


def move_single_issue_to_sprint(jira, issue_key, target_sprint_id):
    """
    Move a single issue to the specified sprint.

    Args:
        jira: JIRA connection object.
        issue_key (str): Key of the issue to be moved.
        target_sprint_id (str): ID of the target sprint.

    Returns:
        None
    """
    try:
        jira.add_issues_to_sprint(target_sprint_id, [issue_key])
        logging.info(f"Issue {issue_key} moved to Sprint {target_sprint_id}")
    except Exception as e:
        logging.error(f"Error moving issue {issue_key} to Sprint: {e}")


def move_issues_in_range_to_sprint(
    jira, project_key, start_issue_key, end_issue_key, target_sprint_id
):
    """
    Move issues within a specified range to the specified sprint.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project.
        start_issue_key (str): Key of the first issue in the range.
        end_issue_key (str): Key of the last issue in the range.
        target_sprint_id (str): ID of the target sprint.

    Returns:
        None
    """
    try:
        start_issue_number = int(start_issue_key.split("-")[1])
        end_issue_number = int(end_issue_key.split("-")[1])

        for i in range(start_issue_number, end_issue_number + 1):
            issue_key = f"{project_key}-{i}"
            jira.add_issues_to_sprint(target_sprint_id, [issue_key])
        logging.info(
            f"Issues from {start_issue_key} to {end_issue_key} moved to Sprint {target_sprint_id}"
        )
    except Exception as e:
        logging.error(f"Error moving issues in range to Sprint: {e}")


def move_all_issues_to_sprint(jira, project_key, target_sprint_id):
    """
    Move all issues in a project to the specified sprint.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project.
        target_sprint_id (str): ID of the target sprint.

    Returns:
        None
    """
    try:
        issues = jira.search_issues(f"project={project_key}")
        issue_keys = [issue.key for issue in issues]
        jira.add_issues_to_sprint(target_sprint_id, issue_keys)
        logging.info(f"All issues moved to Sprint {target_sprint_id}")
    except Exception as e:
        logging.error(f"Error moving all issues to Sprint: {e}")


def get_project_details(jira, project_key):
    """
    Generate a summary for the specified project including projects, sprints, epics, issues, and members.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the project.

    Returns:
        None
    """
    try:
        term = blessed.Terminal()
        print_boundary(term)
        print(term.bold(f"Summary for Project {project_key}:"))
        print_boundary(term)

        # List projects
        print(term.bold("Projects:"))
        projects = jira.projects()
        for project in projects:
            if project.key == project_key:
                print_row(term, [project.key, project.name])
                print_boundary(term)

        # Get board ID
        board_name = (
            f"Board for {project_key}"  # Adjust as per your board naming convention
        )
        board_id = get_board_id(jira, board_name="Dev")
        if board_id is None:
            return

        # Get sprints for board
        print(term.bold("Sprints for Board:"))
        sprints = list_sprints(jira, board_id)
        if sprints:
            for sprint in sprints:
                print_row(term, [sprint.id, sprint.name])
                print_boundary(term)

        # List epics
        print(term.bold("Epics:"))
        epics = list_epics(jira, project_key)
        if epics:
            for epic in epics:
                print_row(term, [epic.key, epic.fields.summary])
                print_boundary(term)

        # Get issues for project
        print(term.bold("Issues:"))
        issues = list_stories_for_project(jira, project_key)
        if issues:
            for issue in issues:
                print_row(
                    term,
                    [
                        issue["Issue Type"],
                        issue["Issue Key"],
                        issue["Status"],
                        issue["Assignee"],
                        issue["Summary"],
                    ],
                )
                print_boundary(term)

        # Get members
        print(term.bold("Members:"))
        members = list_members(jira, project_key)
        if members:
            for member in members:
                print_row(term, [member])
                print_boundary(term)

    except Exception as e:
        logging.error(f"Error generating summary for project {project_key}: {e}")


def print_boundary(term):
    boundary = "+-" + "-+-".join("-" * 70 for _ in range(2)) + "-+"
    print(term.green(boundary))


def print_row(term, row):
    formatted_row = [f"{field:<30}" for field in row]
    print(f"| {' | '.join(formatted_row)} |")


def get_user_account_id(jira, username):
    """
    Retrieve the account ID of a user by their username.

    Args:
        jira: JIRA connection object.
        username (str): Username of the user.

    Returns:
        str or None: The account ID of the user if found, None otherwise.
    """
    try:
        users = jira.search_users(query=username, maxResults=1)
        if users:
            return users[0].accountId
        else:
            logging.error(f"No user found for username: {username}")
            return None
    except JIRAError as e:
        logging.error(f"Error fetching user account ID for {username}: {e}")
        return None


def create_stories_from_csv(jira, project_key, csv_file_path):
    """
    Create stories in JIRA from data in a CSV file.

    Args:
        jira: JIRA connection object.
        project_key (str): Key of the JIRA project.
        csv_file_path (str): Path to the CSV file containing story data.

    Returns:
        None
    """
    try:
        with open(csv_file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

            if not rows:
                logging.warning("The CSV file is empty.")
                return

            for row in rows:
                summary = row.get("Summary")
                description = row.get("Description")
                issue_type = row.get("Issue Type", "Task") 
                assignee_username = row.get("Assignee Username")
                if summary and description:
                    new_story = create_story(jira, project_key, summary, description)
                    if new_story and assignee_username:
                        update_story_assignee(jira, new_story.key, assignee_username)
                else:
                    logging.warning(
                        "Skipped a row due to missing summary or description"
                    )
    except FileNotFoundError:
        logging.error(f"The file {csv_file_path} does not exist.")
    except Exception as e:
        logging.error(f"An error occurred while processing the CSV file: {e}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="jsl", description="Jira Simple Lib Command Line Tool"
    )
    parser.add_argument(
        "--config", help="Path to the configuration file", default="config.json"
    )
    subparsers = parser.add_subparsers(dest="command", required=False)
    # Story Related
    story_parser = subparsers.add_parser("story", help="Actions related to stories")
    story_subparsers = story_parser.add_subparsers(dest="story_action", required=True)
    # Story Related
    create_stories_parser = story_subparsers.add_parser(
        "multiple", help="Create stories from a CSV file"
    )
    create_stories_parser.add_argument(
        "-pk",
        "--project-key",
        metavar="project_key",
        required=True,
        help="Jira project key",
    )
    create_stories_parser.add_argument(
        "-csv",
        "--csv-file-path",
        metavar="csv_file_path",
        required=True,
        help="Path to the CSV file",
    )

    create_story_parser = story_subparsers.add_parser(
        "create", help="Create a new story"
    )
    create_story_parser.add_argument(
        "-pk",
        "--project-key",
        metavar="project_key",
        required=True,
        help="Specify the project key",
    )
    create_story_parser.add_argument(
        "-s",
        "--summary",
        metavar="summary",
        required=True,
        help="Specify the summary of the story",
    )
    create_story_parser.add_argument(
        "-d",
        "--description",
        metavar="description",
        help="Specify the description of the story",
    )
    add_comment_parser = story_subparsers.add_parser(
        "add-comment", help="Add comments to a story"
    )
    add_comment_parser.add_argument(
        "-ik", "--issue-key", metavar="issue_key", required=True
    )
    add_comment_parser.add_argument(
        "-m", "--message", metavar="comment_body", required=True
    )
    get_details_parser = story_subparsers.add_parser(
        "get-details", help="get story details"
    )
    get_details_parser.add_argument(
        "-ik", "--issue-key", metavar="issue_key", required=True
    )
    delete_story_parser = story_subparsers.add_parser("delete", help="Delete a story")
    delete_story_parser.add_argument(
        "-ik", "--issue-key", metavar="issue_key", required=True
    )
    delete_story_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )
    update_story_parser = story_subparsers.add_parser("update", help="Update a story")
    update_story_parser.add_argument(
        "-ik",
        "--issue-key",
        metavar="issue_key",
        required=True,
        help="The key of the story to update",
    )
    update_story_parser.add_argument(
        "-s", "--summary", metavar="new_summary", help="The new summary for the story"
    )
    update_story_parser.add_argument(
        "-d",
        "--description",
        metavar="new_description",
        help="The new description for the story",
    )
    update_story_parser.add_argument(
        "-ns", "--new-status", metavar="new_status", help="The new status for the story"
    )
    update_story_parser.add_argument(
        "-a",
        "--assignee",
        metavar="new_assignee",
        help="The new assignee for the story",
    )
    get_assignee_parser = story_subparsers.add_parser(
        "get-assignee", help="get the assignee of a story"
    )
    get_assignee_parser.add_argument(
        "-ik", "--issue-key", metavar="issue_key", required=True, help="Story key"
    )
    delete_story_parser = story_subparsers.add_parser("delete", help="Delete a story")
    delete_story_parser.add_argument(
        "-ik", "--issue-key", metavar="issue_key", required=True, help="Story Key"
    )
    delete_story_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )

    # Project Related
    project_parser = subparsers.add_parser(
        "project", help="Actions related to projects"
    )
    project_subparsers = project_parser.add_subparsers(
        dest="project_action", required=True
    )
    create_project_parser = project_subparsers.add_parser(
        "create", help="Create a new project"
    )
    create_project_parser.add_argument(
        "-n", "--name", metavar="project_name", required=True
    )
    create_project_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True
    )
    update_project_parser = project_subparsers.add_parser(
        "update", help="Update an existing project"
    )
    update_project_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True
    )
    update_project_parser.add_argument(
        "-nn", "--name", metavar="new_name", required=True
    )
    update_project_parser.add_argument(
        "-nk", "--new-key", metavar="new_key", required=True
    )
    delete_parser = project_subparsers.add_parser(
        "delete", help="Delete a specific project"
    )
    delete_parser.add_argument(
        "-pk",
        "--project-key",
        metavar="project_key",
        required=True,
        help="The key of the project to delete",
    )
    delete_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )
    project_subparsers.add_parser("list", help="List all projects")
    project_subparsers.add_parser(
        "list-members", help="Retrieve members in a Jira project"
    ).add_argument("-pk", "--project-key", metavar="project_key", required=True)
    list_stories_parser = project_subparsers.add_parser(
        "list-stories", help="List all stories in a project"
    )
    list_stories_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True
    )
    my_stories_parser = project_subparsers.add_parser(
        "my-stories", help="List stories assigned to a user in a project"
    )
    my_stories_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True, help="Project key"
    )
    my_stories_parser.add_argument(
        "-u", "--user", metavar="user", required=True, help="User"
    )
    get_project_details_parser = project_subparsers.add_parser(
        "get-details", help="Get details for a project"
    )
    get_project_details_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True, help="Project key"
    )
    get_id_parser = project_subparsers.add_parser(
        "get-id", help="Get the ID of a user by name"
    )
    get_id_parser.add_argument("-u", "--username", metavar="username", required=True)

    # Epic Related
    epic_parser = subparsers.add_parser("epic", help="Actions related to epics")
    epic_subparsers = epic_parser.add_subparsers(dest="epic_action")
    epic_create_parser = epic_subparsers.add_parser("create", help="Create a new epic")
    epic_create_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True
    )
    epic_create_parser.add_argument("-n", "--name", metavar="epic_name", required=True)
    epic_create_parser.add_argument(
        "-s", "--summary", metavar="epic_summary", required=True
    )
    epic_update_parser = epic_subparsers.add_parser(
        "update", help="Update an existing epic"
    )
    epic_update_parser.add_argument(
        "-ek", "--epic-key", metavar="epic_key", required=True
    )
    epic_update_parser.add_argument(
        "-s", "--summary", metavar="new_summary", required=True
    )
    epic_update_parser.add_argument(
        "-d", "--description", metavar="new_description", required=True
    )
    epic_subparsers.add_parser("delete", help="Delete an epic").add_argument(
        "-ek", "--epic-key", metavar="epic_key", required=True
    )
    epic_subparsers.add_parser("list", help="List all epics in a project").add_argument(
        "-pk", "--project-key", metavar="project_key", required=True
    )
    epic_subparsers.add_parser("get-details", help="get epic details").add_argument(
        "-ek", "--epic-key", metavar="epic_key", required=True
    )
    epic_add_issues_parser = epic_subparsers.add_parser(
        "add-issues", help="Add issues to an epic"
    )
    epic_add_issues_parser.add_argument(
        "-ek",
        "--epic-key",
        metavar="epic_key",
        required=True,
        help="The key of the epic to add the stories to",
    )
    epic_add_issues_parser.add_argument(
        "-ik",
        "--issue-key",
        metavar="issue_key",
        nargs="+",
        required=True,
        help="The keys of the stories to add to the epic",
    )
    epic_subparsers.add_parser(
        "unlink-story", help="Unlink a story from its epic"
    ).add_argument("-ik", "--issue-key", metavar="issue_key", required=True)
    delete_epic_parser = epic_subparsers.add_parser("delete", help="Delete an epic")
    delete_epic_parser.add_argument(
        "-ek", "--epic-key", metavar="epic_key", required=True
    )
    delete_epic_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )

    # Board Related
    board_parser = subparsers.add_parser("board", help="Actions related to boards")
    board_subparsers = board_parser.add_subparsers(dest="board_action")
    get_id_parser = board_subparsers.add_parser(
        "get-id", help="Get the ID of a board by name"
    )
    get_id_parser.add_argument("-n", "--name", metavar="board_name", required=True)
    # Sprint Related
    sprint_parser = subparsers.add_parser("sprint", help="Actions related to sprints")
    sprint_subparsers = sprint_parser.add_subparsers(
        dest="sprint_action", help="Sprint update actions"
    )
    sprint_create_parser = sprint_subparsers.add_parser(
        "create", help="Create a new sprint"
    )
    sprint_create_parser.add_argument(
        "-bid", "--board-id", metavar="board_id", required=True
    )
    sprint_create_parser.add_argument(
        "-n", "--name", metavar="sprint_name", required=True
    )
    # Assuming you have already defined the 'sprint_parser' and 'sprint_subparsers' objects

    # Create subparser for updating a sprint
    update_sprint_parser = sprint_subparsers.add_parser("update", help="Update a sprint")

    # Add arguments for updating a sprint
    update_sprint_parser.add_argument(
        "-sid",
        "--sprint-id",
        metavar="sprint_id",
        required=True,
        help="The ID of the sprint to update",
    )
    update_sprint_parser.add_argument(
        "-ns",
        "--new-summary",
        metavar="new_summary",
        help="The new summary for the sprint",
    )
    sprint_subparsers.add_parser("delete", help="Delete a sprint").add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True
    )
    list_sprints_parser = sprint_subparsers.add_parser(
        "list", help="List sprints for a board"
    )
    list_sprints_parser.add_argument(
        "-bid", "--board-id", metavar="board_id", required=True, help="Board ID"
    )
    start_sprint_parser = sprint_subparsers.add_parser("start", help="Start a sprint")
    start_sprint_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    start_sprint_parser.add_argument(
        "-ns", "--new-summary", metavar="new_summary", required=True, help="New summary"
    )
    start_sprint_parser.add_argument(
        "-sd", "--start-date", metavar="start_date", required=True, help="Start date"
    )
    start_sprint_parser.add_argument(
        "-ed", "--end-date", metavar="end_date", required=True, help="End date"
    )
    list_stories_parser = sprint_subparsers.add_parser(
        "list-stories", help="List stories in a sprint"
    )
    list_stories_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    list_stories_parser.add_argument(
        "--print-info",
        action="store_true",
        help="Print information about the retrieved stories",
    )
    complete_stories_parser = sprint_subparsers.add_parser(
        "complete-stories", help="Complete stories in a sprint"
    )
    complete_stories_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    complete_stories_parser.add_argument(
        "--print-info",
        action="store_true",
        help="Print information about the completed stories",
    )
    complete_sprint_parser = sprint_subparsers.add_parser(
        "complete", help="Complete a sprint"
    )
    complete_sprint_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    complete_sprint_parser.add_argument(
        "-sd",
        "--start-date",
        metavar="start_date",
        required=True,
        help="Start date of the sprint",
    )
    complete_sprint_parser.add_argument(
        "-ed",
        "--end-date",
        metavar="end_date",
        required=True,
        help="End date of the sprint",
    )
    get_sprint_details_parser = sprint_subparsers.add_parser(
        "report", help="Generate a sprint report"
    )
    get_sprint_details_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    get_sprint_details_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True, help="Project key"
    )
    delete_sprint_parser = sprint_subparsers.add_parser(
        "delete", help="Delete a sprint"
    )
    delete_sprint_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    delete_sprint_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )
    delete_all_sprints_parser = sprint_subparsers.add_parser(
        "delete-a", help="Delete all sprints in a board"
    )
    delete_all_sprints_parser.add_argument(
        "-bid", "--board-id", metavar="board_id", required=True, help="Board ID"
    )
    delete_all_sprints_parser.add_argument(
        "-y", "--yes", action="store_true", help="Confirm deletion without prompting"
    )
    move_single_issue_parser = sprint_subparsers.add_parser(
        "move-issue", help="Move a single issue to a sprint"
    )
    move_single_issue_parser.add_argument(
        "-ik", "--issue_key", metavar="issue_key", required=True, help="issue_key"
    )
    move_single_issue_parser.add_argument(
        "-sid",
        "--sprint-id",
        metavar="target_sprint_id",
        required=True,
        help="Target sprint ID",
    )

    # Move Issues in Range
    move_range_issue_parser = sprint_subparsers.add_parser(
        "move-issues-range", help="Move issues in a range to a sprint"
    )
    move_range_issue_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True, help="Project key"
    )
    move_range_issue_parser.add_argument(
        "-sik",
        "--start-issue-key",
        metavar="start_issue_key",
        required=True,
        help="Start issue key",
    )
    move_range_issue_parser.add_argument(
        "-eik",
        "--end-issue-key",
        metavar="end_issue_key",
        required=True,
        help="End issue key",
    )
    move_range_issue_parser.add_argument(
        "-sid",
        "--sprint-id",
        metavar="target_sprint_id",
        required=True,
        help="Target sprint ID",
    )

    # Move All Issues
    move_all_issue_parser = sprint_subparsers.add_parser(
        "move-a-issues", help="Move all issues to a sprint"
    )
    move_all_issue_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True, help="Project key"
    )
    move_all_issue_parser.add_argument(
        "-sid",
        "--sprint-id",
        metavar="target_sprint_id",
        required=True,
        help="Target sprint ID",
    )

    return parser


def main():
    parser = parse_arguments()
    args = parser.parse_args()
    config_file = args.config
    initialize(config_file)
    jira_url = os.getenv("JIRA_URL")
    username = os.getenv("USER")
    api_token = os.getenv("API_TOKEN")
    jira = create_jira_connection(jira_url, username, api_token)
    if not jira:
        logger.error("Unable to create Jira connection, exiting.")
        sys.exit(1)
    try:
        if args.command == "story":
            if args.story_action == "multiple":
                create_stories_from_csv(jira, args.project_key, args.csv_file_path)
            elif args.story_action == "add-comment":
                add_comment(jira, args.issue_key, args.message)
            elif args.story_action == "create":
                create_story(jira, args.project_key, args.summary, args.description)
            elif args.story_action == "get-details":
                get_story_details_tui(jira, args.issue_key)
            elif args.story_action == "update":
                if args.summary:
                    update_story_summary(jira, args.issue_key, args.summary)
                if args.description:
                    update_story_description(jira, args.issue_key, args.description)
                if args.new_status:
                    update_story_status(jira, args.issue_key, args.new_status)
                if args.assignee:
                    update_story_assignee(jira, args.issue_key, args.assignee)
            elif args.story_action == "get-assignee":
                get_assignee(jira, args.issue_key)
            elif args.story_action == "delete":
                delete_story(jira, args.issue_key, auto_confirm=args.yes)
        elif args.command == "project":
            if args.project_action == "get-id":
                user_account_id = get_user_account_id(jira, args.username)
                if user_account_id is not None:
                    logging.info(
                        f"Account ID of user '{args.username}': {user_account_id}"
                    )
            elif args.project_action == "create":
                create_jira_project(jira, args.name, args.project_key)
            elif args.project_action == "update":
                update_jira_project(jira, args.project_key, args.name, args.new_key)
            elif args.project_action == "delete":
                delete_project(jira, args.project_key, auto_confirm=args.yes)
            elif args.project_action == "list":
                list_projects(jira)
            elif args.project_action == "list-stories":
                stories = list_stories_for_project(jira, args.project_key)
                if stories:
                    render_tui(stories, fetching_data=False)
                else:
                    logging.error("No stories found")
            elif args.project_action == "list-members":
                list_members_tui(jira, args.project_key)
            elif args.project_action == "my-stories":
                my_stories_tui(jira, args.project_key, args.user)
            elif args.project_action == "get-details":
                get_project_details(jira, args.project_key)
        elif args.command == "epic":
            if args.epic_action == "create":
                create_epic(jira, args.project_key, args.name, args.summary)
            elif args.epic_action == "update":
                update_epic(jira, args.epic_key, args.summary, args.description)
            elif args.epic_action == "delete":
                delete_epic(jira, args.epic_key, auto_confirm=args.yes)
            elif args.epic_action == "list":
                list_epics_tui(jira, args.project_key)
            elif args.epic_action == "get-details":
                get_epic_details_tui(jira, args.epic_key)
            elif args.epic_action == "add-issues":
                add_issues_to_epic(jira, args.epic_key, args.issue_key)
            elif args.epic_action == "unlink-story":
                unlink_story_from_epic(jira, args.issue_key)
        elif args.command == "board":
            if args.board_action == "get-id":
                board_id = get_board_id(jira, args.name)
                if board_id:
                    print(f"The ID of the board '{args.name}' is: {board_id}")
        elif args.command == "sprint":
            if args.sprint_action == "create":
                create_sprint(jira, args.board_id, args.name)        
            elif args.sprint_action == "update":
                    update_sprint_summary(jira, args.sprint_id, args.new_summary)
            elif args.sprint_action == "list":
                sprints = list_sprints_for_board_tui(jira, args.board_id)
                if sprints:
                    for sprint in sprints:
                        logging.info(
                            f"Sprint ID: {sprint.id}, Name: {sprint.name}, State: {sprint.state}"
                        )
            elif args.sprint_action == "start":
                start_sprint(
                    jira,
                    args.sprint_id,
                    args.new_summary,
                    args.start_date,
                    args.end_date,
                )
            elif args.sprint_action == "list-stories":
                list_stories_in_sprint_tui(jira, args.sprint_id)
            elif args.sprint_action == "complete-stories":
                complete_stories_in_sprint(jira, args.sprint_id, args.print_info)
            elif args.sprint_action == "complete":
                complete_sprint(jira, args.sprint_id, args.start_date, args.end_date)
            elif args.sprint_action == "report":
                get_sprint_details_tui(jira, args.sprint_id, args.project_key)
            elif args.sprint_action == "delete":
                delete_sprint(jira, args.sprint_id, auto_confirm=args.yes)
            elif args.sprint_action == "delete-a":
                delete_all_sprints(jira, args.board_id, auto_confirm=args.yes)
            elif args.sprint_action == "move-issue":
                move_single_issue_to_sprint(jira, args.issue_key, args.sprint_id)
            elif args.sprint_action == "move-issues-range":
                move_issues_in_range_to_sprint(
                    jira,
                    args.project_key,
                    args.start_issue_key,
                    args.end_issue_key,
                    args.sprint_id,
                )
            elif args.sprint_action == "move-a-issues":
                move_all_issues_to_sprint(jira, args.project_key, args.sprint_id)
            else:
                logging.error("Failed to establish Jira connection.")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
