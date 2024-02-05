
# this file should run a test script to exercise all the functions in 
# jirasimplelib
#
# create a project
# create epics: ep-1, ep-2, ep-3
# create stories s-1 to s-30
# move stories s-1 to s-15 to ep-1, s-16 to s-20 to ep-2 an s-21 to s-30 to ep-3
# create sprints sp-1 tp sp-3
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

def main():

        # Jira credentials and parameters
    jira_url = "https://jsl-test.atlassian.net/jira/your-work"
    api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
    user = "info@test01.verituslabs.net"


if __name__ == "__main__":
    main()

