import datetime
import argcomplete
from argcomplete.completers import EnvironCompleter
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

# Load credentials from JSON file
def load_credentials(file_path):
    with open(file_path, 'r') as f:
        credentials = json.load(f)
    return credentials

# Set environment variables from credentials
def set_environment_variables(credentials):
    os.environ["JIRA_URL"] = credentials["jira_url"]
    os.environ["API_TOKEN"] = credentials["api_token"]
    os.environ["USER"] = credentials["user"]

# Call the function to load credentials and set environment variables
def initialize():
    credentials = load_credentials("config.json")
    set_environment_variables(credentials)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
def read_config(filename):
    with open(filename, 'r') as f:
        config = json.load(f)
    return config
def create_jira_connection(config_file):
    try:
        with open(config_file, 'r') as file:
            config_data = json.load(file)
            jira_url = config_data.get('jira_url')
            user = config_data.get('user')
            api_token = config_data.get('api_token')

            if not all([jira_url, user, api_token]):
                raise ValueError("Missing or incomplete configuration data")

            jira = JIRA(
                basic_auth=(user, api_token),
                options={'server': jira_url}
            )
            logging.info("Jira connection established successfully.")
            return jira
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_file}")
    except ValueError as ve:
        logging.error(f"Invalid configuration data: {ve}")
    except JIRAError as je:
        logging.error(f"JiraError: {je}")
    except Exception as e:
        logging.error(f"Error creating Jira connection: {e}")
    return None

    # Function to create a new project in Jira
def create_jira_project(jira, project_name, project_key):
    if not jira:
        logging.error("Failed to create project: Jira connection not established.")
        return False

    # Attempt to create the project
    try:
        project = jira.create_project(project_key, project_name)
        logging.info(f"Project '{project_name}' created successfully.")
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
def get_all_projects(jira):
    # Send a request to the projects endpoint
    projects = jira.projects()

    if isinstance(projects, list):
        # If projects is a list, assume it's already the list of projects
        return projects
    elif hasattr(projects, 'status_code') and projects.status_code == 200:
        # Check if the request was successful
        # Extract project information
        projects_info = [{'key': project.key, 'name': project.name} for project in projects]
        return projects_info
    else:
        # If the request was not successful or the response is unexpected, log the error message
        logging.error(f"Failed to retrieve projects: {projects}")
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
        jira.add_comment(issue, comment_body)
        logging.info(f"Comment added to issue {issue_key}")
        return 1  # Return 1 to indicate success
    except JIRAError as e:
        logging.error(f"Error adding comment to issue {issue_key}: {e}")
        return 0  # Return 0 to indicate failure

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
# Function to create a new sprint
def create_sprint(jira_url, jira_username, api_token, board_id, sprint_name):
    create_sprint_api_url = f"{jira_url}/rest/agile/1.0/sprint"
    auth = (jira_username, api_token)
    sprint_data = {
        "name": sprint_name,
        "originBoardId": board_id,
    }
    response_create_sprint = requests.post(
        create_sprint_api_url, json=sprint_data, auth=auth
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
# Get all sprints for the specified board
def get_sprints_for_board(jira, board_id):
    try:
        sprints = jira.sprints(board_id)
        return sprints
    except Exception as e:
        logging.error(f"Error retrieving sprints for board: {e}")
        return None
def move_issues_to_sprint(jira, project_key, start_issue_key, end_issue_key, target_sprint_id):
    start_issue_number = int(start_issue_key.split('-')[1])
    end_issue_number = int(end_issue_key.split('-')[1])

    for i in range(start_issue_number, end_issue_number + 1):
        issue_key = f"{project_key}-{i}"
        try:
            issue = jira.issue(issue_key)
            jira.add_issues_to_sprint(target_sprint_id, [issue.key])
            logging.info(f"Issue {issue_key} moved to Sprint {target_sprint_id}")
        except Exception as e:
            logging.error(f"Error moving issue {issue_key} to Sprint: {e}")

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
def update_sprint_summary(jira, sprint_id, new_summary, sprint_state, start_date, end_date):
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
def create_board(jira_url, api_token, user_email, project_key, project_lead):
    create_board_api_url = f"{jira_url}/rest/agile/1.0/board"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    payload = json.dumps({
        "name": "scrum board",
        "location": {
            "projectKeyOrId": project_key,
            "type": "project"
        },
        "type": "scrum"
    })

    response = requests.post(create_board_api_url, data=payload, headers=headers)

    if response.status_code == 201:
        board_data = response.json()
        board_id = board_data.get("id")
        print(f"Board created successfully. Board ID: {board_id}")
        return board_id
    else:
        print(f"Failed to create board. Status code: {response.status_code}")
        print(response.text)
        return None


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
# def read_epic_details_tui(jira, epic_key):
#     try:
#         term = blessed.Terminal()
#         epic = jira.issue(epic_key)

#         headers = ["Field", "Value"]

#         epic_data = [
#             ("Epic Key", epic.key),
#             ("Summary", epic.fields.summary)

#         ]

#         stories = jira.search_issues(f"'Epic Link' = {epic_key}")
#         story_data = []
#         if stories:
#             for story in stories:
#                 story_data.append(("Story Key", story.key))
#                 story_data.append(("Summary", story.fields.summary))
#                 story_data.append(("Status", story.fields.status.name))
#                 story_data.append(("Assignee", story.fields.assignee.displayName if story.fields.assignee else "Unassigned"))
#                # story_data.append(("Due Date", story.fields.duedate))
#                 #story_data.append(("Start Date", story.fields.customfield_10015 if hasattr(story.fields, "customfield_10015") else "N/A"))
#         else:
#             story_data.append(("No stories found in the Epic.", ""))

#         max_lengths = [len(header) for header in headers]
#         for row in epic_data + story_data:
#             for i, value in enumerate(row):
#                 max_lengths[i] = max(max_lengths[i], len(str(value)))

#         def print_row(row):
#             formatted_row = []
#             for i, field in enumerate(row):
#                 if field is None:
#                     field = ""  # Replace None with an empty string
#                 if isinstance(field, tuple):
#                     formatted_row.append(f"{field[0]:<{max_lengths[i]}}")
#                 else:
#                     formatted_row.append(f"{field:<{max_lengths[i]}}")
#             print(f"| {' | '.join(formatted_row)} |")




#         def print_boundary():
#             boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
#             print(term.green(boundary))

#         print(term.bold("Epic Details:"))
#         print_boundary()
#         print_row(headers)
#         print_boundary()
#         for row in epic_data + story_data:
#             print_row(row)
#             print_boundary()
#     except JIRAError as e:
#         logging.error(f"Error reading epic: {e}")

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
            def print_boundary():
                boundary = "+-" + "-+-".join("-" * length for length in max_lengths) + "-+"
                print(term.green(boundary))

            print(term.bold(table_title))
            print_boundary()
            print_row(headers, max_lengths)
            print_boundary()
            for row in data:
                print_row(row, max_lengths)
                print_boundary()

        print_table(epic_data, epic_headers, epic_max_lengths, "Epic Details:")
        print_table(story_data, story_headers, story_max_lengths, "Stories Linked with Epic:")

    except JIRAError as e:
        logging.error(f"Error reading epic: {e}")

def print_row(row, max_lengths):
    formatted_row = []
    for i, field in enumerate(row):
        if field is None:
            field = ""  # Replace None with an empty string
        formatted_row.append(f"{field:<{max_lengths[i]}}")
    print(f"| {' | '.join(formatted_row)} |")
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

def move_issues_to_sprint_tui(jira, project_key, start_issue_key, end_issue_key, target_sprint_id):
    try:
        term = blessed.Terminal()

        start_issue_number = int(start_issue_key.split('-')[1])
        end_issue_number = int(end_issue_key.split('-')[1])

        headers = ["Issue Key", "Status", "Info"]

        print(term.bold("Moving Issues to Sprint:"))
        print_boundary()
        print_row(headers)
        print_boundary()

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
    except JIRAError as e:
        logging.error(f"Error reading story: {e}")


def print_row(row):
    formatted_row = []
    for i, field in enumerate(row):
        if i == 2:
            formatted_row.append(f"{field:<20}")
        elif i == 3:  # Assuming "INFO" is the third column
            formatted_row.append(f"{field:<20}")  # Adjust width as needed
        else:
            formatted_row.append(f"{field:<10}")
    print(f"| {' | '.join(formatted_row)} |")        
def print_boundary():
    term = blessed.Terminal()
    boundary = "+-" + "-+-".join("-" * 30 for _ in range(2)) + "-+"
    print(term.green(boundary))
def get_stories_in_sprint_tui(jira, sprint_id):
    try:
        term = blessed.Terminal()

        # Construct JQL to search for issues in the given sprint
        jql = f'sprint = {sprint_id} AND issuetype = Task'
        
        # Search for issues using the constructed JQL
        issues = jira.search_issues(jql)
        
        # Extract issue keys and summaries from the search result
        story_info = [{'key': issue.key, 'summary': issue.fields.summary} for issue in issues]
        
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

def print_row(row):
    term = blessed.Terminal()
    formatted_row = [f"{field:<30}" for field in row]  # Adjust width as needed
    print(f"| {' | '.join(formatted_row)} |")

def print_boundary():
    term = blessed.Terminal()
    boundary = "+-" + "-+-".join("-" * 40 for _ in range(2)) + "-+"
    print(term.green(boundary)) 
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

def print_boundary(term):
    boundary = "+-" + "-+-".join("-" * 40 for _ in range(2)) + "-+"
    print(term.green(boundary))   
def my_stories_tui(jira, project_key, user):
    try:
        term = blessed.Terminal()

        # Construct JQL query to retrieve stories for the user
        jql_query = f"project = '{project_key}' AND assignee = '{user}' AND issuetype = Task"

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
def complete_create_project(prefix, parsed_args, **kwargs):
    # Accessing parsed_args just for demonstration
    project_name = parsed_args.project_name
    project_key = parsed_args.project_key
    possible_projects = ['Project1', 'Project2', 'Project3']  # Replace with actual project names/keys from Jira
    completions = [project for project in possible_projects if project.startswith(prefix)]
    return completions

# Define a generic completion function for all commands
def complete_command(prefix, parsed_args, **kwargs):
    command = parsed_args.__dict__.get('__command__')
    if command == 'create_project':
        return complete_create_project(prefix, parsed_args)
    elif command == 'update_project':
        return complete_update_project(prefix, parsed_args)
    elif command == 'delete_all_projects':
        return complete_delete_all_projects(prefix, parsed_args)
    elif command == 'delete_project':
        return complete_delete_project(prefix, parsed_args)
    elif command == 'get_stories':
        return complete_get_stories(prefix, parsed_args)
    elif command == 'delete_all_stories':
        return complete_delete_all_stories(prefix, parsed_args)
    elif command == 'create_story':
        return complete_create_story(prefix, parsed_args)
    elif command == 'update_story_status':
        return complete_update_story_status(prefix, parsed_args)
    elif command == 'update_story_summary':
        return complete_update_story_summary(prefix, parsed_args)
    elif command == 'update_story_description':
        return complete_update_story_description(prefix, parsed_args)
    elif command == 'add_comment':
        return complete_add_comment(prefix, parsed_args)
    elif command == 'read_story_details':
        return complete_read_story_details(prefix, parsed_args)
    elif command == 'delete_story':
        return complete_delete_story(prefix, parsed_args)
    elif command == 'create_epic':
        return complete_create_epic(prefix, parsed_args)
    elif command == 'list_epics':
        return complete_list_epics(prefix, parsed_args)
    elif command == 'update_epic':
        return complete_update_epic(prefix, parsed_args)
    elif command == 'read_epic_details':
        return complete_read_epic_details(prefix, parsed_args)
    elif command == 'add_story_to_epic':
        return complete_add_story_to_epic(prefix, parsed_args)
    elif command == 'unlink_story_from_epic':
        return complete_unlink_story_from_epic(prefix, parsed_args)
    elif command == 'delete_epic':
        return complete_delete_epic(prefix, parsed_args)
    elif command == 'create_sprint':
        return complete_create_sprint(prefix, parsed_args)
    elif command == 'get_sprints_for_board':
        return complete_get_sprints_for_board(prefix, parsed_args)
    elif command == 'move_issues_to_sprint':
        return complete_move_issues_to_sprint(prefix, parsed_args)
    elif command == 'start_sprint':
        return complete_start_sprint(prefix, parsed_args)
    elif command == 'get_stories_in_sprint':
        return complete_get_stories_in_sprint(prefix, parsed_args)
    elif command == 'complete_stories_in_sprint':
        return complete_complete_stories_in_sprint(prefix, parsed_args)
    elif command == 'complete_sprint':
        return complete_complete_sprint(prefix, parsed_args)
    elif command == 'update_sprint_summary':
        return complete_update_sprint_summary(prefix, parsed_args)
    elif command == 'sprint_report':
        return complete_sprint_report(prefix, parsed_args)
    elif command == 'delete_sprint':
        return complete_delete_sprint(prefix, parsed_args)
    elif command == 'delete_all_sprints':
        return complete_delete_all_sprints(prefix, parsed_args)
    elif command == 'create_board':
        return complete_create_board(prefix, parsed_args)
    elif command == 'get_board_id':
        return complete_get_board_id(prefix, parsed_args)
    elif command == 'my_stories':
        return complete_my_stories(prefix, parsed_args)
    else:
        return []

#  Register completion function dynamically for all commands
def register_completion_functions(parser):
    parser.set_defaults(__command__=None)  # Create a default command attribute

    for action in parser._actions:
        if action.dest.startswith("--"):
            parser._registries[argcomplete.ACTION_REGISTRY].register(action.dest, complete_command)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Jira CLI Tool')
    parser.add_argument('--config', help='Path to the configuration file', default='config.json').completer = EnvironCompleter
    parser.add_argument("--create-project", nargs=2, metavar=("\tproject_name", "project_key"),help="\n Create a new project. Example: --create-project MyProject MP").completer = EnvironCompleter
    parser.add_argument("--update-project", nargs=3, metavar=("\tproject_key", "new_name", "new_key"), help="\nUpdate an existing project.Example: --update-project MP NewName NewKey").completer = EnvironCompleter
    parser.add_argument("--get-all-projects",help="list of all projects")
    parser.add_argument("--delete-all-projects",help="Delete all projects", action="store_true").completer = EnvironCompleter
    parser.add_argument("--delete-project",metavar="\tproject_key", help="\nDelete a specific project.Example: --delete-project MP").completer = EnvironCompleter
    parser.add_argument("--get-stories", metavar="\tproject_key", help="\nGet stories for a project. Example: --get-stories MP").completer = EnvironCompleter
    parser.add_argument("--delete-all-stories", metavar="\tproject_key", help="\nDelete all stories in a project. Example: --delete-all-stories MP").completer = EnvironCompleter
    parser.add_argument("--create-story", nargs=3, metavar=("\tproject_key", "summary", "description"), help="\nCreate a new story. Example: --create-story MP \"Summary\" \"Description\"").completer = EnvironCompleter
    parser.add_argument("--update-story-status", nargs=2, metavar=("\tstory_key", "new_status"), help="\nUpdate story status. Example: --update-story-status ST-1 \"In Progress\"").completer = EnvironCompleter
    parser.add_argument("--update-story-summary", nargs=2, metavar=("\tstory_key", "new_summary"), help="\nUpdate story summary. Example: --update-story-summary ST-1 \"New Summary\"").completer = EnvironCompleter
    parser.add_argument("--update-story-description", nargs=2, metavar=("\tstory_key", "new_description"), help="\nUpdate story description. Example: --update-story-description ST-1 \"New Description\"").completer = EnvironCompleter
    parser.add_argument("--add-comment", nargs=2, metavar=("\tissue_key", "comment_body"), help="\nAdd comments to issue. Example: --add-comment \"issue-key\" \"Comment body\"").completer = EnvironCompleter
    parser.add_argument("--read-story-details", metavar="\tstory_key", help="\nRead story details. Example: --read-story-details ST-1").completer = EnvironCompleter
    parser.add_argument("--delete-story", metavar="\tstory_key", help="\nDelete a story. Example: --delete-story ST-1").completer = EnvironCompleter
    parser.add_argument("--create-epic", nargs=3, metavar=("\tproject_key", "epic_name", "epic_summary"), help="\nCreate a new epic. Example: --create-epic PROJ-1 \"Epic Name\" \"Epic Summary\"").completer = EnvironCompleter
    parser.add_argument("--list-epics", metavar="\tproject_key", help="\nList all epics in a project. Example: --list-epics PROJ-1").completer = EnvironCompleter
    parser.add_argument("--update-epic", nargs=3, metavar=("\tepic_key", "new_summary", "new_description"), help="\nUpdate an existing epic. Example: --update-epic EPIC-1 \"New Summary\" \"New Description\"").completer = EnvironCompleter
    parser.add_argument("--read-epic-details", metavar="\tepic_key", help="\nRead epic details. Example: --read-epic-details EPIC-1").completer = EnvironCompleter
    parser.add_argument("--add-story-to-epic", nargs=2, metavar=("\tepic_key", "story_key"), help="\nAdd a story to an epic. Example: --add-story-to-epic EPIC-1 STORY-1").completer = EnvironCompleter
    parser.add_argument("--unlink-story-from-epic", metavar="\tstory_key", help="\nUnlink a story from its epic. Example: --unlink-story-from-epic STORY-1").completer = EnvironCompleter
    parser.add_argument("--delete-epic", metavar="\tepic_key", help="\nDelete an epic. Example: --delete-epic EPIC-1").completer = EnvironCompleter
    parser.add_argument("--create-sprint", nargs=1, metavar=("\tsprint_name"), help="\nCreate a new sprint").completer = EnvironCompleter
    parser.add_argument('--get-sprints-for-board', dest='board_id', help='ID of the board for which to retrieve sprints').completer = EnvironCompleter
    parser.add_argument('--move-issues-to-sprint', nargs=4, metavar=("\tproject_key", "start_issue_key", "end_issue_key", "target_sprint_id"), help="\nMove issues to a sprint").completer = EnvironCompleter
    parser.add_argument("--start-sprint", nargs=4, metavar=("\tsprint_id", "new_summary", "start_date", "end_date"), help="\nStart a sprint").completer = EnvironCompleter
    parser.add_argument("--get-stories-in-sprint", nargs=1, metavar=("\tsprint_id"), help="\nGet list of stories in a sprint").completer = EnvironCompleter
    parser.add_argument("--complete-stories-in-sprint", nargs=1, metavar=("\tsprint_id"), help="\nComplete stories in a sprint").completer = EnvironCompleter
    parser.add_argument("--complete-sprint", nargs=3, metavar=("\tsprint_id", "start_date", "end_date"), help="\nComplete a sprint").completer = EnvironCompleter
    parser.add_argument("--update-sprint-summary", nargs=5, metavar=("sprint_id", "new_summary", "sprint_state", "start_date", "end_date"), help="Update sprint summary").completer = EnvironCompleter
    parser.add_argument("--sprint-report", nargs=2, metavar=("\tsprint_id", "project_key"), help="\nGenerate sprint report").completer = EnvironCompleter
    parser.add_argument("--delete-sprint", nargs=1, metavar=("\tsprint_id"), help="\nDelete a sprint").completer = EnvironCompleter
    parser.add_argument("--delete-all-sprints", action="store_true", help="\nDelete all sprints").completer = EnvironCompleter
    parser.add_argument("--create-board", nargs=3, metavar=("\tproject_key", "project_lead", "user_email"), help="\hCreate a new board").completer = EnvironCompleter
    parser.add_argument("--get-board-id", nargs=1, metavar=("\tboard_name"), help="\nGet the ID of a board by name").completer = EnvironCompleter
    parser.add_argument("--my-stories", nargs=2, metavar=("\tproject_key", "user"), help="\nGet stories assigned to a user").completer = EnvironCompleter
    argcomplete.autocomplete(parser)
    return parser

def main():
    parser = parse_arguments()
    args = parser.parse_args()
    # Initialize Blessed terminal
    term = Terminal() 
    # Register and enable tab completion
    register_completion_functions(parser)
    argcomplete.autocomplete(parser)
    # Create Jira connection
    jira = create_jira_connection(args.config)
    if not jira:
        return
    initialize()
    if args.create_project:
        project_name, project_key = args.create_project
        if create_jira_project(jira, project_name, project_key):
            logging.info(f"Project '{project_name}' created successfully with key '{project_key}'.")
        else:
            logging.error(f"Failed to create project '{project_name}' with key '{project_key}'.")

    if args.update_project:
        project_key, new_name, new_key = args.update_project
        if update_jira_project(jira, project_key, new_name, new_key):
            logging.info(f"Project '{project_key}' updated successfully with new name '{new_name}' and key '{new_key}'.")
        else:
            logging.error(f"Failed to update project '{project_key}' with new name '{new_name}' and key '{new_key}'.")
            projects = get_all_projects(jira)
            if projects:
                for project in projects:
                    if isinstance(project, dict):
                        logging.info(f"Project Key: {project['key']}, Name: {project['name']}")
                    else:
                        logging.error(f"Unexpected project format: {project}")
            else:
                logging.error("Failed to retrieve projects.")
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
    else:
        # Logic for other options if needed
        pass
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
        add_comment(jira, args.issue_key, args.comment_body)

    if args.read_story_details:
        read_story_details_tui(jira, *args.read_story_details)

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
    if args.create_epic:
        epic_result = create_epic(jira, *args.create_epic)
        if epic_result:
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
        unlink_result = unlink_story_from_epic(jira, args.unlink_story_from_epic)
        if unlink_result:
            logging.info("Story unlinked from epic successfully.")
        else:
            logging.error("Failed to unlink story from epic.")

    if args.delete_epic:
        delete_result = delete_epic(jira, args.delete_epic)
        if delete_result:
            logging.info("Epic deleted successfully.")
        else:
            logging.error("Failed to delete epic.")
    if args.create_sprint:
        sprint_id = create_sprint(args.url, args.username, args.api_token, args.board_id, *args.create_sprint)
        if sprint_id:
            logging.info(f"Sprint created successfully with ID: {sprint_id}")
        else:
            logging.error("Failed to create sprint.")
            get_sprints_for_board_tui(jira,args.board_id)
    if args.move_issues_to_sprint:
        project_key, start_issue_key, end_issue_key, target_sprint_id = args.move_issues_to_sprint
        move_issues_to_sprint_tui(jira, project_key, start_issue_key, end_issue_key, target_sprint_id)  
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

    if args.update_sprint_summary:
        if update_sprint_summary(jira, *args.update_sprint_summary):
            logging.info("Sprint summary updated successfully.")
        else:
            logging.error("Failed to update sprint summary.")

    if args.sprint_report:
        sprint_report_tui(jira, *args.sprint_report)

    if args.delete_sprint:
        if delete_sprint(jira, *args.delete_sprint):
            logging.info("Sprint deleted successfully.")
        else:
            logging.error("Failed to delete sprint.")

    if args.delete_all_sprints:
        if delete_all_sprints(jira, args.board_id):
            logging.info("All sprints deleted successfully.")
        else:
            logging.error("Failed to delete all sprints.")
    if args.create_board:
        board_id = create_board(*args.create_board)
        if board_id is not None:
            logging.info(f"Board created successfully. Board ID: {board_id}")
        else:
            logging.error("Failed to create board.")

    if args.get_board_id:
        board_id = get_board_id(jira, args.get_board_id[0])
        if board_id is not None:
            logging.info(f"Board ID for '{args.get_board_id[0]}': {board_id}")
        else:
            logging.error("Failed to retrieve board ID.")

    if args.my_stories:
        user_stories = my_stories_tui(jira, *args.my_stories)
    # tasks = search(jira, args.query)
    # if tasks:
    #     for task in tasks:
    #         print(f"Key: {task['key']}")
    #         print(f"Summary: {task['summary']}")
    #         print(f"Status: {task['status']}")
    #         print(f"Assignee: {task['assignee']}")
    #         print("-------------------------")
    # else:
    #     print("No tasks found.")

        
    
if __name__ == "__main__":
    main()



