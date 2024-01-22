from jira import JIRA
import matplotlib.pyplot as plt
from datetime import datetime


jira_url =  'https://jtest-vl.atlassian.net'
api_token = "ATATT3xFfGF033NKJ-mORvkUaA4D4vjuoyUeBcZI-Flp5DPvyDVpmBJEHA-ght6aI25vmgemImTniuMOihZvnd1bbWKProU4VJcJNnnq5-1GwVT7txZQOFOB9f8zHL96uKyaK0vhYQni7brR2Tp5ClGEA5jrH1wi1bkZIIvHm1TEJMGYsZrqTMU=D4D623B5"
user = 'admin@jtest.verituslabs.com'
jira = JIRA(server=jira_url, basic_auth=(user, api_token))
# Get a list of all projects
def get_list_of_all_projects(): 
    projects = jira.projects()
    return {project.key:project.name for project in projects}
print(get_list_of_all_projects())

#Get list of all stories in a project
def print_stories(project_key):
    issues = jira.search_issues(f'project = {project_key} AND issuetype = Story')
    for issue in issues:
        print(f"Story Key: {issue.key}, Summary: {issue.fields.summary}")
print_stories('JE')

#Get report of specific sprint
def print_sprint_details(jira, project_key, sprint_id):
    # Get detailed information about the sprint
    sprint_info = jira.sprint(sprint_id)

    if not sprint_info:
        print(f"Sprint with ID {sprint_id} not found.")
        return

    # Print all details of the sprint
    print("Sprint Details:")
    for key, value in sprint_info.raw.items():
        print(f"{key}: {value}")

    # Define the JQL query to search for issues of type 'Story' in a specific sprint
    jql_query = f'project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}'

    # Search for issues using the JQL query
    issues = jira.search_issues(jql_query)

    # Count issue statuses
    status_counts = {'To Do': 0, 'In Progress': 0, 'Done': 0}
    for issue in issues:
        status = issue.fields.status.name
        if status in status_counts:
            status_counts[status] += 1

        # Print details of each story in the sprint
        print("\nIssue Details:")
        print(f"Issue Key: {issue.key}")
        print(f"Summary: {issue.fields.summary}")
        print(f"Status: {issue.fields.status.name}")

        # Handle Assignee
        assignee = getattr(issue.fields, 'assignee', {})
        assignee_display_name = assignee.get('displayName', 'Unassigned') if isinstance(assignee, dict) else 'Unassigned'
        print(f"Assignee: {assignee_display_name}")

        # Handle Reporter
        reporter = getattr(issue.fields, 'reporter', {})
        reporter_display_name = reporter.get('displayName', 'N/A') if isinstance(reporter, dict) else 'N/A'
        print(f"Reporter: {reporter_display_name}")

        # Handle Created Date
        created_date = issue.fields.created
        created_date_str = datetime.strptime(created_date, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S")
        print(f"Created Date: {created_date_str}")

        # Handle Updated Date
        updated_date = issue.fields.updated
        updated_date_str = datetime.strptime(updated_date, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S")
        print(f"Updated Date: {updated_date_str}")

    # Plot a bar chart
    labels = status_counts.keys()
    counts = status_counts.values()

    plt.bar(labels, counts, color=['orange', 'yellow', 'green'])
    plt.title('Issue Status Distribution in Sprint')
    plt.xlabel('Status')
    plt.ylabel('Number of Issues')
    plt.show()

# Example usage
print_sprint_details(jira, 'JE', '1')