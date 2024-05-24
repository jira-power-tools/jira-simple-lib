import getpass
from requests.auth import HTTPBasicAuth
from jira.exceptions import JIRAError
from datetime import datetime
import blessed
from blessed import Terminal
import logging
from jira import JIRA, JIRAError
import requests
import json
import os
import argparse

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def read_config(filename):
    with open(filename, "r") as f:
        config = json.load(f)
    return config

def create_jira_connection(jira_url, username, api_token):
    try:
        if not all([jira_url, username, api_token]):

            raise ValueError("Missing username, API token, or Jira URL")

        jira = JIRA(basic_auth=(username, api_token), options={"server": jira_url})
        logging.info("Jira connection established successfully.")
        return jira
    except ValueError as ve:
        logging.error(f"Invalid input: {ve}")
    except JIRAError as je:
        logging.error(f"JiraError: {je}")
    except Exception as e:
        logging.error(f"Error creating Jira connection: {e}")
    return None


def get_user_credentials():
    jira_url = input("Enter Jira URL: ")
    username = input("Enter your username: ")
    api_token = getpass.getpass("Enter your API token: ")
    return jira_url, username, api_token


def save_credentials_to_config(config_file, jira_url, username, api_token):
    config_data = {"jira_url": jira_url, "user": username, "api_token": api_token}
    with open(config_file, "w") as f:
        json.dump(config_data, f)
    logging.info(f"Credentials saved to {config_file}")


# Function to create a new project in Jira
def create_jira_project(jira, project_name, project_key):
    if not jira:
        logging.error("Failed to create project: Jira connection not established.")
        return False

    # Attempt to create the project
    try:
        project = jira.create_project(project_key, project_name)
        logging.info(
            f"Project '{project_name}' created successfully with key '{project_key}'."
        )
        return project
    except JIRAError as e:
        logging.error(f"Error creating project: {e}")
        return None


def update_jira_project(jira, project_key, new_name=None, new_key=None):
    if not jira:
        logging.error("Failed to update project: Jira connection not established.")
        return False

    if not new_name and not new_key:
        logging.error("Failed to update project: No new name or key provided.")
        return False

    try:
        project = jira.project(project_key)
        if new_name:
            project.update(name=new_name)
            logging.info(f"Project name updated to '{new_name}' successfully.")
        if new_key:
            project.update(key=new_key)
            logging.info(f"Project key updated to '{new_key}' successfully.")
        return True
    except JIRAError as e:
        logging.error(f"Error updating project: {e}")
        return False
    except Exception as e:
        logging.error(f"Error updating project: {e}")
        return False


# list of all projects
def list_projects(jira):
    try:
        projects = jira.projects()
        for project in projects:
            print(f"Project Key: {project.key}, Name: {project.name}")
        return projects
    except JIRAError as e:
        print(f"Error listing projects: {e}")
        return None


def delete_all_projects(jira):
    try:
        # Get all projects
        projects = jira.projects()

        # Iterate over projects
        for project in projects:
            # Delete project
            jira.delete_project(project.key)
            logging.info(f"Project {project.key} deleted successfully.")

        logging.info("All projects have been deleted.")
        return True
    except Exception as e:
        logging.error(f"Error deleting projects: {e}")
        return False


def delete_project(jira, project_key):
    try:
        # Delete project
        jira.delete_project(project_key)
        logging.info(f"Project {project_key} deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting project {project_key}: {e}")
        return False


def list_stories_for_project(jira, project_key):
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
    except Exception as e:
        logging.error(f"Error retrieving stories for project: {e}")
        return None


def delete_all_stories_in_project(jira, project_key):
    try:
        # Retrieve all issues (stories) in the project
        issues = jira.search_issues(f"project={project_key}")

        # Delete each story
        for issue in issues:
            issue.delete()
            logging.info(f"Story deleted successfully. Key: {issue.key}")

        logging.info(f"All stories in Project {project_key} have been deleted.")
        return True
    except Exception as e:
        logging.error(f"Error deleting stories in project: {e}")
        raise


# Function to create a new story in Jira
def create_story(jira, project_key, summary, description):
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
        return None


def update_story_status(jira, story_key, new_status, print_info=False):
    try:
        issue = jira.issue(story_key)
        transitions = jira.transitions(issue)
        for transition in transitions:
            if transition["to"]["name"] == new_status:
                jira.transition_issue(issue, transition["id"])
                if print_info:
                    logging.info(f"Story status updated successfully. Key: {story_key}")
                return True
        logging.error(f"Invalid status: {new_status}")
        return False
    except JIRAError as e:
        logging.error(f"Error updating story status: {e}")
        return False


# Function to update a story's summary
def update_story_summary(jira, story_key, new_summary):
    try:
        story = jira.issue(story_key)
        story.update(summary=new_summary)
        logging.info(f"Story summary updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        logging.error(f"Error updating story summary: {e}")
        return None


# Function to update a story's description
def update_story_description(jira, story_key, new_description):
    try:
        story = jira.issue(story_key)
        story.update(description=new_description)
        logging.info(f"Story description updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        logging.error(f"Error updating story description: {e}")
        return None


def view_assignee(jira, issue_key):
    try:
        # Retrieve the issue object
        issue = jira.issue(issue_key)

        # Get the assignee of the issue
        assignee = issue.fields.assignee

        if assignee is not None:
            print(f"The assignee of issue {issue_key} is: {assignee.displayName}")
        else:
            print(f"Issue {issue_key} is currently unassigned.")
    except Exception as e:
        print(f"Error: {e}")


# Function to read a story's details
def read_story_details(jira, story_key):
    try:
        story = jira.issue(story_key)
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
    except JIRAError as e:
        logging.error(f"Error reading story: {e}")


# Function to delete a story
def delete_story(jira, story_key):
    try:
        issue = jira.issue(story_key)
        issue.delete()
        logging.info(f"Story deleted successfully. Key: {story_key}")
        return True
    except JIRAError as e:
        logging.error(f"Error deleting story: {e}")
        return False


def add_comment(jira, issue_key, comment_body):
    try:
        issue = jira.issue(issue_key)
        # comment_body = jira.comment(comment_body)
        jira.add_comment(issue, comment_body)
        logging.info(f"Comment added to issue {issue_key}")
        return 1
    except JIRAError as e:
        logging.error(f"Error adding comment to issue {issue_key}: {e}")
        return 0


def create_epic(jira, project_key, epic_name, epic_summary):
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


# Function to list all Epics in a project
def list_epics(jira, project_key):
    try:
        jql_query = f"project = {project_key} AND issuetype = Epic"
        epics = jira.search_issues(jql_query)
        return epics
    except Exception as e:
        logging.error(f"Error listing epics: {e}")
        return None


def update_epic(jira, epic_key, new_summary, new_description):
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


# Function to read the details of an Epic
def read_epic_details(jira, epic_key):
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


# Add story to epic
def add_story_to_epic(jira, epic_key, story_key):
    try:
        epic = jira.issue(epic_key)
        story = jira.issue(story_key)
        jira.add_issues_to_epic(epic.id, [story.id])
        logging.info(f"Story {story_key} added to Epic {epic_key}")
        return True
    except JIRAError as e:
        logging.error(f"Error adding story to epic: {e}")
        return False


# Function to unlink a Story from an Epic
def unlink_story_from_epic(jira, story_key):
    try:
        story = jira.issue(story_key)

        # Update the 'Epic Link' custom field of the story to remove its association with the epic
        story.update(
            fields={"customfield_10014": None}
        )  # Replace 'customfield_123456' with the actual Epic Link field ID

        logging.info(f"Story {story_key} unlinked from its Epic")
        return True
    except JIRAError as e:
        logging.error(f"Error unlinking story from epic: {e}")
        return False


def delete_epic(jira, epic_key):
    try:
        issue = jira.issue(epic_key)
        issue.delete()
        logging.info(f"Epic deleted successfully. Key: {epic_key}")
        return True
    except JIRAError as e:
        logging.error(f"Error deleting epic: {e}")
        return False


def create_sprint(jira, board_id, sprint_name):
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
    try:
        sprints = jira.sprints(board_id)
        return sprints
    except Exception as e:
        logging.error(f"Error retrieving sprints for board: {e}")
        return None


def start_sprint(jira, sprint_id, new_summary, start_date, end_date):
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
    try:
        # Construct JQL to search for issues in the given sprint
        jql = f"sprint = {sprint_id} AND issuetype = Task"

        # Search for issues using the constructed JQL
        issues = jira.search_issues(jql)

        # Extract issue keys from the search result
        story_keys = [issue.key for issue in issues]

        if print_info:
            logging.info(f"Retrieved {len(story_keys)} stories in sprint {sprint_id}")
            for key in story_keys:
                logging.info(f"Story Key: {key}")

        return story_keys
    except JIRAError as e:
        logging.error(f"Error retrieving stories in sprint: {e}")
        return None


def complete_stories_in_sprint(jira, sprint_id, print_info=False):
    try:
        # Get the list of stories in the sprint
        story_keys = list_stories_in_sprint(jira, sprint_id, print_info)

        if not story_keys:
            logging.error("No stories found in the sprint.")
            return False

        # Iterate through each story and update its status to "Done"
        for story_key in story_keys:
            update_story_status(jira, story_key, "Done", print_info)
            logging.info(f"All stories in sprint {sprint_id} marked as completed.")
            return True
    except Exception as e:
        logging.error(f"Error completing stories in sprint: {e}")
        return False


def complete_sprint(jira, sprint_id, start_date, end_date):
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
    try:
        current_sprint = jira.sprint(sprint_id)
        current_state = current_sprint.state
        jira.update_sprint(sprint_id, name=new_summary, state=current_state)
        logging.info(f"Sprint summary updated successfully. ID: {sprint_id}")
        return True
    except JIRAError as e:
        logging.error(f"Error updating sprint summary: {e}")
        return False


def sprint_report(jira, sprint_id, project_key):
    try:
        # Get detailed information about the sprint
        sprint_info = jira.sprint(sprint_id)
        if not sprint_info:
            print(f"Sprint with ID {sprint_id} not found.")
            return

        # Print all details of the sprint
        print("Sprint Details:")
        for key, value in sprint_info.raw.items():
            print(f"{key}: {value}")

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
        print("Issue Status Distribution in Sprint:")
        for status, count in status_counts.items():
            print(f"{status}: {count}")

    except Exception as e:
        print(f"Error generating sprint report: {e}")


# Function to delete a sprint
def delete_sprint(jira, sprint_id):
    try:
        sprint = jira.sprint(sprint_id)
        sprint.delete()
        logging.info(f"Sprint with ID {sprint_id} deleted successfully.")
        return True
    except JIRAError as e:
        logging.error(f"Error deleting sprint: {e}")
        return False


def delete_all_sprints(jira, board_id):
    try:
        # Retrieve all sprints in the board
        sprints = jira.sprints(board_id)

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
    # Make a GET request to retrieve the list of boards
    response = jira._session.get(f'{jira._options["server"]}/rest/agile/1.0/board')
    if response.status_code == 200:
        boards = response.json()["values"]
        for board in boards:
            if board["name"] == board_name:
                return board["id"]
        print(f"Board '{board_name}' not found.")
        return None
    else:
        print(f"Failed to retrieve boards. Status code: {response.status_code}")
        return None


def my_stories(jira, project_key, user):
    try:
        jql_query = (
            f"project = {project_key} AND assignee = {user} AND issuetype = Task"
        )
        issues = jira.search_issues(jql_query)
        stories = [
            {"key": issue.key, "summary": issue.fields.summary} for issue in issues
        ]
        return stories
    except Exception as e:
        logging.error(f"Error retrieving stories for user: {e}")
        return None


def render_tui(issues, fetching_data=False):
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
        print(term.green(boundary))  # Green boundary

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


def read_story_details_tui(jira, story_key):
    try:
        term = blessed.Terminal()
        story = jira.issue(story_key)

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

        max_lengths = [len(header) for header in headers]
        for row in data:
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

        print(term.bold("Story Details:"))
        print_boundary()
        print_row(headers)
        print_boundary()
        for row in data:
            print_row(row)
            print_boundary()
    except JIRAError as e:
        logging.error(f"Error reading story: {e}")


def list_epics_tui(jira, project_key):
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
            formatted_row = []
            for i, field in enumerate(row):
                formatted_row.append(f"{field:<{max_lengths[i]}}")
            print(f"| {' | '.join(formatted_row)} |")

        def print_boundary():
            boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
            print(term.green(boundary))

        print(term.bold("List of Epics:"))
        print_boundary()
        print_row(headers)
        print_boundary()
        for row in data:
            print_row(row)
            print_boundary()
    except JIRAError as e:
        logging.error(f"Error listing epics: {e}")


def list_projects_tui(jira):
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
            formatted_row = [
                f"{value:<{max_lengths[i]}}" for i, value in enumerate(row)
            ]
            print(f"| {' | '.join(formatted_row)} |")

        # Function to print the boundary of the table
        def print_boundary():
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


def read_epic_details_tui(jira, epic_key):
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


def sprint_report_tui(jira, sprint_id, project_key):
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


def sprint_report_tui(jira, sprint_id, project_key):
    try:
        term = blessed.Terminal()

        # Get detailed information about the sprint
        sprint_info = jira.sprint(sprint_id)
        if not sprint_info:
            print(f"Sprint with ID {sprint_id} not found.")
            return

        # Print sprint details with TUI formatting
        print(term.bold("Sprint Details:"))
        print_boundary(term)
        for key, value in sprint_info.raw.items():
            print_row(term, [key, value])
        print_boundary(term)

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

        # Print issue status distribution with TUI formatting
        print(term.bold("Issue Status Distribution in Sprint:"))
        print_boundary(term)
        for status, count in status_counts.items():
            print_row(term, [status, str(count)])
        print_boundary(term)

    except Exception as e:
        print(f"Error generating sprint report: {e}")


def print_row(term, row):
    formatted_row = [f"{field:<30}" for field in row]  # Adjust width as needed
    print(f"| {' | '.join(formatted_row)} |")


def print_boundary():
    term = blessed.Terminal()
    boundary = "+-" + "-+-".join("-" * 40 for _ in range(2)) + "-+"
    print(term.green(boundary))


def my_stories_tui(jira, project_key, user):
    try:
        term = blessed.Terminal()

        # Construct JQL query to retrieve stories for the user
        jql_query = (
            f"project = '{project_key}' AND assignee = '{user}' AND issuetype = Task"
        )

        # Search for issues using the JQL query
        issues = jira.search_issues(jql_query)

        # Check if any issues are found
        if not issues:
            print(f"No stories found assigned to  {user}")
            return None

        # Print user stories with TUI formatting
        print(term.bold(f"Stories assigned to  {user}:"))
        print_boundary(term)
        for issue in issues:
            print_row(term, [issue.key, issue.fields.summary])
        print_boundary(term)

        # Return the list of user stories
        return [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]

    except Exception as e:
        logging.error(f"Error retrieving stories for user: {e}")
        return None


def print_row(term, row):
    formatted_row = [f"{field:<30}" for field in row]  # Adjust width as needed
    print(f"| {' | '.join(formatted_row)} |")


def print_boundary(term):
    boundary = "+-" + "-+-".join("-" * 40 for _ in range(2)) + "-+"
    print(term.green(boundary))


def get_members(jira, project_key):
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


def get_members_tui(jira, project_key):
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
    except Exception as e:
        # Log any exceptions that occur during the process
        logging.error(f"Error fetching users for project {project_key}: {e}")
        return None


def print_row(term, row):
    formatted_row = [f"{field:<30}" for field in row]  # Adjust width as needed
    print(f"| {' | '.join(formatted_row)} |")


def print_boundary(term):
    boundary = "+-" + "-+-".join("-" * 30 for _ in range(1)) + "-+"
    print(term.green(boundary))


def move_single_issue_to_sprint(jira, story_key, target_sprint_id):
    try:
        jira.add_issues_to_sprint(target_sprint_id, [story_key])
        logging.info(f"Issue {story_key} moved to Sprint {target_sprint_id}")
    except Exception as e:
        logging.error(f"Error moving issue {story_key} to Sprint: {e}")


def move_issues_in_range_to_sprint(
    jira, project_key, start_issue_key, end_issue_key, target_sprint_id
):
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
    try:
        issues = jira.search_issues(f"project={project_key}")
        issue_keys = [issue.key for issue in issues]
        jira.add_issues_to_sprint(target_sprint_id, issue_keys)
        logging.info(f"All issues moved to Sprint {target_sprint_id}")
    except Exception as e:
        logging.error(f"Error moving all issues to Sprint: {e}")


def summary(jira, project_key):
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
            return  # Stop execution if board ID retrieval fails

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

        # Get stories for project
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
        members = get_members(jira, project_key)
        if members:
            for member in members:
                print_row(term, [member])
                print_boundary(term)

    except Exception as e:
        print(f"Error retrieving project summary: {e}")


def print_boundary(term):
    boundary = "+-" + "-+-".join("-" * 70 for _ in range(2)) + "-+"
    print(term.green(boundary))


def print_row(term, row):
    formatted_row = [f"{field:<30}" for field in row]
    print(f"| {' | '.join(formatted_row)} |")


def update_assignee(story_key, user_account_id):
    url = f"https://jirasimplelib.atlassian.net/rest/api/2/issue/{story_key}/assignee"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = json.dumps(
        {"accountId": user_account_id}  # Replace with the actual accountId
    )
    auth = HTTPBasicAuth(
        "rimsha.ashfaq@verituslabs.com",
        "ATATT3xFfGF0Nnf69USKMyeqvq0C4X8fxZc2v4Sn5F4VmxYIjEUjtuik2bqy-abJDodOiNCrakl5Ae5R1U-FlvE5AfNJ3b2ZGOprGWJ3GsEnMilU6Aff32m4xsrWhsQdsgQCwrtAPKRZnNU2DSgvvFlep3Twrd9vvZraD2mlW6aeVp_Q2SG3YT0=848384A6",
    )

    try:
        response = requests.put(url, data=payload, headers=headers, auth=auth)
        if response.status_code == 204:
            print(f"Issue {story_key} assigned successfully.")
        else:
            # Print error details
            print(f"Failed to assign issue {story_key}.")
            print(f"Status Code: {response.status_code}")
            print(
                f"Response: {json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(',', ': '))}"
            )
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while trying to assign the issue: {e}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="jsl", description="Jira Simple Lib Command Line Tool"
    )
    # Configuration
    parser.add_argument(
        "--config", help="Path to the configuration file", default="config.json"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    # Story Related
    story_parser = subparsers.add_parser("story", help="Actions related to stories")
    story_subparsers = story_parser.add_subparsers(dest="story_action", required=True)
    # Story Related
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
        "-sk", "--story-key", metavar="story_key", required=True
    )
    add_comment_parser.add_argument(
        "-m", "--message", metavar="comment_body", required=True
    )
    read_details_parser = story_subparsers.add_parser(
        "read-details", help="Read story details"
    )
    read_details_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True
    )
    delete_story_parser = story_subparsers.add_parser("delete", help="Delete a story")
    delete_story_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True
    )
    update_summary_parser = story_subparsers.add_parser(
        "update-summary", help="Update story summary"
    )
    update_summary_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True
    )
    update_summary_parser.add_argument(
        "-s", "--summary", metavar="new_summary", required=True
    )
    update_description_parser = story_subparsers.add_parser(
        "update-description", help="Update story description"
    )
    update_description_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True
    )
    update_description_parser.add_argument(
        "-d", "--description", metavar="new_description", required=True
    )
    update_status_parser = story_subparsers.add_parser(
        "update-status", help="Update the status of a story"
    )
    update_status_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True, help="Story key"
    )
    update_status_parser.add_argument(
        "-ns", "--new-status", metavar="new_status", required=True, help="New status"
    )
    view_assignee_parser = story_subparsers.add_parser(
        "view-assignee", help="View the assignee of a story"
    )
    view_assignee_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True, help="Story key"
    )
    update_assignee_parser = story_subparsers.add_parser(
        "update-assignee", help="Update the assignee of a story"
    )
    update_assignee_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True, help="story key"
    )
    update_assignee_parser.add_argument(
        "-uid",
        "--user-accound-id",
        metavar="user_account_id",
        required=True,
        help="User account ID",
    )
    delete_story_parser = story_subparsers.add_parser("delete", help="Delete a story")
    delete_story_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True, help="Story Key"
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
    project_subparsers.add_parser(
        "delete", help="Delete a specific project"
    ).add_argument("-pk", "--project-key", metavar="project_key", required=True)
    project_subparsers.add_parser("delete-a", help="Delete all projects")
    project_subparsers.add_parser("list", help="List all projects")
    project_subparsers.add_parser(
        "get-members", help="Retrieve members in a Jira project"
    ).add_argument("-pk", "--project-key", metavar="project_key", required=True)
    delete_all_stories_parser = project_subparsers.add_parser(
        "delete-a-stories", help="Delete all stories in a project"
    )
    delete_all_stories_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True
    )
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
    summary_parser = project_subparsers.add_parser(
        "summary", help="Generate summary for a project"
    )
    summary_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True, help="Project key"
    )

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
    epic_subparsers.add_parser("read-details", help="Read epic details").add_argument(
        "-ek", "--epic-key", metavar="epic_key", required=True
    )
    epic_add_story_parser = epic_subparsers.add_parser(
        "add-story", help="Add a story to an epic"
    )
    epic_add_story_parser.add_argument(
        "-ek", "--epic-key", metavar="epic_key", required=True
    )
    epic_add_story_parser.add_argument(
        "-sk", "--story-key", metavar="story_key", required=True
    )
    epic_subparsers.add_parser(
        "unlink-story", help="Unlink a story from its epic"
    ).add_argument("-sk", "--story-key", metavar="story_key", required=True)
    delete_epic_parser = epic_subparsers.add_parser("delete", help="Delete an epic")
    delete_epic_parser.add_argument(
        "-ek", "--epic-key", metavar="epic_key", required=True
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
    sprint_summary_parser = sprint_subparsers.add_parser(
        "update-summary", help="Update sprint summary"
    )
    sprint_summary_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    sprint_summary_parser.add_argument(
        "-ns", "--new_summary", metavar="new_summary", required=True, help="New summary"
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
    sprint_report_parser = sprint_subparsers.add_parser(
        "report", help="Generate a sprint report"
    )
    sprint_report_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    sprint_report_parser.add_argument(
        "-pk", "--project-key", metavar="project_key", required=True, help="Project key"
    )
    delete_sprint_parser = sprint_subparsers.add_parser(
        "delete", help="Delete a sprint"
    )
    delete_sprint_parser.add_argument(
        "-sid", "--sprint-id", metavar="sprint_id", required=True, help="Sprint ID"
    )
    delete_all_sprints_parser = sprint_subparsers.add_parser(
        "delete-a", help="Delete all sprints in a board"
    )
    delete_all_sprints_parser.add_argument(
        "-bid", "--board-id", metavar="board_id", required=True, help="Board ID"
    )
    move_single_issue_parser = sprint_subparsers.add_parser(
        "move-issue", help="Move a single issue to a sprint"
    )
    move_single_issue_parser.add_argument(
        "-sk", "--story_key", metavar="story_key", required=True, help="story_key"
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
    try:
        parser = parse_arguments()
        args = parser.parse_args()
        config_file = args.config
        if os.path.exists(config_file):
            config_data = read_config(config_file)
            jira_url = config_data.get("jira_url")
            username = config_data.get("user")
            api_token = config_data.get("api_token")

            if all([jira_url, username, api_token]):
                jira = create_jira_connection(jira_url, username, api_token)
                if jira:
                    if args.command == "story":
                        if args.story_action == "add-comment":
                            add_comment(jira, args.story_key, args.message)
                        elif args.story_action == "create":
                            create_story(
                                jira, args.project_key, args.summary, args.description
                            )
                        elif args.story_action == "read-details":
                            read_story_details_tui(jira, args.story_key)
                        elif args.story_action == "delete":
                            delete_story(jira, args.story_key)
                        elif args.story_action == "update-summary":
                            update_story_summary(jira, args.story_key, args.summary)
                        elif args.story_action == "update-description":
                            update_story_description(
                                jira, args.story_key, args.description
                            )
                        elif args.story_action == "update-status":
                            success = update_story_status(
                                jira, args.story_key, args.new_status, print_info=True
                            )
                            if success:
                                logging.info(
                                    f"Story {args.story_key} status updated to {args.new_status} successfully."
                                )
                            else:
                                logging.error(
                                    f"Failed to update story {args.story_key} status to {args.new_status}."
                                )
                        elif args.story_action == "view-assignee":
                            view_assignee(jira, args.story_key)
                        elif args.story_action == "update-assignee":
                            update_assignee(args.story_key, args.user_accound_id)
                        elif args.command == "story":
                            if args.story_action == "delete":
                                delete_story(jira, args.story_key)
                    if args.command == "project":
                        if args.project_action == "create":
                            create_jira_project(jira, args.name, args.project_key)
                        elif args.project_action == "update":
                            update_jira_project(
                                jira, args.project_key, args.name, args.new_key
                            )
                        elif args.project_action == "delete":
                            delete_project(jira, args.project_key)
                        elif args.project_action == "delete-a":
                            delete_all_projects(jira)
                        elif args.project_action == "list":
                            list_projects(jira)
                        elif args.project_action == "delete-a-stories":
                            delete_all_stories_in_project(jira, args.project_key)
                        elif args.project_action == "list-stories":
                            stories = list_stories_for_project(jira, args.project_key)
                            if stories:
                                render_tui(stories, fetching_data=False)
                            else:
                                logging.error("No stories found")
                        elif args.project_action == "get-members":
                            get_members_tui(jira, args.project_key)
                        elif args.project_action == "my-stories":
                            my_stories_tui(jira, args.project_key, args.user)
                        elif args.project_action == "summary":
                            summary(jira, args.project_key)
                    elif args.command == "epic":
                        if args.epic_action == "create":
                            create_epic(jira, args.project_key, args.name, args.summary)
                        elif args.epic_action == "update":
                            update_epic(
                                jira, args.epic_key, args.summary, args.description
                            )
                        elif args.epic_action == "delete":
                            delete_epic(jira, args.epic_key)
                        elif args.epic_action == "list":
                            list_epics_tui(jira, args.project_key)
                        elif args.epic_action == "read-details":
                            read_epic_details_tui(jira, args.epic_key)
                        elif args.epic_action == "add-story":
                            add_story_to_epic(jira, args.epic_key, args.story_key)
                        elif args.epic_action == "unlink-story":
                            unlink_story_from_epic(jira, args.story_key)
                    elif args.command == "board":
                        if args.board_action == "get-id":
                            board_id = get_board_id(jira, args.name)
                            if board_id:
                                print(
                                    f"The ID of the board '{args.name}' is: {board_id}"
                                )
                    elif args.command == "sprint":
                        if args.sprint_action == "create":
                            create_sprint(jira, args.board_id, args.name)
                        elif args.sprint_action == "update-summary":
                            update_sprint_summary(
                                jira, args.sprint_id, args.new_summary
                            )
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
                            complete_stories_in_sprint(
                                jira, args.sprint_id, args.print_info
                            )
                        elif args.sprint_action == "complete":
                            complete_sprint(
                                jira, args.sprint_id, args.start_date, args.end_date
                            )
                        elif args.sprint_action == "report":
                            sprint_report_tui(jira, args.sprint_id, args.project_key)
                        elif args.sprint_action == "delete":
                            delete_sprint(jira, args.sprint_id)
                        elif args.sprint_action == "delete-a":
                            delete_all_sprints(jira, args.board_id)
                        elif args.sprint_action == "move-issue":
                            move_single_issue_to_sprint(
                                jira, args.story_key, args.sprint_id
                            )
                        elif args.sprint_action == "move-issues-range":
                            move_issues_in_range_to_sprint(
                                jira,
                                args.project_key,
                                args.start_issue_key,
                                args.end_issue_key,
                                args.sprint_id,
                            )
                        elif args.sprint_action == "move-a-issues":
                            move_all_issues_to_sprint(
                                jira, args.project_key, args.sprint_id
                            )
            else:
                logging.error("Jira configuration is missing required fields.")
        else:
            logging.error(f"Configuration file '{config_file}' not found.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
