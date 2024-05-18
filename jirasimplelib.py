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
import sys

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
    config_data = {
        "jira_url": jira_url,
        "user": username,
        "api_token": api_token
    }
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
        logging.info(f"Project '{project_name}' created successfully with key '{project_key}'.")
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
def get_stories_for_project(jira, project_key):
    try:
        jql_query = f"project = {project_key} AND issuetype in (Bug, Task, Story)"
        issues = jira.search_issues(jql_query)
        stories = [{
            "Issue Type": issue.fields.issuetype.name,
            "Issue Key": issue.key,
            "Status": issue.fields.status.name,
            "Assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
            "Summary": issue.fields.summary,
        } for issue in issues]
        return stories
    except Exception as e:
        logging.error(f"Error retrieving stories for project: {e}")
        return None

def delete_all_stories_in_project(jira, project_key):
    try:
        # Retrieve all issues (stories) in the project
        issues = jira.search_issues(f'project={project_key}')

        # Delete each story
        for issue in issues:
            issue.delete()
            logging.info(f"Story deleted successfully. Key: {issue.key}")

        logging.info(f"All stories in Project {project_key} have been deleted.")
        return True
    except Exception as e:
        logging.error(f"Error deleting stories in project: {e}")
        raise  # Re-raise the exception to propagate it further

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
            if transition['to']['name'] == new_status:
                jira.transition_issue(issue, transition['id'])
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
def assignee_name(jira, issue_key):
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
            #customfield_10000=epic_name  # Replace with the appropriate custom field ID for Epic name
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
                logging.info(f"Start Date: {story.fields.customfield_10015}")  # Replace 'xxxxx' with the custom field ID for start date
        else:
            logging.info("No stories found in the Epic.")
        
    except JIRAError as e:
        logging.error(f"Error reading epic: {e}")

#Add story to epic
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
        story.update(fields={'customfield_10014': None})  # Replace 'customfield_123456' with the actual Epic Link field ID

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
def get_sprints_for_board(jira, board_id):
    try:
        sprints = jira.sprints(board_id)
        return sprints
    except Exception as e:
        logging.error(f"Error retrieving sprints for board: {e}")
        return None

def start_sprint(jira, sprint_id, new_summary, start_date, end_date):
    try:
        sprint = jira.sprint(sprint_id)
        if sprint.state == 'CLOSED':
            logging.warning(f"Sprint {sprint_id} is already closed. You cannot restart it.")
            return "Sprint is closed"
        elif sprint.state == 'ACTIVE':
            logging.warning(f"Sprint {sprint_id} is already active. No action taken.")
            return sprint
        else:
            sprint.update(
                name=new_summary,
                state='active',
                startDate=start_date,
                endDate=end_date
            )
            logging.info(f"Sprint {sprint_id} started successfully.")
            return sprint
    except JIRAError as e:
        logging.error(f"Error starting sprint {sprint_id}: {e}")
        return None

def get_stories_in_sprint(jira, sprint_id, print_info=False):
    try:
        # Construct JQL to search for issues in the given sprint
        jql = f'sprint = {sprint_id} AND issuetype = Task'
        
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
        story_keys = get_stories_in_sprint(jira, sprint_id, print_info)
        
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


    #complete sprint 
def complete_sprint(jira, sprint_id, start_date, end_date):
    try:
        sprint = jira.sprint(sprint_id)
        sprint_name = sprint.name
        sprint.update(name=sprint_name, state='closed', startDate=start_date, endDate=end_date)
        logging.info(f"Sprint '{sprint_name}' ({sprint_id}) has been completed.")
        return True
    except JIRAError as e:
        logging.error(f"Error completing sprint: {e}")
        return False
# Function to update sprint summary
def update_sprint(jira, sprint_id, new_summary, sprint_state, start_date, end_date):
    try:
        sprint = jira.sprint(sprint_id)
        sprint.update(
            name=new_summary, state=sprint_state, startDate=start_date, endDate=end_date
        )
        logging.info(f"Sprint summary updated successfully. ID: {sprint_id}")
        return sprint
    except JIRAError as e:
        logging.error(f"Error updating sprint summary: {e}")
        return None
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
        jql_query = f'project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}'

        # Search for issues using the JQL query
        issues = jira.search_issues(jql_query)

        # Count issue statuses
        status_counts = {'To Do': 0, 'In Progress': 0, 'Done': 0}
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
        boards = response.json()['values']
        for board in boards:
            if board['name'] == board_name:
                return board['id']
        print(f"Board '{board_name}' not found.")
        return None
    else:
        print(f"Failed to retrieve boards. Status code: {response.status_code}")
        return None
def my_stories(jira, project_key, user):
    try:
        jql_query = f"project = {project_key} AND assignee = {user} AND issuetype = Task"
        issues = jira.search_issues(jql_query)
        stories = [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]
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
    max_lengths[headers.index("Summary")] = max(max_lengths[headers.index("Summary")], max_summary_length)

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
    print_row([header for header in headers]) # Green background and bold text
    print_boundary()

    # Print rows with alternating colors
    for i, issue in enumerate(issues):
        row = [
            issue.get("Issue Type", ""),    # Green text for issue type
            issue.get("Issue Key", ""),   # Dark pink text for issue key
            issue.get("Status", ""),         # Blue text for status
            issue.get("Assignee", ""),       # Cyan text for assignee
            issue.get("Summary", "")
        ]
        print_row(row)  # Reverse colors for alternating rows
        print_boundary()

    # Print status bar with colored text
    status_message = "Fetching..." if fetching_data else "Ready"
    print(term.green(f"Status Bar: {status_message}"))
    
    # Wait for user input and then exit
    with term.cbreak():
        inp = ""
        while inp.lower() != 'q':
            inp = term.inkey()
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
            ("Assignee", story.fields.assignee.displayName if story.fields.assignee else "Unassigned"),
            ("Reporter", story.fields.reporter.displayName if story.fields.reporter else "Unassigned"),
            ("Created", story.fields.created),
            ("Updated", story.fields.updated)
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
            formatted_row = [f"{value:<{max_lengths[i]}}" for i, value in enumerate(row)]
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

        epic_data = [
            ("Epic Key", epic.key),
            ("Summary", epic.fields.summary)
        ]

        stories = jira.search_issues(f"'Epic Link' = {epic_key}")
        story_data = []
        if stories:
            for story in stories:
                story_data.append((
                    story.fields.issuetype.name,
                    story.key,
                    story.fields.status.name,
                    story.fields.assignee.displayName if story.fields.assignee else "Unassigned",
                    story.fields.summary
                ))
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
            print(term.green("+" + "+".join(["-" * (length + 2) for length in max_lengths]) + "+"))
            print(term.green(f"| {' | '.join([header.center(max_lengths[i] + 2) for i, header in enumerate(headers)])} |"))
            print(term.green("+" + "+".join(["-" * (length + 2) for length in max_lengths]) + "+"))
            for row in data:
                print(term.green(f"| {' | '.join([str(value).ljust(max_lengths[i]) for i, value in enumerate(row)])} |"))
                print(term.green("+" + "+".join(["-" * (length + 2) for length in max_lengths]) + "+"))

        print_table(epic_data, epic_headers, epic_max_lengths, "Epic Details:")
        print_table(story_data, story_headers, story_max_lengths, "Stories Linked with Epic:")

    except JIRAError as e:
        logging.error(f"Error reading epic: {e}")

def get_sprints_for_board_tui(jira, board_id):
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
        
        jql_query = f"project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}"
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
        print_row([issue.key, "Moved", f"Issue {issue_key} moved to Sprint {target_sprint_id}"])
        print_boundary()
    except Exception as e:
        logging.error(f"Error moving issue {issue_key} to Sprint: {e}")

def move_issues_in_range_to_sprint_tui(jira, project_key, start_issue_key, end_issue_key, target_sprint_id):
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

        start_issue_number = int(start_issue_key.split('-')[1])
        end_issue_number = int(end_issue_key.split('-')[1])

        for i in range(start_issue_number, end_issue_number + 1):
            issue_key = f"{project_key}-{i}"
            try:
                issue = jira.issue(issue_key)
                jira.add_issues_to_sprint(target_sprint_id, [issue.key])
                print_row([issue.key, "Moved", f"Issue {issue_key} moved to Sprint {target_sprint_id}"])
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

        issues = jira.search_issues(f'project={project_key}')
        for issue in issues:
            try:
                jira.add_issues_to_sprint(target_sprint_id, [issue.key])
                print_row([issue.key, "Moved", f"Issue {issue.key} moved to Sprint {target_sprint_id}"])
                print_boundary()
            except Exception as e:
                print_row([issue.key, f"Error: {e}", ""])
                print_boundary()
                logging.error(f"Error moving issue {issue.key} to Sprint: {e}")
    except Exception as e:
        logging.error(f"Error moving all issues to Sprint: {e}")

def get_stories_in_sprint_tui(jira, sprint_id):
    try:
        term = blessed.Terminal()

        # Construct JQL to search for issues in the given sprint
        jql = f'sprint = {sprint_id} AND issuetype = Task'
        
        # Search for issues using the constructed JQL
        issues = jira.search_issues(jql)
        
        # Extract issue keys and summaries from the search result
        story_info = [{'key': issue.key, 'summary': issue.fields.summary} for issue in issues]
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
            print_row([story['key'], story['summary']])

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
        jql_query = f'project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}'

        # Search for issues using the JQL query
        issues = jira.search_issues(jql_query)

        # Count issue statuses
        status_counts = {'To Do': 0, 'In Progress': 0, 'Done': 0}
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
        user_names = set(issue.fields.assignee.displayName for issue in issues if issue.fields.assignee)

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
        user_names = set(issue.fields.assignee.displayName for issue in issues if issue.fields.assignee)

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
def move_single_issue_to_sprint(jira, issue_key, target_sprint_id):
    try:
        jira.add_issues_to_sprint(target_sprint_id, [issue_key])
        logging.info(f"Issue {issue_key} moved to Sprint {target_sprint_id}")
    except Exception as e:
        logging.error(f"Error moving issue {issue_key} to Sprint: {e}")

def move_issues_in_range_to_sprint(jira, project_key, start_issue_key, end_issue_key, target_sprint_id):
    try:
        start_issue_number = int(start_issue_key.split('-')[1])
        end_issue_number = int(end_issue_key.split('-')[1])

        for i in range(start_issue_number, end_issue_number + 1):
            issue_key = f"{project_key}-{i}"
            jira.add_issues_to_sprint(target_sprint_id, [issue_key])
        logging.info(f"Issues from {start_issue_key} to {end_issue_key} moved to Sprint {target_sprint_id}")
    except Exception as e:
        logging.error(f"Error moving issues in range to Sprint: {e}")

def move_all_issues_to_sprint(jira, project_key, target_sprint_id):
    try:
        issues = jira.search_issues(f'project={project_key}')
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
        board_name = f"Board for {project_key}"  # Adjust as per your board naming convention
        board_id = get_board_id(jira, board_name="Dev")
        if board_id is None:
            return  # Stop execution if board ID retrieval fails

        # Get sprints for board
        print(term.bold("Sprints for Board:"))
        sprints = get_sprints_for_board(jira, board_id)
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
        issues = get_stories_for_project(jira, project_key)
        if issues:
            for issue in issues:
                print_row(term, [
                    issue["Issue Type"], issue["Issue Key"], 
                    issue["Status"], issue["Assignee"], issue["Summary"]
                ])
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
def assign_issue(jira, issue_key, new_assignee):
    try:
        url = f"https://jirasimplelib.atlassian.net/rest/api/2/issue/{issue_key}/assignee"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "name": new_assignee
        }
        print(new_assignee)
        response = requests.put(url, json=data, auth=("user", "api_token"))
        print(response)
        if response.status_code == 204:
            print(f"Issue {issue_key} has been successfully assigned to {new_assignee}.")
        else:
            print(f"Failed to assign issue. Status code: {response.status_code}, Error: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")
def parse_arguments():
    term = blessed.Terminal()
    parser = argparse.ArgumentParser(description=term.green('Jira CLI Tool'))
    # Configuration
    parser.add_argument('--config', help=term.blue('Path to the configuration file'), default='config.json')
    # Issue Related
    issue_group = parser.add_argument_group(term.green('Issue Related'))
    issue_group.add_argument("--assignee-name", metavar="\tissue_key", dest="issue_key", type=str, help=term.blue("Issue key for which to print the assignee name"))
    issue_group.add_argument("--get-members", metavar="\tproject_key", help=term.blue("Retrieve members in a Jira project."))
    issue_group.add_argument('--list-projects', action='store_true', help=term.blue('Get all projects'))
    issue_group.add_argument("--add-comment", nargs=2, metavar=("\tissue_key", "comment_body"), help=term.blue("Add comments to issue."))
    issue_group.add_argument("--read-story-details", metavar="\tstory_key", help=term.blue("Read story details."))
    issue_group.add_argument("--delete-story", metavar="\tstory_key", help=term.blue("Delete a story."))

    # Project Related
    project_group = parser.add_argument_group(term.green('Project Related'))
    project_group.add_argument("--summary",metavar="\t\tproject_key", help=term.blue("Key of the project to generate the summary for."))
    project_group.add_argument("--create-project", nargs=2, metavar=("\tproject_name", "project_key"), help=term.blue("Create a new project."))
    project_group.add_argument("--update-project", nargs=3, metavar=("\tproject_key", "new_name", "new_key"), help=term.blue("Update an existing project."))
    project_group.add_argument("--delete-all-projects", help=term.blue("Delete all projects"), action="store_true")
    project_group.add_argument("--delete-project", metavar="\tproject_key", help=term.blue("Delete a specific project."))
    project_group.add_argument("--get-stories", metavar="\tproject_key", help=term.blue("Get stories for a project."))
    project_group.add_argument("--delete-all-stories", metavar="\tproject_key", help=term.blue("Delete all stories in a project."))
    project_group.add_argument("--create-story", nargs=3, metavar=("\tproject_key", "summary", "description"), help=term.blue("Create a new story."))
    project_group.add_argument("--update-story-status", nargs=2, metavar=("\tstory_key", "new_status"), help=term.blue("Update story status."))
    project_group.add_argument("--update-story-summary", nargs=2, metavar=("\tstory_key", "new_summary"), help=term.blue("Update story summary."))
    project_group.add_argument("--update-story-description", nargs=2, metavar=("\tstory_key", "new_description"), help=term.blue("Update story description."))
    # Epic Relate
    epic_group = parser.add_argument_group(term.green('Epic Related'))
    epic_group.add_argument("--create-epic", nargs=3, metavar=("\tproject_key", "epic_name", "epic_summary"), help=term.blue("Create a new epic."))
    epic_group.add_argument("--list-epics", metavar="\tproject_key", help=term.blue("List all epics in a project."))
    epic_group.add_argument("--update-epic", nargs=3, metavar=("\tepic_key", "new_summary", "new_description"), help=term.blue("Update an existing epic."))
    epic_group.add_argument("--read-epic-details", metavar="\tepic_key", help=term.blue("Read epic details."))
    epic_group.add_argument("--add-story-to-epic", nargs=2, metavar=("\tepic_key", "story_key"), help=term.blue("Add a story to an epic."))
    epic_group.add_argument("--unlink-story-from-epic", metavar="\tstory_key", help=term.blue("Unlink a story from its epic."))
    epic_group.add_argument("--delete-epic", metavar="\tepic_key", help=term.blue("Delete an epic."))

    # Board Related
    board_group = parser.add_argument_group(term.green('Board Related'))
    board_group.add_argument("--get-board-id", nargs=1, metavar=("\tboard_name"), help=term.blue("Get the ID of a board by name"))

    # Sprint Related
    sprint_group = parser.add_argument_group(term.green('Sprint Related'))
    sprint_group.add_argument("--create-sprint", nargs=2, metavar=("\tboard_id","sprint_name"), help=term.blue("Create a new sprint"))
    sprint_group.add_argument("--get-sprints-for-board", metavar="\tboard_id",type=int, help=term.blue('ID of the board for which to retrieve sprints'))
    sprint_group.add_argument('--move-single-issue', nargs=2, metavar=("\tissue_key", "target_sprint_id"), help=term.blue("Move a single issue to a sprint"))
    sprint_group.add_argument('--move-range', nargs=4, metavar=("\tproject_key","start_issue_key", "end_issue_key", "target_sprint_id"), help=term.blue("Move issues in a range to a sprint"))
    sprint_group.add_argument('--move-all', nargs=2, metavar=("\tproject_key","target_sprint_id"), help=term.blue("Move all issues to a sprint"))
    sprint_group.add_argument("--start-sprint", nargs=4, metavar=("\tsprint_id", "new_summary", "start_date", "end_date"), help=term.blue("Start a sprint"))
    sprint_group.add_argument("--get-stories-in-sprint", nargs=1, metavar=("\tsprint_id"), help=term.blue("Get list of stories in a sprint"))
    sprint_group.add_argument("--complete-stories-in-sprint", nargs=1, metavar=("\tsprint_id"), help=term.blue("Complete stories in a sprint"))
    sprint_group.add_argument("--complete-sprint", nargs=3, metavar=("\tsprint_id", "start_date", "end_date"), help=term.blue("Complete a sprint"))
    sprint_group.add_argument("--update-sprint", nargs=5, metavar=("\tsprint_id", "new_summary", "sprint_state", "start_date", "end_date"), help=term.blue("Update sprint summary"))
    sprint_group.add_argument("--sprint-report", nargs=2, metavar=("\tsprint_id", "project_key"), help=term.blue("Generate sprint report"))
    sprint_group.add_argument("--delete-sprint", nargs=1, metavar=("\tsprint_id"), help=term.blue("Delete a sprint"))
    sprint_group.add_argument("--delete-all-sprints", metavar="\tboard_id",type=int, help=term.blue("Delete all sprints"))

    # User Related
    user_group = parser.add_argument_group(term.green('User Related'))
    user_group.add_argument("--my-stories", nargs=2, metavar=("\tproject_key", "user"), help=term.blue("Get stories assigned to a user"))
    user_group.add_argument("--assign-issue", nargs=2,metavar=("issue_key", "new_assignee"),help="assign issue to new user")
    return parser
def main():
    try:
        term = Terminal()
        parser = parse_arguments()
        args = parser.parse_args()       
        config_file = "config.json"
        if os.path.exists(config_file):
            config_data = read_config(config_file)
            jira_url = config_data.get("jira_url")
            username = config_data.get("user")
            api_token = config_data.get("api_token")
            if all([jira_url, username, api_token]):
                jira = create_jira_connection(jira_url, username, api_token)
                if jira:  
                    if args.issue_key:
                        assignee_name(jira, args.issue_key)   
                    if args.assign_issue:
                        issue_key, new_assignee = args.assign_issue
                        assign_issue(jira, issue_key, new_assignee)  
                    if args.get_members:
                        project_key = args.get_members
                        members = get_members_tui(jira, project_key)
                    if args.create_project:
                        project_name, project_key = args.create_project
                        create_jira_project(jira, project_name, project_key)
                    if args.update_project:
                        project_key, new_name, new_key = args.update_project
                        if update_jira_project(jira, project_key, new_name, new_key):
                            logging.info(f"Project '{project_key}' updated successfully with new name '{new_name}' and key '{new_key}'.")
                        else:
                            logging.error(f"Failed to update project '{project_key}' with new name '{new_name}' and key '{new_key}'.")   
                    if args.list_projects:
                        projects = list_projects_tui(jira)
                    if args.delete_all_projects:
                        if delete_all_projects(jira):
                            logging.info("All projects deleted successfully.")
                        else:
                            logging.error("Failed to delete all projects.")
                    if args.delete_project:
                        if delete_project(jira, args.delete_project):
                            logging.info(f"Project '{args.delete_project}' deleted successfully.")
                        else:
                            logging.error(f"Failed to delete project '{args.delete_project}'.")   
                    if args.get_stories:
                        project_key = args.get_stories
                        stories = get_stories_for_project(jira, project_key)
                        if stories:
                            render_tui(stories, fetching_data=False)  # Not fetching data when getting stories
                    if args.delete_all_stories:
                        if delete_all_stories_in_project(jira, args.delete_all_stories):
                            logging.info("All stories deleted successfully.")
                        else:
                            logging.error("Failed to delete all stories.")
                    if args.create_story:
                        create_story(jira, *args.create_story)
                    if args.update_story_status:
                        if update_story_status(jira, *args.update_story_status):
                            logging.info("Story status updated successfully.")
                        else:
                            logging.error("Failed to update story status.")
                    if args.update_story_summary:
                        if update_story_summary(jira, *args.update_story_summary):
                            logging.info("Story summary updated successfully.")
                        else:
                            logging.error("Failed to update story summary.")
                    if args.update_story_description:
                        if update_story_description(jira, *args.update_story_description):
                            logging.info("Story description updated successfully.")
                        else:
                            logging.error("Failed to update story description.")
                    if args.add_comment:
                        issue_key, comment_body = args.add_comment
                        add_comment(jira, issue_key, comment_body)  # Use the assigned variables here
                    if args.read_story_details:
                        story_key = args.read_story_details
                        read_story_details_tui(jira, story_key)
                    if args.delete_story:
                        if delete_story(jira, args.delete_story):
                            logging.info(f"Story '{args.delete_story}' deleted successfully.")
                        else:
                            logging.error(f"Failed to delete story '{args.delete_story}'.")
                    if args.create_epic:
                        if create_epic(jira, *args.create_epic):
                            logging.info("Epic created successfully.")
                        else:
                            logging.error("Failed to create epic.")
                    if args.list_epics:
                        epic_list = list_epics_tui(jira, args.list_epics)
                        if epic_list:
                            logging.info("List of epics:")
                            for epic in epic_list:
                                logging.info(f"Epic Key: {epic.key}, Summary: {epic.fields.summary}")
                        else:
                            logging.error("Failed to retrieve the list of epics.")
                    if args.update_epic:
                        update_result = update_epic(jira, *args.update_epic)
                        if update_result:
                            logging.info("Epic updated successfully.")
                        else:
                            logging.error("Failed to update epic.")
                    if args.read_epic_details:
                        read_epic_details_tui(jira, args.read_epic_details)
                    if args.add_story_to_epic:
                        add_result = add_story_to_epic(jira, *args.add_story_to_epic)
                        if add_result:
                            logging.info("Story added to epic successfully.")
                        else:
                            logging.error("Failed to add story to epic.")
                    if args.unlink_story_from_epic:
                        unlink_story_from_epic(jira, args.unlink_story_from_epic)
                    if args.delete_epic:
                        delete_result = delete_epic(jira, args.delete_epic)
                        if delete_result:
                            logging.info("Epic deleted successfully.")
                        else:
                            logging.error("Failed to delete epic.")
                    if args.create_sprint:
                        board_id, sprint_name = args.create_sprint
                        sprint_id = create_sprint(jira, board_id, sprint_name)
                        if sprint_id:
                            logging.info(f"Sprint created successfully with ID: {sprint_id}")
                        else:
                            logging.error("Failed to create sprint.")
                    if args.get_sprints_for_board:
                        get_sprints_for_board_tui(jira, args.get_sprints_for_board)
                    if args.move_single_issue:
                        issue_key, target_sprint_id = args.move_single_issue
                        move_single_issue_to_sprint_tui(jira, issue_key, target_sprint_id)
                    elif args.move_range:
                        project_key,start_issue_key, end_issue_key, target_sprint_id = args.move_range
                        move_issues_in_range_to_sprint_tui(jira,project_key, start_issue_key, end_issue_key, target_sprint_id)
                    elif args.move_all:
                        project_key,target_sprint_id = args.move_all # Assuming only one argument for sprint ID
                        move_all_issues_to_sprint_tui(jira, project_key, target_sprint_id) 
                    if args.start_sprint:
                        sprint_id, new_summary, start_date, end_date = args.start_sprint
                        sprint = start_sprint(jira, *args.start_sprint)
                    if args.get_stories_in_sprint:
                        stories = get_stories_in_sprint_tui(jira, *args.get_stories_in_sprint)
                    if args.complete_stories_in_sprint:
                        complete_stories_in_sprint(jira, *args.complete_stories_in_sprint)
                    if args.complete_sprint:
                        if complete_sprint(jira, *args.complete_sprint):
                            logging.info("Sprint completed successfully.")
                        else:
                            logging.error("Failed to complete sprint.")
                    if args.update_sprint:
                        if update_sprint(jira, *args.update_sprint):
                            logging.info("Sprint updated successfully.")
                        else:
                            logging.error("Failed to update sprint.")
                    if args.sprint_report:
                        sprint_report_tui(jira, *args.sprint_report)
                    if args.delete_sprint:
                        if delete_sprint(jira, *args.delete_sprint):
                            logging.info("Sprint deleted successfully.")
                        else:
                            logging.error("Failed to delete sprint.")
                    if args.delete_all_sprints:
                        if delete_all_sprints(jira, args.delete_all_sprints):
                            logging.info("All sprints deleted successfully.")
                        else:
                            logging.error("Failed to delete all sprints.")
                    if args.summary:
                        project_key = args.summary
                        summary(jira, project_key)
                    if args.get_board_id:
                        board_id = get_board_id(jira, args.get_board_id[0])
                        if board_id is not None:
                            logging.info(f"Board ID for '{args.get_board_id[0]}': {board_id}")
                        else:
                            logging.error("Failed to retrieve board ID.")
                    if args.my_stories:
                        my_stories_tui(jira, *args.my_stories)
                    pass
                else:
                    logging.error("Failed to establish Jira connection.")
            else:
                logging.warning("Configuration file is missing or incomplete. Asking for credentials...")
                jira_url, username, api_token = get_user_credentials()
                save_config = input("Do you want to save these credentials for future use? (y/n): ")
                if save_config.lower() == 'y':
                    save_credentials_to_config(config_file, jira_url, username, api_token)
        else:
            logging.warning(f"Config file not found: {config_file}. Asking for credentials...")
            jira_url, username, api_token = get_user_credentials()
            save_config = input("Do you want to save these credentials for future use? (y/n): ")
            if save_config.lower() == 'y':
                save_credentials_to_config(config_file, jira_url, username, api_token)

    except KeyboardInterrupt:
        logging.error("Script execution interrupted.")
        sys.exit(1)
if __name__ == "__main__":
    main()