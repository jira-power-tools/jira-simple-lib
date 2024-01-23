from jira import JIRA
import matplotlib.pyplot as plt
from datetime import datetime
from pprint import pprint


# Get a list of all projects
def get_list_of_all_projects(jira_url, user, api_token): 
    jira_instance = JIRA(server=jira_url, basic_auth=(user, api_token))
    projects = jira_instance.projects()
    return {project.key: project.name for project in projects}
# Example usage:
jira_url = 'https://jtest-vl.atlassian.net'
api_token = "ATATT3xFfGF033NKJ-mORvkUaA4D4vjuoyUeBcZI-Flp5DPvyDVpmBJEHA-ght6aI25vmgemImTniuMOihZvnd1bbWKProU4VJcJNnnq5-1GwVT7txZQOFOB9f8zHL96uKyaK0vhYQni7brR2Tp5ClGEA5jrH1wi1bkZIIvHm1TEJMGYsZrqTMU=D4D623B5"
user = 'admin@jtest.verituslabs.com'

result = get_list_of_all_projects(jira_url, user, api_token)
print(result)
#Get specific Sprint report


def get_sprint_details(jira_url, jira_username, api_token, project_key, sprint_id):

    # Create a Jira connection
    jira = JIRA(server=jira_url, basic_auth=(jira_username, api_token))

    # Get detailed information about the sprint
    sprint_info = jira.sprint(sprint_id)

    if not sprint_info:
        return {"error": f"Sprint with ID {sprint_id} not found."}



#update status of specific story
def transition_jira_issue(issue_key, target_status, jira_url, jira_username, api_token):
    # Create a Jira connection
    jira = JIRA(server=jira_url, basic_auth=(jira_username, api_token))
    transitions = jira.transitions(issue_key)
    transition_id = None
    for transition in transitions:
        if transition['to']['name'] == target_status:
            transition_id = transition['id']
            break
    if transition_id:
        try:
            jira.transition_issue(issue_key, transition_id)
            print(f"Issue {issue_key} transitioned to status '{target_status}'")
        except Exception as e:
            print(f"Error transitioning issue {issue_key}: {str(e)}")
    else:
        print(f"Target status '{target_status}' not found for the specified issue")
issue_key = 'JE-25'
target_status = 'Done'
transition_jira_issue(issue_key, target_status, jira_url, user, api_token)
#Get specific sprint report
def get_sprint_details(jira, project_key, sprint_id):
    sprint_details = {}
    sprint_info = jira.sprint(sprint_id)
    if not sprint_info:
        sprint_details["error"] = f"Sprint with ID {sprint_id} not found."
        return sprint_details
    sprint_details["Sprint Details"] = sprint_info.raw
    jql_query = f'project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}'
    issues = jira.search_issues(jql_query)
    status_counts = {'To Do': 0, 'In Progress': 0, 'Done': 0}
    issue_details = []
    for issue in issues:
        status = issue.fields.status.name
        if status in status_counts:
            status_counts[status] += 1
        assignee = getattr(issue.fields, 'assignee', None)
        assignee_display_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
        reporter_display_name = getattr(getattr(issue.fields, 'reporter', None), 'displayName', 'N/A')
        issue_details.append({
            "Issue Key": issue.key,
            "Summary": issue.fields.summary,
            "Status": issue.fields.status.name,
            "Assignee": assignee_display_name,
            "Reporter": reporter_display_name,
            "Created Date": datetime.strptime(issue.fields.created, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S"),
            "Updated Date": datetime.strptime(issue.fields.updated, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d %H:%M:%S"),
        })
    sprint_details["Issue Details"] = issue_details
    sprint_details["Issue Status Distribution"] = status_counts
    return sprint_details

jira_url = 'https://jtest-vl.atlassian.net'
api_token = "ATATT3xFfGF033NKJ-mORvkUaA4D4vjuoyUeBcZI-Flp5DPvyDVpmBJEHA-ght6aI25vmgemImTniuMOihZvnd1bbWKProU4VJcJNnnq5-1GwVT7txZQOFOB9f8zHL96uKyaK0vhYQni7brR2Tp5ClGEA5jrH1wi1bkZIIvHm1TEJMGYsZrqTMU=D4D623B5"
user = 'admin@jtest.verituslabs.com'
project_key = 'JE'
sprint_id = '2'
jira = JIRA(server=jira_url, basic_auth=(user, api_token))
result = get_sprint_details(jira, project_key, sprint_id)
pprint(result)

# Plot a bar chart
labels = result["Issue Status Distribution"].keys()
counts = result["Issue Status Distribution"].values()
plt.bar(labels, counts, color=['orange', 'yellow', 'green'])
plt.title('Issue Status Distribution in Sprint')
plt.xlabel('Status')
plt.ylabel('Number of Issues')
plt.show()
