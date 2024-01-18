from jira import JIRA
import matplotlib.pyplot as plt


jira_url =  'https://jtest-vl.atlassian.net'
api_token = "ATATT3xFfGF033NKJ-mORvkUaA4D4vjuoyUeBcZI-Flp5DPvyDVpmBJEHA-ght6aI25vmgemImTniuMOihZvnd1bbWKProU4VJcJNnnq5-1GwVT7txZQOFOB9f8zHL96uKyaK0vhYQni7brR2Tp5ClGEA5jrH1wi1bkZIIvHm1TEJMGYsZrqTMU=D4D623B5"
user = 'admin@jtest.verituslabs.com'
jira = JIRA(server=jira_url, basic_auth=(user, api_token))
issue_key = 'JE-2'
issue = jira.issue(issue_key)
print(f"Issue Key: {issue.key}, Summary: {issue.fields.summary}")


def get_list_of_all_projects():
    # Get a list of all projects
    projects = jira.projects()

    return {project.key:project.name for project in projects}



print(get_list_of_all_projects())