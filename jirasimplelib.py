
from datetime import datetime
import blessed
from blessed import Terminal
import logging
from jira import JIRA, JIRAError
import requests
import json
import os
import argparse 

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
    except Exception as e:
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
 #Function to get a list of stories in a project
def get_stories_for_project(jira, project_key):
    try:
        jql_query = f"project = {project_key} AND issuetype = Task"
        issues = jira.search_issues(jql_query)
        stories = [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]
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
def update_story_status(jira, story_key, new_status):
    try:
        issue = jira.issue(story_key)
        transitions = jira.transitions(issue)
        for transition in transitions:
            if transition['to']['name'] == new_status:
                jira.transition_issue(issue, transition['id'])
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
#Add comments to issues
def add_comment_to_issues_in_range(jira, start_issue_num, end_issue_num, comment_body):
    success_count = 0
    for issue_num in range(start_issue_num, end_issue_num + 1):
        issue_key = f'JST-{issue_num}'
        try:
            issue = jira.issue(issue_key)
            jira.add_comment(issue, comment_body)
            logging.info(f"Comment added to issue {issue_key}")
            success_count += 1
        except JIRAError as e:
            logging.error(f"Error adding comment to issue {issue_key}: {e}")
    logging.info(f"Comments added to {success_count} issues in the range {start_issue_num} to {end_issue_num}")
    return success_count
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
             #Epic related functions
# Function to create a new Epic
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
           # customfield_10012=new_status,  # Epic Status field
           # customfield_10011=new_name  # Epic Name field
            # Add more fields as needed, e.g., customfield_10013 for Epic Color, customfield_10014 for Epic Link
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
#start sprint
def start_sprint(jira, sprint_id, new_summary, start_date, end_date):
    try:
        sprint = jira.sprint(sprint_id)
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

#get list of stories in a sprint
def get_stories_in_sprint(jira, sprint_id):
    try:
        # Construct JQL to search for issues in the given sprint
        jql = f'sprint = {sprint_id} AND issuetype = Task'
        
        # Search for issues using the constructed JQL
        issues = jira.search_issues(jql)
        
        # Extract issue keys and summaries from the search result
        story_info = [(issue.key, issue.fields.summary) for issue in issues]
        
        logging.info(f"Retrieved {len(story_info)} stories in sprint {sprint_id}")
        for key, summary in story_info:
            logging.info(f"Story Key: {key}, Summary: {summary}")
        
        return [key for key, _ in story_info]
    except JIRAError as e:
        logging.error(f"Error retrieving stories in sprint: {e}")
        return None


#complete stories in sprint
def complete_stories_in_sprint(jira, sprint_id):
    try:
        # Get the list of stories in the sprint
        story_keys = get_stories_in_sprint(jira, sprint_id)
        
        if not story_keys:
            logging.error("No stories found in the sprint.")
            return False
        
        # Iterate through each story and update its status to "Done"
        for story_key in story_keys:
            update_story_status(jira, story_key, "Done")
        
        logging.info(f"All stories in sprint {sprint_id} marked as completed.")
        return True
    except Exception as e:
        logging.error(f"Error completing stories in sprint: {e}")
        return False
    #complete sprint 1
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
        sprint_info = jira.sprint(sprint_id)
        if not sprint_info:
            logging.error(f"Sprint with ID {sprint_id} not found.")
            return
        logging.info("Sprint Details:")
        for key, value in sprint_info.raw.items():
            logging.info(f"{key}: {value}")
        jql_query = (
            f"project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}"
        )
        issues = jira.search_issues(jql_query)
        status_counts = {"To Do": 0, "In Progress": 0, "Done": 0}
        for issue in issues:
            status = issue.fields.status.name
            if status in status_counts:
                status_counts[status] += 1
        logging.info("Issue Status Distribution in Sprint:")
        for status, count in status_counts.items():
            logging.info(f"{status}: {count}")

    except Exception as e:
        logging.error(f"Error generating sprint report: {e}")
# Get active sprint velocity
def get_velocity(jira, project_key):
    try:
        completed_velocity = 0
        total_velocity = 0
        boards = jira.boards()
        board_id = next(
            (board.id for board in boards if board.location.projectKey == project_key),
            None,
        )
        if board_id is None:
            logging.error(f"No board found for project {project_key}")
            return None, None
        sprints = jira.sprints(board_id)
        for sprint in sprints:
            sprint_issues = jira.search_issues(
                f"project={project_key} AND Sprint={sprint.id}"
            )
            for issue in sprint_issues:
                if issue.fields.status.name == "Done" and hasattr(
                        issue.fields, "customfield_10031"
                ):
                    story_points = issue.fields.customfield_10031
                    if story_points is not None:
                        completed_velocity += story_points

                if hasattr(
                        issue.fields, "customfield_10031"
                ):
                    story_points = issue.fields.customfield_10031
                    if story_points is not None:
                        total_velocity += story_points

        return completed_velocity, total_velocity

    except Exception as e:
        logging.error(f"Error calculating velocity: {e}")
        return None, None
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
def get_stories_for_user(jira, project_key, user):
    try:
        jql_query = f"project = {project_key} AND assignee = {user} AND issuetype = Task"
        issues = jira.search_issues(jql_query)
        stories = [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]
        return stories
    except Exception as e:
        logging.error(f"Error retrieving stories for user: {e}")
        return None







def parse_arguments():
    parser = argparse.ArgumentParser(description='Jira CLI Tool')
    parser.add_argument('--config', help='Path to the configuration file', default='config.json')
    parser.add_argument("--create-project", nargs=2, metavar=("\tproject_name", "project_key"),help="\n Create a new project. Example: --create-project MyProject MP")
    parser.add_argument("--update-project", nargs=3, metavar=("\tproject_key", "new_name", "new_key"), help="\nUpdate an existing project.Example: --update-project MP NewName NewKey")
    parser.add_argument("--delete-all-projects",help="Delete all projects", action="store_true")
    parser.add_argument("--delete-project",metavar="\tproject_key", help="\nDelete a specific project.Example: --delete-project MP")
    parser.add_argument("--get-stories", metavar="\tproject_key", help="\nGet stories for a project. Example: --get-stories MP")
    parser.add_argument("--delete-all-stories", metavar="\tproject_key", help="\nDelete all stories in a project. Example: --delete-all-stories MP")
    parser.add_argument("--create-story", nargs=3, metavar=("\tproject_key", "summary", "description"), help="\nCreate a new story. Example: --create-story MP \"Summary\" \"Description\"")
    parser.add_argument("--update-story-status", nargs=2, metavar=("\tstory_key", "new_status"), help="\nUpdate story status. Example: --update-story-status ST-1 \"In Progress\"")
    parser.add_argument("--update-story-summary", nargs=2, metavar=("\tstory_key", "new_summary"), help="\nUpdate story summary. Example: --update-story-summary ST-1 \"New Summary\"")
    parser.add_argument("--update-story-description", nargs=2, metavar=("\tstory_key", "new_description"), help="\nUpdate story description. Example: --update-story-description ST-1 \"New Description\"")
    parser.add_argument("--add-comment-to-issues", nargs=3, metavar=("\tstart_issue_num", "end_issue_num", "comment_body"), help="\nAdd comments to issues in a range. Example: --add-comment-to-issues 1 5 \"Comment body\"")
    parser.add_argument("--read-story-details", metavar="\tstory_key", help="\nRead story details. Example: --read-story-details ST-1")
    parser.add_argument("--delete-story", metavar="\tstory_key", help="\nDelete a story. Example: --delete-story ST-1")
    parser.add_argument("--create-epic", nargs=3, metavar=("\tproject_key", "epic_name", "epic_summary"), help="\nCreate a new epic. Example: --create-epic PROJ-1 \"Epic Name\" \"Epic Summary\"")
    parser.add_argument("--list-epics", metavar="\tproject_key", help="\nList all epics in a project. Example: --list-epics PROJ-1")
    parser.add_argument("--update-epic", nargs=3, metavar=("\tepic_key", "new_summary", "new_description"), help="\nUpdate an existing epic. Example: --update-epic EPIC-1 \"New Summary\" \"New Description\"")
    parser.add_argument("--read-epic-details", metavar="\tepic_key", help="\nRead epic details. Example: --read-epic-details EPIC-1")
    parser.add_argument("--add-story-to-epic", nargs=2, metavar=("\tepic_key", "story_key"), help="\nAdd a story to an epic. Example: --add-story-to-epic EPIC-1 STORY-1")
    parser.add_argument("--unlink-story-from-epic", metavar="\tstory_key", help="\nUnlink a story from its epic. Example: --unlink-story-from-epic STORY-1")
    parser.add_argument("--delete-epic", metavar="\tepic_key", help="\nDelete an epic. Example: --delete-epic EPIC-1")
    parser.add_argument("--create-sprint", nargs=1, metavar=("\tsprint_name"), help="\nCreate a new sprint")
    parser.add_argument("--get-sprints-for-board", action="store_true", help="\nGet all sprints for the specified board")
    parser.add_argument("--move-issues-to-sprint", nargs=3, metavar=("\tstart_issue_key", "end_issue_key", "target_sprint_id"), help="\nMove issues to a sprint")
    parser.add_argument("--start-sprint", nargs=4, metavar=("\tsprint_id", "new_summary", "start_date", "end_date"), help="\nStart a sprint")
    parser.add_argument("--get-stories-in-sprint", nargs=1, metavar=("\tsprint_id"), help="\nGet list of stories in a sprint")
    parser.add_argument("--complete-stories-in-sprint", nargs=1, metavar=("\tsprint_id"), help="\nComplete stories in a sprint")
    parser.add_argument("--complete-sprint", nargs=3, metavar=("\tsprint_id", "start_date", "end_date"), help="\nComplete a sprint")
    parser.add_argument("--update-sprint-summary", nargs=5, metavar=("sprint_id", "new_summary", "sprint_state", "start_date", "end_date"), help="Update sprint summary")
    parser.add_argument("--sprint-report", nargs=2, metavar=("\tsprint_id", "project_key"), help="\nGenerate sprint report")
    parser.add_argument("--get-velocity", nargs=1, metavar=("\tproject_key"), help="\nGet active sprint velocity")
    parser.add_argument("--delete-sprint", nargs=1, metavar=("\tsprint_id"), help="\nDelete a sprint")
    parser.add_argument("--delete-all-sprints", action="store_true", help="\nDelete all sprints")
    parser.add_argument("--create-board", nargs=3, metavar=("\tproject_key", "project_lead", "user_email"), help="\hCreate a new board")
    parser.add_argument("--get-board-id", nargs=1, metavar=("\tboard_name"), help="\nGet the ID of a board by name")
    parser.add_argument("--get-stories-for-user", nargs=2, metavar=("\tproject_key", "user"), help="\nGet stories assigned to a user")
    return parser.parse_args()

def main():   
    
        # Initialize blessed
    term = Terminal()

    # Define layout
    main_display_height = term.height - 4
    mini_buffer_height = 3
    status_bar_height = 1

    # Main loop
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        while True:
            # Render main display
            with term.location(0, 0):
                for i in range(main_display_height):
                    print(term.move_yx(i, 0) + " " * term.width)

                # Render tasks in main display area
                with term.location(0, 0):
                    print("Main Display Area")

            # Render mini-buffer
            with term.location(0, main_display_height):
                for i in range(mini_buffer_height):
                    print(term.move_yx(main_display_height + i, 0) + " " * term.width)

                print("Mini-Buffer (Command Line): ", end='')
                user_input = input()

            # Render status bar
            with term.location(0, main_display_height + mini_buffer_height):
                for i in range(status_bar_height):
                    print(term.move_yx(main_display_height + mini_buffer_height + i, 0) + " " * term.width)

                # Update status bar based on application status
                print("Status Bar")

            # Refresh screen
            term.clear()


    initialize()
   # Parse command-line arguments
    args = parse_arguments()
    # Create Jira connection
    jira = create_jira_connection(args.config)
    if not jira:
        return
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
        stories = get_stories_for_project(jira, args.get_stories)
        if stories:
            logging.info(f"Retrieved stories for project '{args.get_stories}'.")
            for story in stories:
                logging.info(f"Story Key: {story.key}, Summary: {story.fields.summary}")
        else:
            logging.error(f"Failed to retrieve stories for project '{args.get_stories}'.")

    if args.delete_all_stories:
        if delete_all_stories_in_project(jira, args.delete_all_stories):
            logging.info("All stories deleted successfully.")
        else:
            logging.error("Failed to delete all stories.")

    if args.create_story:
        if create_story(jira, *args.create_story):
            logging.info("Story created successfully.")
        else:
            logging.error("Failed to create story.")

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

    if args.add_comment_to_issues:
        if add_comment_to_issues_in_range(jira, *args.add_comment_to_issues):
            logging.info("Comments added to issues successfully.")
        else:
            logging.error("Failed to add comments to issues.")

    if args.read_story_details:
        read_story_details(jira, args.read_story_details)

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
        epic_list = list_epics(jira, args.list_epics)
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
        read_epic_details(jira, args.read_epic_details)

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

    if args.get_sprints_for_board:
        sprints = get_sprints_for_board(jira, args.board_id)
        if sprints:
            logging.info("Sprints for the specified board:")
            for sprint in sprints:
                logging.info(f"Sprint ID: {sprint.id}, Name: {sprint.name}")
        else:
            logging.error("Failed to retrieve sprints for the board.")

    if args.move_issues_to_sprint:
        move_issues_to_sprint(jira, args.project_key, *args.move_issues_to_sprint)

    if args.start_sprint:
        sprint_id, new_summary, start_date, end_date = args.start_sprint
        if start_sprint(jira, sprint_id, new_summary, start_date, end_date):
            logging.info(f"Sprint '{new_summary}' ({sprint_id}) started successfully.")
        else:
            logging.error("Failed to start sprint.")

    if args.get_stories_in_sprint:
        stories = get_stories_in_sprint(jira, *args.get_stories_in_sprint)
        if stories:
            logging.info("Stories in the sprint:")
            for story in stories:
                logging.info(f"Story Key: {story['key']}, Summary: {story['summary']}")
        else:
            logging.error("Failed to retrieve stories for the sprint.")
    if args.complete_stories_in_sprint:
        if complete_stories_in_sprint(jira, *args.complete_stories_in_sprint):
            logging.info("Completed all stories in the sprint.")
        else:
            logging.error("Failed to complete stories in the sprint.")

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
        sprint_report(jira, *args.sprint_report)

    if args.get_velocity:
        completed_velocity, total_velocity = get_velocity(jira, *args.get_velocity)
        if completed_velocity is not None and total_velocity is not None:
            logging.info(f"Completed velocity: {completed_velocity}, Total velocity: {total_velocity}")
        else:
            logging.error("Failed to retrieve velocity information.")

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

    if args.get_stories_for_user:
        user_stories = get_stories_for_user(jira, *args.get_stories_for_user)
        if user_stories:
            logging.info(f"Stories assigned to user {args.get_stories_for_user[1]}:")
            for story in user_stories:
                logging.info(f"Key: {story['key']}, Summary: {story['summary']}")
        else:
            logging.info(f"No stories found assigned to user {args.get_stories_for_user[1]}")
        
    
if __name__ == "__main__":
    main()



