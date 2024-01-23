from jira import JIRA
from datetime import datetime
import yaml
from pathlib import Path
import matplotlib.pyplot as plt

# Function to get specific sprint report
def get_sprint_details(jira_url, jira_username, api_token, project_key, sprint_id):
    # Create a Jira connection
    jira = JIRA(server=jira_url, basic_auth=(jira_username, api_token))

    # Get detailed information about the sprint
    sprint_info = jira.sprint(sprint_id)

    if not sprint_info:
        return {"error": f"Sprint with ID {sprint_id} not found."}

    # JQL query to search for issues of type 'Story' in a specific sprint
    jql_query = f'project = {project_key} AND issuetype = Story AND Sprint = {sprint_id}'

    # Search for issues using the JQL query
    issues = jira.search_issues(jql_query)

    # Count issue statuses
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

    sprint_details = {
        "Sprint Details": sprint_info.raw,
        "Issue Status Distribution": status_counts,
        "Issue Details": issue_details,
    }

    return sprint_details

# Jira configuration
jira_url = 'https://jtest-vl.atlassian.net'
api_token = "ATATT3xFfGF033NKJ-mORvkUaA4D4vjuoyUeBcZI-Flp5DPvyDVpmBJEHA-ght6aI25vmgemImTniuMOihZvnd1bbWKProU4VJcJNnnq5-1GwVT7txZQOFOB9f8zHL96uKyaK0vhYQni7brR2Tp5ClGEA5jrH1wi1bkZIIvHm1TEJMGYsZrqTMU=D4D623B5"
user = 'admin@jtest.verituslabs.com'
project_key = 'JE'
sprint_id = '2'

# Get specific sprint report
jira = JIRA(server=jira_url, basic_auth=(user, api_token))
result = get_sprint_details(jira_url, user, api_token, project_key, sprint_id)

# Save sprint report to YAML file with bar graph
yaml_file_path = Path("sprint_report.yaml")
with yaml_file_path.open(mode="w") as yaml_file:
    # Write Sprint Details
    yaml.dump({"Sprint Details": result["Sprint Details"]}, yaml_file, default_flow_style=False)

    # Write Issue Status Distribution
    yaml.dump({"Issue Status Distribution": result["Issue Status Distribution"]}, yaml_file, default_flow_style=False)

    # Write Issue Details
    yaml.dump({"Issue Details": result["Issue Details"]}, yaml_file, default_flow_style=False)

# Plot a bar chart
labels = result["Issue Status Distribution"].keys()
counts = result["Issue Status Distribution"].values()
plt.bar(labels, counts, color=['orange', 'yellow', 'green'])
plt.title('Issue Status Distribution in Sprint')
plt.xlabel('Status')
plt.ylabel('Number of Issues')
plt.savefig('sprint_status_distribution.png')
print("Plot saved as 'sprint_status_distribution.png'")
