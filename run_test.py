
# this file should run a test script to exercise all the functions in 
# jirasimplelib
#
# create a project                              ~~DONE
# create epics: ep-1, ep-2, ep-3                ~~DONE
# create stories s-1 to s-30                    ~~DONE
# move stories s-1 to s-15 to ep-1, s-16 to s-20 to ep-2 an s-21 to s-30 to ep-3  ~~DONE
# create sprints sp-1 to sp-3                   ~~DONE
# add s-1 to s10 to sp-1                        ~~DONE
# add s-11 to s20 to sp-2                       ~~DONE
# add s-21 to s30 to sp-3                       ~~DONE
# start sp-1                                    ~~DONE
# add comments to s-1 to s-15                   ~~DONE
# get list of stories in sp-1                   ~~DONE
# move s-10 to s-15 to s-2                      ~~DONE
# complete all stories in sp-1                  ~~DONE
# complete sp-1                                 ~~DONE
# start sp-2                                    ~~DONE
# add comment to all stories in sp-2            ~~DONE
# delete all stories                            ~~DONE
# delete all sptrints                           ~~DONE
from datetime import datetime
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
        return project
    except JIRAError as e:
        logging.error(f"Error creating project: {e}")
        return None
    except Exception as e:
        logging.error(f"Error creating project: {e}")
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
    except JIRAError as e:
        logging.error(f"Error deleting stories in project: {e}")
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






def main():

    # Jira credentials and parameters
    jira_url = "https://jsl-test.atlassian.net"
    api_token = "ATATT3xFfGF0h7m9HE3DQGsJ_XQ1TbSYSKxCHlvuRHX0cFWuST5ANEM5UyX5AkWVzGBWDpOXAXJo7Kk4G3ulCJpB3AWEJMELIsdiyYj80Z_13Lv165GZMR7MelDtDKS9AJ0VW0GJCw1PJXbpxY2i46VbtTvGekTLCvFA5PjHsPrNB6uC3yXK8wM=1E97E388"
    user = "info@test01.verituslabs.net"
     # Create Jira connection
    jira = create_jira_connection(jira_url, user, api_token)
     # Create the project
    #create_jira_project(jira, 'DemoProject2', 'D2')

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
    # Create three sprints6
    
    #for i in range(1, 4):
     #   sprint_name = f"Sprint {i}"
    sprint_name = 'new sprint'
    create_sprint(jira_url, user, api_token, '2', sprint_name)
    # Example usage:
    #move_issues_to_sprint(jira, 'JST-7', 'JST-15', '1')
   # move_issues_to_sprint(jira, 'JST-16', 'JST-25', '2')
   # move_issues_to_sprint(jira, 'JST-26', 'JST-37', '3')
        # Start the specified sprint
     #start_sprint(jira, '1', 'Sprint 11', '2024-02-06T00:00:00.000+0000', '2024-02-29T23:59:59.999+0000')
   # add_comment_to_issues_in_range(jira, 16, 25, 'this is a second test comment.')
    #story_keys = get_stories_in_sprint(jira, '1')
   # move_issues_to_sprint(jira, 'JST-7', 'JST-15', '1')
    #complete_stories_in_sprint(jira, '1')
   # complete_sprint(jira, '1','2024-02-06T00:00:00.000+0000','2024-02-29T23:59:59.999+0000')
    #start_sprint(jira, '2', 'Sprint 12', '2024-02-06T00:00:00.000+0000', '2024-02-29T23:59:59.999+0000')
    #delete_all_stories_in_project(jira,'JST')
    #delete_all_sprints(jira,'1')
    #delete_all_projects(jira)








if __name__ == "__main__":
    main()

