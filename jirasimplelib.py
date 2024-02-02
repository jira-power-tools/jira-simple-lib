from jira import JIRA, JIRAError
import requests

# Function to create a Jira connection
def create_jira_connection(jira_url, user, api_token):
    return JIRA(server=jira_url, basic_auth=(user, api_token))

# Function to create a new story in Jira
def create_story(jira, project_key, summary, description, goal):
    try:
        new_story = jira.create_issue(
            project=project_key,
            summary=summary,
            description=description,
            #customfield_10030=goal,  # Using custom field 'Total forms' for story goal
            issuetype={'name': 'Story'},
        )
        print(f"Story created successfully. Story Key: {new_story.key}")
        return new_story
    except JIRAError as e:
        print(f"Error creating story: {e}")
        return None

# Function to read a story's details
def read_story_details(jira, story_key):
    try:
        story = jira.issue(story_key)
        print(f"Key: {story.key}")
        print(f"Summary: {story.fields.summary}")
        print(f"Description: {story.fields.description}")
        print(f"Status: {story.fields.status.name}")

        # Check if assignee is set before accessing displayName
        if story.fields.assignee:
            print(f"Assignee: {story.fields.assignee.displayName}")
        else:
            print("Assignee: Unassigned")

        # Check if reporter is set before accessing displayName
        if story.fields.reporter:
            print(f"Reporter: {story.fields.reporter.displayName}")
        else:
            print("Reporter: Unassigned")

        print(f"Created: {story.fields.created}")
        print(f"Updated: {story.fields.updated}")

    except JIRAError as e:
        print(f"Error reading story: {e}")

# Function to update a story's summary
def update_story_summary(jira, story_key, new_summary):
    try:
        story = jira.issue(story_key)
        story.update(summary=new_summary)
        print(f"Story summary updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        print(f"Error updating story summary: {e}")
        return None


# Function to update a story's description
def update_story_description(jira, story_key, new_description):
    try:
        story = jira.issue(story_key)
        story.update(description=new_description)
        print(f"Story description updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        print(f"Error updating story description: {e}")
        return None


# Function to update a story's status
def update_story_status(jira, story_key, new_status):
    try:
        story = jira.issue(story_key)
        transitions = jira.transitions(story)
        for transition in transitions:
            if transition['to']['name'] == new_status:
                jira.transition_issue(story, transition['id'])
                print(f"Story status updated successfully. Key: {story_key}")
                return story
        print(f"Invalid status: {new_status}")
        return None
    except JIRAError as e:
        print(f"Error updating story status: {e}")
        return None

# Function to update a story's assignee
def update_story_assignee(jira, story_key, new_assignee):
    try:
        story = jira.issue(story_key)
        story.update(assignee={'name': new_assignee})
        print(f"Story assignee updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        print(f"Error updating story assignee: {e}")
        return None

# Function to update a story's reporter
def update_story_reporter(jira, story_key, new_reporter):
    try:
        story = jira.issue(story_key)
        story.update(reporter={'name': new_reporter})
        print(f"Story reporter updated successfully. Key: {story_key}")
        return story
    except JIRAError as e:
        print(f"Error updating story reporter: {e}")
        return None

# Function to delete a story
def delete_story(jira, story_key):
    try:
        issue = jira.issue(story_key)
        issue.delete()
        print(f"Story deleted successfully. Key: {story_key}")
        return True
    except JIRAError as e:
        print(f"Error deleting story: {e}")
        return False
# Function to create a new sprint
def create_sprint(jira_url, jira_username, api_token, board_id, sprint_name):
    # API endpoint for creating a new sprint
    create_sprint_api_url = f'{jira_url}/rest/agile/1.0/sprint'

    # HTTP Basic Authentication
    auth = (jira_username, api_token)

    # Sprint details
    sprint_data = {
        "name": sprint_name,
        "originBoardId": board_id,
    }

    # Send a POST request to create the sprint
    response_create_sprint = requests.post(create_sprint_api_url, json=sprint_data, auth=auth)

    # Check the response status for creating the sprint
    if response_create_sprint.status_code == 201:
        created_sprint_data = response_create_sprint.json()
        sprint_id = created_sprint_data.get('id')
        print(f"New Sprint created with ID: {sprint_id}")
        return sprint_id
    else:
        print(f"Failed to create a new Sprint. Status code: {response_create_sprint.status_code}, Error: {response_create_sprint.text}")
        return None
def update_sprint_summary(jira, sprint_id, new_summary, sprint_state, start_date, end_date):
    try:
        sprint = jira.sprint(sprint_id)
        sprint.update(name=new_summary, state=sprint_state, startDate=start_date, endDate=end_date)
        print(f"Sprint summary updated successfully. ID: {sprint_id}")
        return sprint
    except JIRAError as e:
        print(f"Error updating sprint summary: {e}")
        return None
#sprint report
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
    #delete a sprint
def delete_sprint(jira, sprint_id):
    try:
        sprint = jira.sprint(sprint_id)
        sprint.delete()
        print(f"Sprint with ID {sprint_id} deleted successfully.")
        return True
    except JIRAError as e:
        print(f"Error deleting sprint: {e}")
        return False



# Driver function
def main():
    jira_url = 'https://jtest-vl.atlassian.net'
    api_token = 'ATATT3xFfGF0XxgsYvdpyIsMnMOeE9CdUPu75dO7Kh03II60Cg5KYf4d41LTubrshQFmTVCo24mxyYd07-flBqd6DIQHvuKdkWGDrlohGhNMew_hCMqTjgnaPnj2NYCXv4PtzxdzjNq8Vi0vg3NzJcFAQivkuvDjPVnqAs-BdN9PAHfSwGCYex8=7C73D52A'
    user = 'rimsha.ashfaq@verituslabs.com'
    jira = create_jira_connection(jira_url, user, api_token)
    project_key = 'JE'
    story_key = 'JE-187'
    board_id = '2'
    sprint_name = "Sprint test"
    sprint_goal = "Complete feature X"


    # Create a new story
    #new_story = create_story(jira, project_key, "Test Story", "This is a test story.", "Goal of the story")

    # Read the newly created story
    #story = read_story_details(jira, story_key)

    # Update the story with new summary
    #story = update_story_summary(jira, story_key, "Updated Test Story")

    # Update the story with new description
    #story = update_story_description(jira, story_key, "This is an updated test story.")

    # Update the story with new status
    #story = update_story_status(jira, story_key, "In Progress")

    # Update the story with new assignee
    #story = update_story_assignee(jira, story_key, "Arman")
  
    # Update the story with new reporter
    #story = update_story_reporter(jira, story_key, "Arman Anwar")

    # Delete the story
    #delete_story(jira, story_key)
    #sprint = create_sprint(jira_url, user, api_token, board_id, sprint_name)
    #updated_sprint_summary = update_sprint_summary(jira, "2", "2New summary", "future", "2024-01-30","2024-02-10")
    sprint_report(jira, "2", "JE")
    #delete_sprint(jira, "6")

if __name__ == "__main__":
    main()
