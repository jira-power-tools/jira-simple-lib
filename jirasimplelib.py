
from datetime import datetime
import logging
from jira import JIRA, JIRAError
import requests
import json
import argparse 

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

def update_user_story_status(jira, story_key, new_status, user_name):
    issue = jira.issue(story_key)
    if issue.fields.assignee and issue.fields.assignee.name == user_name:
        transitions = jira.transitions(issue)
        for transition in transitions:
            if transition['to'].name.lower() == new_status.lower():
                jira.transition_issue(issue, transition['id'])
                return True
    return False


def parse_arguments():
    parser = argparse.ArgumentParser(description='Jira CLI Tool')
    parser.add_argument('--config', help='Path to the configuration file', default='config.json')
    parser.add_argument('--project-name', help='Name of the Jira project to create')
    parser.add_argument('--project-key', help='Key for the Jira project to create')
    parser.add_argument('--new-name', help='New name for the Jira project')
    parser.add_argument('--new-key', help='New key for the Jira project')
    parser.add_argument('--delete-projects', action='store_true', help='Delete all projects')
    parser.add_argument('--get-stories', action='store_true', help='Get stories for a project')
    parser.add_argument('--delete-stories', action='store_true', help='Delete all stories in a project')
    parser.add_argument('--new-story-summary', help='Summary of the new story to create')
    parser.add_argument('--new-story-description', help='Description of the new story to create')
    parser.add_argument('--update-story-status', help='Update status of a story')
    parser.add_argument('--update-story-summary', help='Update summary of a story')
    parser.add_argument('--update-story-description', help='Update description of a story')
    parser.add_argument('--add-comment-start', type=int, help='Start issue number for adding comments')
    parser.add_argument('--add-comment-end', type=int, help='End issue number for adding comments')
    parser.add_argument('--add-comment-body', help='Body of the comment to be added')
    parser.add_argument('--read-story-details', help='Read details of a story')
    parser.add_argument('--delete-story', help='Delete a story')
    parser.add_argument('--create-epic', help='Create a new Epic')
    parser.add_argument('--list-epics', action='store_true', help='List all Epics in a project')
    parser.add_argument('--update-epic', help='Update an Epic')
    parser.add_argument('--read-epic-details', help='Read details of an Epic')
    parser.add_argument('--add-story-to-epic', help='Add story to an Epic')
    parser.add_argument('--unlink-story-from-epic', help='Unlink story from an Epic')
    parser.add_argument('--delete-epic', help='Delete an Epic')
    parser.add_argument('--create-sprint', help='Create a new sprint')
    parser.add_argument('--get-sprints-for-board', help='Get all sprints for the specified board')
    parser.add_argument('--move-issues-to-sprint', help='Move issues to a sprint')
    parser.add_argument('--start-sprint', help='Start a sprint')
    parser.add_argument('--get-stories-in-sprint', help='Get stories in a sprint')
    parser.add_argument('--complete-stories-in-sprint', help='Complete stories in a sprint')
    parser.add_argument('--complete-sprint', help='Complete a sprint')
    parser.add_argument('--update-sprint-summary', help='Update sprint summary')
    parser.add_argument('--sprint-report', help='Generate sprint report')
    parser.add_argument('--get-velocity', help='Get active sprint velocity')
    parser.add_argument('--delete-sprint', help='Delete a sprint')
    parser.add_argument('--delete-all-sprints', help='Delete all sprints')
    parser.add_argument('--create-board', help='Create a new board')
    parser.add_argument('--get-board-id', help='Get board ID')
    parser.add_argument("--project", required=True, help="Project key")
    parser.add_argument("--user", required=True, help="User to filter")
    parser.add_argument("--action", choices=["get_stories", "update_status"], required=True, help="Action to perform")
    parser.add_argument("--story", help="Story key (required for update_status action)")
    parser.add_argument("--new_status", help="New status for the story (required for update_status action)")
    return parser.parse_args()

def main():   
   # Parse command-line arguments
    args = parse_arguments()
    # Create Jira connection
    jira = create_jira_connection(args.config)
    if not jira:
        return
    # Create Jira project
    if args.project_name and args.project_key:
        create_jira_project(jira, args.project_name, args.project_key)
    # Update Jira project if specified
    if args.new_name or args.new_key:
        update_jira_project(jira, args.project_key, args.new_name, args.new_key)

    # Delete all projects if specified
    if args.delete_projects:
        delete_all_projects(jira)

    # Get stories for a project if specified
    if args.get_stories:
        stories = get_stories_for_project(jira, args.project_key)
        if stories:
            for story in stories:
                logging.info(story)

    # Delete all stories in a project if specified
    if args.delete_stories:
        delete_all_stories_in_project(jira, args.project_key)

    # Create a new story if specified
    if args.new_story_summary and args.new_story_description:
        create_story(jira, args.project_key, args.new_story_summary, args.new_story_description)
    # Update status of a story if specified
    if args.update_story_status:
        update_story_status(jira, args.update_story_status)

    # Update summary of a story if specified
    if args.update_story_summary:
        update_story_summary(jira, args.update_story_summary)

    # Update description of a story if specified
    if args.update_story_description:
        update_story_description(jira, args.update_story_description)

    # Add comments to issues in a range if specified
    if args.add_comment_start and args.add_comment_end and args.add_comment_body:
        add_comment_to_issues_in_range(jira, args.add_comment_start, args.add_comment_end, args.add_comment_body)

    # Read details of a story if specified
    if args.read_story_details:
        read_story_details(jira, args.read_story_details)
    # Delete a story if specified
    if args.delete_story:
        delete_story(jira, args.delete_story)

    # Create a new Epic if specified
    if args.create_epic:
        create_epic(jira, args.project_key, args.create_epic, args.new_story_description)

    # List all Epics in a project if specified
    if args.list_epics:
        epics = list_epics(jira, args.project_key)
        if epics:
            print("Epics in Project", args.project_key)
            for epic in epics:
                print("Key:", epic.key, "| Summary:", epic.fields.summary)
        else:
            print("No epics found for Project", args.project_key)

    # Update an Epic if specified
    if args.update_epic:
        update_epic(jira, args.update_epic, args.new_summary, args.new_description)

    # Read details of an Epic if specified
    if args.read_epic_details:
        read_epic_details(jira, args.read_epic_details)
     # Add story to an Epic if specified
    if args.add_story_to_epic:
        add_story_to_epic(jira, args.add_story_to_epic, args.project_key)

    # Unlink story from an Epic if specified
    if args.unlink_story_from_epic:
        unlink_story_from_epic(jira, args.unlink_story_from_epic)

    # Delete an Epic if specified
    if args.delete_epic:
        delete_epic(jira, args.delete_epic)

    # Create a new sprint if specified
    if args.create_sprint:
        create_sprint(jira, args.create_sprint, args.create_sprint, args.create_sprint, args.create_sprint)

    # Get all sprints for the specified board if specified
    if args.get_sprints_for_board:
        get_sprints_for_board(jira, args.get_sprints_for_board)
    # Move issues to a sprint if specified
    if args.move_issues_to_sprint:
        move_issues_to_sprint(jira, args.project_key, args.start_issue_key, args.end_issue_key, args.target_sprint_id)

    # Start a sprint if specified
    if args.start_sprint:
        start_sprint(jira, args.start_sprint, args.new_summary, args.start_date, args.end_date)

    # Get stories in a sprint if specified
    if args.get_stories_in_sprint:
        get_stories_in_sprint(jira, args.get_stories_in_sprint)

    # Complete stories in a sprint if specified
    if args.complete_stories_in_sprint:
        complete_stories_in_sprint(jira, args.complete_stories_in_sprint)

    # Complete a sprint if specified
    if args.complete_sprint:
        complete_sprint(jira, args.complete_sprint, args.start_date, args.end_date)
     # Update sprint summary if specified
    if args.update_sprint_summary:
        update_sprint_summary(jira, args.update_sprint_summary[0], args.update_sprint_summary[1], args.update_sprint_summary[2], args.update_sprint_summary[3], args.update_sprint_summary[4])

    # Generate sprint report if specified
    if args.sprint_report:
        sprint_report(jira, args.sprint_report[0], args.sprint_report[1])

    # Get active sprint velocity if specified
    if args.get_velocity:
        get_velocity(jira, args.get_velocity)

    # Delete a sprint if specified
    if args.delete_sprint:
        delete_sprint(jira, args.delete_sprint)

    # Delete all sprints if specified
    if args.delete_all_sprints:
        delete_all_sprints(jira, args.delete_all_sprints)

    # Create a new board if specified
    if args.create_board:
        create_board(args.create_board[0], args.create_board[1], args.create_board[2], args.create_board[3], args.create_board[4])

    # Get board ID if specified
    if args.get_board_id:
        get_board_id(jira, args.get_board_id)

    if args.get_stories:
            stories = get_stories_for_user(jira, args.project, args.user)
            if stories:
                for story in stories:
                    print(f"Key: {story['key']}, Summary: {story['summary']}")
            else:
                print("Failed to retrieve stories.")
    else:
            # Handle other command-line options or provide usage information
            pass
    
    update_user_story_status(jira, args.story, args.new_status, args.user)




if __name__ == "__main__":
    main()



