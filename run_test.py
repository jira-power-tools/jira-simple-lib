
# this file should run a test script to exercise all the functions in 
# jirasimplelib
#
# create a project                              ~~DONE
# create epics: ep-1, ep-2, ep-3                ~~DONE
# create stories s-1 to s-30                    ~~DONE
# move stories s-1 to s-15 to ep-1, s-16 to s-20 to ep-2 an s-21 to s-30 to ep-3  ~~DONE
# create sprints sp-1 to sp-3                   ~~DONE
# add s-1 to s10 to sp-1
# add s-11 to s20 to sp-2
# add s-21 to s30 to sp-3
# start sp-1
# add comments to s-1 to s-15
# get list of stories in sp-1
# move s-10 to s-15 to s-2
# complete all stories in sp-1
# complete sp-1
# start sp-2
# add comment to all stories in sp-2
# delete all stories
# delete all sptrints
# delete all projects
import logging
from jira import JIRA, JIRAError
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='jira_test.log'
)

# Function to create a Jira connection
def create_jira_connection(jira_url, user, api_token):
    try:
        return JIRA(server=jira_url, basic_auth=(user, api_token))
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
        return True
    except JIRAError as e:
        logging.error(f"Error creating project: {e}")
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
def move_issues_to_sprint(jira, start_issue_key, end_issue_key, target_sprint_id):
    for i in range(int(start_issue_key.split('-')[1]), int(end_issue_key.split('-')[1]) + 1):
        issue_key = f"JST-{i}"
        try:
            issue = jira.issue(issue_key)
            jira.add_issues_to_sprint(target_sprint_id, [issue.key])
            logging.info(f"Issue {issue_key} moved to Sprint {target_sprint_id}")
        except Exception as e:
            logging.error(f"Error moving issue {issue_key} to Sprint: {e}")




def main():

    # Jira credentials and parameters
    jira_url = "https://jsl-test.atlassian.net"
    api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
    user = "info@test01.verituslabs.net"
     # Create Jira connection
    jira = create_jira_connection(jira_url, user, api_token)
     # Create the project
    #create_jira_project(jira, 'Jsl-Test', 'JST')

    # Define names and summaries for the epics
    # epic_details = [
      #  {"name": "Test Epic 1", "summary": "This is a test epic 1."},
      #  {"name": "Test Epic 2", "summary": "This is a test epic 2."},
      #  {"name": "Test Epic 3", "summary": "This is a test epic 3."}
   # ]
    # Create 3 epics with different names and summaries
   # for epic_detail in epic_details:
       # epic_name = epic_detail["name"]
       # epic_summary = epic_detail["summary"]
       # create_epic(jira, 'JST', epic_name, epic_summary)
    # Create a new story
    # Create 30 stories
    #for i in range(30):
     #   summary = f"This is a test story {i+1}."
      #  description = f"Test Story {i+1}"
       # new_story = create_story(jira, 'JST', summary, description)
     # Define the mapping between epic keys and story keys
    #epic_story_ranges = {
     #  'JST-1': ['JST-7', 'JST-15'],
      #  'JST-2': ['JST-16', 'JST-25'],
       # 'JST-3': ['JST-23', 'JST-37'],
        # Add more mappings as needed
   # } 
      # Add stories to epics
    #for epic_key, (start_story, end_story) in epic_story_ranges.items():
     #   for story_id in range(int(start_story.split('-')[1]), int(end_story.split('-')[1]) + 1):
      #      story_key = f"JST-{story_id}"
       #     add_story_to_epic(jira, epic_key, story_key)
    # Create three sprints
    #for i in range(1, 4):
     #   sprint_name = f"Sprint {i}"
      #  create_sprint(jira_url, user, api_token, '1', sprint_name)
    # Example usage:
    #move_issues_to_sprint(jira, 'JST-7', 'JST-15', '1')
    move_issues_to_sprint(jira, 'JST-16', 'JST-25', '2')
    move_issues_to_sprint(jira, 'JST-26', 'JST-37', '3')







if __name__ == "__main__":
    main()

