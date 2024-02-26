
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
            jira_url = config_data['jira_url']
            user = config_data['user']
            api_token = config_data['api_token']

            jira = JIRA(
                basic_auth=(user, api_token),
                options={'server': jira_url}
            )
            logging.info("Jira connection established successfully.")
            return jira
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
def delete_epic(jira, epic_key):
    try:
        issue = jira.issue(epic_key)
        issue.delete()
        logging.info(f"Epic deleted successfully. Key: {epic_key}")
        return True
    except JIRAError as e:
        logging.error(f"Error deleting epic: {e}")
        return False
# Function to list all Epics in a project
def list_epics(jira, project_key):
    try:
        jql_query = f"project = {project_key} AND issuetype = Epic"
        epics = jira.search_issues(jql_query)
        return epics
    except Exception as e:
        logging.error(f"Error listing epics: {e}")
        return None
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


def parse_arguments():
    parser = argparse.ArgumentParser(description='Jira CLI Tool')
    parser.add_argument('--config', help='Path to the configuration file', default='default_config.txt')
    return parser.parse_args()

# Define function to display the menu
def display_menu():
    logging.info("Choose an option:")
    logging.info("1: Create Jira Project ()")
    logging.info("2: Create Epic")
    logging.info("3: Delete Epic")
    logging.info("4: Create Story")
    logging.info("5: Add Story to Epic")
    logging.info("6: Create Sprint")
    logging.info("7: Move Issues to Sprint")
    logging.info("8: Start Sprint")
    logging.info("9: Add Comments to Issues in Range")
    logging.info("10: Get Stories in Sprint")
    logging.info("11: Complete Stories in Sprint")
    logging.info("12: Complete Sprint")
    logging.info("13: Delete All Stories in Project")
    logging.info("14: Delete All Sprints")
    logging.info("15: Delete All Projects")
    logging.info("16: List All Epics")
    logging.info("17: List All stories in a project")
    logging.info("18: Create board")
    logging.info("19: update Epic")
    logging.info("20: Read Epic")
    logging.info("21: Update project information")
    logging.info("22: Get board id ")
    logging.info("23: Exit")
# Define function to parse user input
def get_user_input():
    try:
        choice = int(input("Enter the function number (1-23): "))
        if 1 <= choice <= 23:
            return choice
        else:
            logging.error("Invalid choice. Please enter a number between 1 and 23.")
            return get_user_input()
    except ValueError:
        logging.error("Invalid input. Please enter a number.")
        return get_user_input()

def main():   
   # Parse command-line arguments
    args = parse_arguments()
    # Create Jira connection
    jira = create_jira_connection(args.config)
    if not jira:
        return

    while True:
        display_menu()
        choice = get_user_input()

        if choice == 1:
            project_name = input("Enter project name: ")
            project_key = input("Enter project key: ")
            create_jira_project(jira, project_name, project_key)
        elif choice == 2:
            project_key = input("Enter project key: ")
            num_epics = int(input("Enter the number of epics to create (1 or more): "))
            epic_details = []
            for i in range(num_epics):
                epic_name = input(f"Enter epic name for epic {i+1}: ")
                epic_summary = input(f"Enter epic summary for epic {i+1}: ")
                create_epic(jira, project_key, epic_name, epic_summary)
        elif choice == 3:
            delete_choice = input("Do you want to delete any epics? (yes/no): ").lower()
            if delete_choice == "yes":
                delete_option = input("Choose the deletion option (single/range/all): ").lower()
                
                if delete_option == "single":
                    epic_key = input("Enter the key of the epic to delete: ")
                    delete_epic(jira, epic_key)
                
                elif delete_option == "range":
                    range_input = input("Enter the range of epic keys to delete (e.g., 'np1-2,np1-5'): ")
                    epic_keys = [key.strip() for key in range_input.split(',')]
                    for epic_key in epic_keys:
                        delete_epic(jira, epic_key)
                
                elif delete_option == "all":
                    project_key = input("Enter the project key: ")
                    epics = list_epics(jira, project_key)
                    if epics:
                        for epic in epics:
                            delete_epic(jira, epic.key)
                    else:
                        print("Failed to retrieve epic list. No epics deleted.")
                else:
                    print("Invalid option. Please choose 'single', 'range', or 'all'.")    
        elif choice == 4:            
            project_key = input("Enter project key: ")
            num_stories = int(input("Enter the number of stories to create: "))
            stories = []
            for i in range(num_stories):
                print(f"Entering details for Story {i+1}:")
                summary = input("Enter story summary: ")
                description = input("Enter story description: ")
                stories.append({"summary": summary, "description": description})
            for story in stories:
                create_story(jira, project_key, story["summary"], story["description"])
        elif choice == 5:
            project_key = input("Enter project key: ")
            epic_key = input("Enter epic key: ")           
            add_option = input("Choose the option to add stories to the epic (single/range/all): ").lower()
            if add_option == "single":
                story_key = input("Enter the key of the story to add to the epic: ")
                add_story_to_epic(jira, epic_key, story_key)           
            elif add_option == "range":
                range_input = input("Enter the range of story keys to add (e.g., 'NP1-14,NP1-16'): ")
                start_story, end_story = map(str.strip, range_input.split(','))
                for i in range(int(start_story.split('-')[1]), int(end_story.split('-')[1]) + 1):
                    story_key = f"{start_story.split('-')[0]}-{i}"
                    add_story_to_epic(jira, epic_key, story_key)                   
            elif add_option == "all":
                num_stories = int(input("Enter the total number of stories: "))
                for i in range(num_stories):
                    story_key = input(f"Enter the key of story {i+1} to add to the epic: ")
                    add_story_to_epic(jira, epic_key, story_key)
            else:
                print("Invalid option. Please choose 'single', 'range', or 'all'.")
        elif choice == 6:
             # Jira credentials and parameters
            jira_url = "https://jirasimplelib.atlassian.net"
            api_token = "ATATT3xFfGF0fw-ydjB26YylvNBhO2Xw9Wy2bHnEbU30EnIVxVbl1zP9ZACOcAj5Q1A7bF7Y8qhSYgeZ75Krct58L_6LHcWg3jTYJ-uTAS1e6F3RcC6AP9mWIzr6axZcXExFWSDBp5rPU6MECMuZIQHkqi2ai0Z60ihzXRxLUgnEHE-fMFyPH7g=AF5B8618"
            user = "info@jiratest003.verituslabs.net"
            sprint_name = 'new sprint'
            create_sprint(jira_url, user, api_token, '1', sprint_name)
        elif choice == 7:
            project_key = input("Enter the project key: ")
            start_issue_number = input("Enter the start issue number: ")
            end_issue_number = input("Enter the end issue number: ")
            target_sprint_id = input("Enter spritn id :")
            # Assuming you have initialized 'jira' somewhere in your code
            move_issues_to_sprint(jira, project_key, start_issue_number, end_issue_number, target_sprint_id)
        elif choice == 8:
          pass
        elif choice == 9:
            start_issue_num = input("Enter start issue number: ")
            end_issue_num = input("Enter end issue number: ")
            comment_body = input("Enter comment body: ")
            add_comment_to_issues_in_range(jira, start_issue_num, end_issue_num, comment_body)
        elif choice == 10:
            sprint_id = input("Enter sprint ID: ")
            get_stories_in_sprint(jira, sprint_id)
        elif choice == 11:
            sprint_id = input("Enter sprint ID: ")
            complete_stories_in_sprint(jira, sprint_id)
        elif choice == 12:
            sprint_id = input("Enter sprint ID: ")
            start_date = input("Enter start date: ")
            end_date = input("Enter end date: ")
            complete_sprint(jira, sprint_id, start_date, end_date)
        elif choice == 13:
            project_key = input("Enter project key: ")
            delete_all_stories_in_project(jira, project_key)
        elif choice == 14:
            board_id = input("Enter board ID: ")
            delete_all_sprints(jira, board_id)
        elif choice == 15:
            delete_all_projects(jira)
        elif choice == 16:
            project_key = input("Enter project key: ")
            epics = list_epics(jira, project_key)
            if epics:
                for epic in epics:
                  logging.info(f"Epic Key: {epic.key}, Summary: {epic.fields.summary}")
        elif choice == 17 :
           project_key = input("Enter project key: ")
           stories = get_stories_for_project(jira, project_key)
           if stories:
                print("List of stories:")
                for story in stories:
                    print(f"Key: {story['key']}, Summary: {story['summary']}")
           else:
                print("No stories found for the project.")
        elif choice == 18 :
            pass
            # jira_url : "https://jirasimplelib.atlassian.net"
            # api_token :"ATATT3xFfGF0fw-ydjB26YylvNBhO2Xw9Wy2bHnEbU30EnIVxVbl1zP9ZACOcAj5Q1A7bF7Y8qhSYgeZ75Krct58L_6LHcWg3jTYJ-uTAS1e6F3RcC6AP9mWIzr6axZcXExFWSDBp5rPU6MECMuZIQHkqi2ai0Z60ihzXRxLUgnEHE-fMFyPH7g=AF5B8618"
            # user_email :"info@jiratest003.verituslabs.net"
            # project_key = "JSL"
            # project_lead = "Jira Test 001"
            # create_board(jira_url, api_token, user_email, project_key, project_lead)
        elif choice == 19 :
            epic_key = input("Enter epic key :")
            new_summary = input("Enter new summary :")
            new_description = input("Enter new description:")
            update_epic(jira, epic_key, new_summary, new_description)
        elif choice == 20 :
             epic_key = input("Enter epic key :")
             read_epic_details(jira, epic_key)
        elif choice == 21 :
            project_key = input("Enter projects key :")
            new_name = input("Enter new name :")
            new_key = input("Enter new key :")
            update_jira_project(jira, project_key, new_name, new_key)
        elif choice == 22 :
            board_name = input("Enter board name :")
            board_id = get_board_id(jira, board_name)
            if board_id:
                logging.info(f"The Board ID of '{board_name}' is: {board_id}")
        elif choice == 23 :
            break
        else:
            logging.error("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


