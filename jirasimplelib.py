import logging
from jira import JIRA, JIRAError
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='jira_operations.log'
)

# Function to create a Jira connection
def create_jira_connection(jira_url, user, api_token):
    try:
        return JIRA(server=jira_url, basic_auth=(user, api_token))
    except Exception as e:
        logging.error(f"Error creating Jira connection: {e}")
        return None

# Function to list all projects
def list_projects(jira):
    try:
        projects = jira.projects()
        for project in projects:
            logging.info(f"Project Key: {project.key}, Name: {project.name}")
        return projects
    except JIRAError as e:
        logging.error(f"Error listing projects: {e}")
        return None

# Function to get a list of stories in a project
def get_stories_for_project(jira, project_key):
    try:
        jql_query = f"project = {project_key} AND issuetype = Story"
        issues = jira.search_issues(jql_query)
        return issues
    except Exception as e:
        logging.error(f"Error retrieving stories for project: {e}")
        return None

# Function to create a new story in Jira
def create_story(jira, project_key, summary, description, goal):
    try:
        new_story = jira.create_issue(
            project=project_key,
            summary=summary,
            description=description,
            issuetype={"name": "Story"},
        )
        logging.info(f"Story created successfully. Story Key: {new_story.key}")
        return new_story
    except JIRAError as e:
        logging.error(f"Error creating story: {e}")
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

# Function to update a story's status
def update_story_status(jira, story_key, new_status):
    try:
        story = jira.issue(story_key)
        transitions = jira.transitions(story)
        for transition in transitions:
            if transition["to"]["name"] == new_status:
                jira.transition_issue(story, transition["id"])
                logging.info(f"Story status updated successfully. Key: {story_key}")
                return story
        logging.error(f"Invalid status: {new_status}")
        return None
    except JIRAError as e:
        logging.error(f"Error updating story status: {e}")
        return None

# Function to update a story's assignee
def update_story_assignee(jira, story_key, new_assignee):
    try:
        story = jira.issue(story_key)
        story.update(assignee={"name": new_assignee})
        logging.info(f"Story assignee updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        logging.error(f"Error updating story assignee: {e}")
        return None

# Function to update a story's reporter
def update_story_reporter(jira, story_key, new_reporter):
    try:
        story = jira.issue(story_key)
        story.update(reporter={"name": new_reporter})
        logging.info(f"Story reporter updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        logging.error(f"Error updating story reporter: {e}")
        return None

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

# Move story to specific sprint
def move_issue_to_sprint(jira, issue_key, target_sprint_id):
    try:
        issue = jira.issue(issue_key)
        jira.add_issues_to_sprint(target_sprint_id, [issue.key])
        logging.info(f"Issue {issue_key} moved to Sprint {target_sprint_id}")
        return True
    except Exception as e:
        logging.error(f"Error moving issue to Sprint: {e}")
        return False

# Sprint-related functions

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

# Function to update sprint summary
def update_sprint_summary(
        jira, sprint_id, new_summary, sprint_state, start_date, end_date):
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

# Sprint report
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

# Get all sprints for the specified board
def get_sprints_for_board(jira, board_id):
    try:
        sprints = jira.sprints(board_id)
        return sprints
    except Exception as e:
        logging.error(f"Error retrieving sprints for board: {e}")
        return None
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

# Function to read the details of an Epic
def read_epic_details(jira, epic_key):
    try:
        epic = jira.issue(epic_key)
        logging.info(f"Epic Key: {epic.key}")
        logging.info(f"Summary: {epic.fields.summary}")
        # Add more fields as needed
    except JIRAError as e:
        logging.error(f"Error reading epic: {e}")

# Function to update an epic
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
    # Function to delete an Epic
def delete_epic(jira, epic_key):
    try:
        issue = jira.issue(epic_key)
        issue.delete()
        logging.info(f"Epic deleted successfully. Key: {epic_key}")
        return True
    except JIRAError as e:
        logging.error(f"Error deleting epic: {e}")
        return False
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
  



def main():
   
    # Jira credentials and parameters
    jira_url = "https://jtest-vl.atlassian.net"
    api_token = "ATATT3xFfGF0XxgsYvdpyIsMnMOeE9CdUPu75dO7Kh03II60Cg5KYf4d41LTubrshQFmTVCo24mxyYd07-flBqd6DIQHvuKdkWGDrlohGhNMew_hCMqTjgnaPnj2NYCXv4PtzxdzjNq8Vi0vg3NzJcFAQivkuvDjPVnqAs-BdN9PAHfSwGCYex8=7C73D52A"
    user = "rimsha.ashfaq@verituslabs.com"
    project_key = "JE"
    story_key = "JE-187"
    board_id = "2"
    sprint_name = "Sprint test"
    sprint_goal = "Complete feature"

    # Create Jira connection
    jira = create_jira_connection(jira_url, user, api_token)

    # List all projects
    projects = list_projects(jira)

    # Get stories for a project
   # stories = get_stories_for_project(jira, project_key)

    # Create a new story
   # new_story = create_story(jira, project_key, "New Story", "Description", "Goal")

    # Read story details
   # read_story_details(jira, story_key)

    # Update story summary
    #update_story_summary(jira, story_key, "New Summary")

    # Update story description
    #update_story_description(jira, story_key, "New Description")

    # Update story status
    #update_story_status(jira, story_key, "In Progress")

    # Update story assignee
    #update_story_assignee(jira, story_key, "assignee_username")

    # Update story reporter
   # update_story_reporter(jira, story_key, "reporter_username")

    # Delete a story
   # delete_story(jira, story_key)

    # Move issue to a specific sprint
   # move_issue_to_sprint(jira, story_key, "target_sprint_id")

    # Create a new sprint
   # create_sprint(jira_url, user, api_token, board_id, sprint_name)

    # Update sprint summary
    #update_sprint_summary(jira, "sprint_id", "New Summary", "state", "start_date", "end_date")

    # Sprint report
   # sprint_report(jira, "sprint_id", project_key)

    # Delete a sprint
    #delete_sprint(jira, "sprint_id")

    # Get velocity
   # get_velocity(jira, project_key)

    # Get sprints for board
   # get_sprints_for_board(jira, board_id)
     # Create an Epic
    #epic = create_epic(jira, "JE", "TEST EPIC", "THIS IS A TEST EPIC.")
     # List all Epics in a project
    #epics = list_epics(jira, project_key)
    #if epics:
       # for epic in epics:
           # logging.info(f"Epic Key: {epic.key}, Summary: {epic.fields.summary}")

     # Read the details of a specific Epic
    #epic_key = "JE-123"  # Replace with the actual Epic key
    #read_epic_details(jira, epic_key)
    # Call the update_epic function
    #update_epic(jira, 'JE-123', '1new summary', 'new_description')
    #delete_epic(jira, 'JE-197')
    #add_story_to_epic(jira, 'JE-123', 'JE-47')
    unlink_story_from_epic(jira, 'JE-47')





if __name__ == "__main__":
    main()

