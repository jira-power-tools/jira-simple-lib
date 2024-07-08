import unittest
from builtins import input  # to mock input function
from requests.models import Response
from unittest.mock import patch, mock_open,MagicMock, call
import os,logging,jsl,requests, json
from jsl import (
    JIRAError,
    read_config,update_story_assignee,
    create_jira_connection,
    create_jira_project,get_assignee,
    update_jira_project,list_projects,
    list_stories_for_project,delete_project,
    create_story,
    update_story_summary,
    update_story_status,
    update_story_description,
    add_comment,
    get_story_details,
    delete_story,
    create_epic,
    update_epic,
    get_epic_details,
    add_issues_to_epic,
    unlink_story_from_epic,
    delete_epic,
    list_epics,
    create_sprint,
    move_all_issues_to_sprint,
    move_single_issue_to_sprint,
    move_issues_in_range_to_sprint,
    start_sprint,
    list_stories_in_sprint,
    complete_stories_in_sprint,
    complete_sprint,
    list_sprints,
    update_sprint_summary,
    get_sprint_details,
    delete_sprint,
    delete_all_sprints,
    get_board_id,
)


class TestReadConfig(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_read_config(self, mock_open):
        # Call the function being tested
        config = read_config('test_config.json')
        
        # Check if the function returns the expected result
        self.assertEqual(config, {'key': 'value'})
        # Check if the open function was called with the correct file name
        mock_open.assert_called_once_with('test_config.json', 'r')


class TestInitialize(unittest.TestCase):
    @patch('jsl.load_credentials')
    @patch('jsl.set_environment_variables')
    def test_initialize_with_existing_config(self, mock_set_env_vars, mock_load_credentials):
        config_file = 'existing_config.json'
        # Mocking the existence of the config file
        os.path.exists = MagicMock(return_value=True)
        # Mocking the credentials loading
        mock_load_credentials.return_value = {"jira_url": "example.com", "user": "user", "api_token": "token"}

        # Call the function being tested
        jsl.initialize(config_file)
        
        # Check if the load_credentials and set_environment_variables functions were called
        mock_load_credentials.assert_called_once_with(config_file)
        mock_set_env_vars.assert_called_once_with({"jira_url": "example.com", "user": "user", "api_token": "token"})

    @patch('jsl.get_user_credentials', return_value=("example.com", "user", "token"))
    @patch('jsl.save_credentials_to_config')
    @patch('jsl.set_environment_variables')
    @patch('builtins.input', return_value='y')
    def test_initialize_without_existing_config(self, mock_input, mock_set_env_vars, mock_save_to_config, mock_get_user_credentials):
        config_file = 'nonexistent_config.json'
        # Mocking the absence of the config file
        os.path.exists = MagicMock(return_value=False)

        # Call the function being tested
        jsl.initialize(config_file)
        
        # Check if the get_user_credentials, save_credentials_to_config, and set_environment_variables functions were called
        mock_get_user_credentials.assert_called_once()
        mock_save_to_config.assert_called_once_with(config_file, "example.com", "user", "token")
        mock_set_env_vars.assert_called_once_with({"jira_url": "example.com", "user": "user", "api_token": "token"})
        
class TestSetEnvironmentVariables(unittest.TestCase):
    def test_set_environment_variables(self):
        # Prepare test data
        credentials = {"jira_url": "example.com", "user": "user", "api_token": "token"}

        # Call the function being tested
        jsl.set_environment_variables(credentials)

        # Check if the environment variables are set correctly
        self.assertEqual(os.environ["JIRA_URL"], "example.com")
        self.assertEqual(os.environ["API_TOKEN"], "token")
        self.assertEqual(os.environ["USER"], "user")
        

class TestLoadCredentials(unittest.TestCase):
    @patch('jsl.open', new_callable=mock_open, read_data='{"username": "test_user", "password": "test_pass"}')
    def test_load_credentials(self, mock_open):
        # Call the function being tested
        credentials = jsl.load_credentials('test_credentials.json')
        
        # Check if the function returns the expected result
        self.assertEqual(credentials, {'username': 'test_user', 'password': 'test_pass'})
        # Check if the open function was called with the correct file name
        mock_open.assert_called_once_with('test_credentials.json', 'r')
        
class TestGetUserCredentials(unittest.TestCase):
    @patch('builtins.input', side_effect=['example.com', 'test_user', 'test_token'])
    def test_get_user_credentials(self, mock_input):
        # Call the function being tested
        jira_url, username, api_token = jsl.get_user_credentials()
        
        # Check if the function returns the expected result
        self.assertEqual(jira_url, 'example.com')
        self.assertEqual(username, 'test_user')
        self.assertEqual(api_token, 'test_token')
        # Check if input was called the expected number of times with the correct prompts
        expected_prompts = ["Enter Jira URL: ", "Enter username: ", "Enter API token: "]
        for i, prompt in enumerate(expected_prompts):
            with self.subTest(i=i, prompt=prompt):
                mock_input.assert_any_call(prompt)
                

class TestCreateJiraConnection(unittest.TestCase):
    @patch('jsl.JIRA')
    @patch('jsl.logging')
    def test_create_jira_connection_success(self, mock_logging, mock_jira):
        # Set up mock behavior for the JIRA constructor
        mock_jira_instance = MagicMock()
        mock_jira.return_value = mock_jira_instance

        # Call the function being tested
        jira_connection = create_jira_connection('https://example.com', 'username', 'api_token')
        
        # Check if the function returns the expected result
        self.assertEqual(jira_connection, mock_jira_instance)
        # Check if the JIRA constructor was called with the correct arguments
        mock_jira.assert_called_once_with(basic_auth=('username', 'api_token'), options={"server": 'https://example.com'})
        # Check if the logging was called with the correct message
        mock_logging.info.assert_called_once_with("Jira connection established successfully.")

    @patch('jsl.logging')
    def test_create_jira_connection_missing_inputs(self, mock_logging):
        # Call the function being tested with missing inputs
        with self.assertRaises(ValueError):
            create_jira_connection('', '', '')

        # Check if the logging was called with the correct message
        mock_logging.error.assert_called_once_with("Missing username, API token, or Jira URL")

    @patch('jsl.JIRA')
    @patch('jsl.logging')
    def test_create_jira_connection_error(self, mock_logging, mock_jira):
        # Set up mock behavior for the JIRA constructor to raise an exception
        mock_jira.side_effect = Exception('Connection error')

        # Call the function being tested
        with self.assertRaises(Exception):
            create_jira_connection('https://example.com', 'username', 'api_token')

        # Check if the logging was called with the correct message
        mock_logging.error.assert_called_once_with("Error creating Jira connection: Connection error")


class TestCreateJiraProject(unittest.TestCase):
    def test_create_project_success(self):
        # Create a mock JIRA client
        jira_mock = MagicMock()
        # Set up mock behavior for the create_project function
        jira_mock.create_project.return_value = {'key': 'PROJECT', 'name': 'Test Project'}
        
        # Call the function being tested
        result = create_jira_project(jira_mock, 'Test Project', 'PROJECT')
        
        # Check if the function returns the expected result
        self.assertEqual(result, {'key': 'PROJECT', 'name': 'Test Project'})
        # Check if the create_project method of the mock was called with the correct arguments
        jira_mock.create_project.assert_called_once_with('PROJECT', 'Test Project')

    def test_create_project_missing_arguments(self):
        # Call the function being tested without providing required arguments
        with self.assertRaises(ValueError):
            create_jira_project(None, None, None)

    def test_create_project_api_error(self):
        # Create a mock JIRA client
        jira_mock = MagicMock()
        # Set up mock behavior for the create_project function to raise an exception
        jira_mock.create_project.side_effect = Exception("API Error")
        
        # Call the function being tested and expect it to raise an exception
        with self.assertRaises(Exception):
            create_jira_project(jira_mock, 'Test Project', 'PROJECT')


class TestUpdateJiraProject(unittest.TestCase):
    @patch('jsl.logging')
    def test_update_jira_project_no_jira_connection(self, mock_logging):
        # Call the function being tested without providing a JIRA client instance
        with self.assertRaises(ValueError):
            update_jira_project(None, 'PROJ', new_name='New Name')

        # Check if logging error was called
        mock_logging.error.assert_called_once_with("Failed to update project: Jira connection not established.")

    @patch('jsl.logging')
    def test_update_jira_project_no_project_key(self, mock_logging):
        # Mock the JIRA client instance
        mock_jira = MagicMock()

        # Call the function being tested without providing a project key
        with self.assertRaises(ValueError):
            update_jira_project(mock_jira, '', new_name='New Name')

        # Check if logging error was called
        mock_logging.error.assert_called_once_with("Failed to update project: Project key not provided.")

    @patch('jsl.logging')
    def test_update_jira_project_no_changes(self, mock_logging):
        # Mock the JIRA client instance
        mock_jira = MagicMock()

        # Call the function being tested with no changes
        with self.assertRaises(ValueError):
            update_jira_project(mock_jira, 'PROJ')

        # Check if logging error was called
        mock_logging.error.assert_called_once_with("Failed to update project: No new name or key provided.")

    @patch('jsl.logging')
    def test_update_jira_project_project_not_found(self, mock_logging):
        # Mock the JIRA client instance
        mock_jira = MagicMock()
        mock_jira.project.return_value = None

        # Call the function being tested with a project that doesn't exist
        result = update_jira_project(mock_jira, 'PROJ', new_name='New Name')

        # Check if the function returns the expected result
        self.assertFalse(result)
        # Check if logging error was called
        mock_logging.error.assert_called_once_with("Project with key 'PROJ' does not exist.")

    @patch('jsl.logging')
    def test_update_jira_project_error_retrieving_project(self, mock_logging):
        # Mock the JIRA client instance
        mock_jira = MagicMock()
        mock_jira.project.side_effect = JIRAError()

        # Call the function being tested with an error retrieving the project
        result = update_jira_project(mock_jira, 'PROJ', new_name='New Name')

        # Check if the function returns the expected result
        self.assertFalse(result)
        # Check if logging error was called
        mock_logging.error.assert_called_once()


class TestListProjects(unittest.TestCase):
    def test_list_projects_success(self):
        # Create mock project objects with key and name attributes
        project1 = MagicMock(key='PROJ1', name='Project 1')
        project2 = MagicMock(key='PROJ2', name='Project 2')
        # Create a mock JIRA client
        jira_mock = MagicMock()
        # Mock the return value of the projects method
        jira_mock.projects.return_value = [project1, project2]
        
        # Call the function being tested
        result = list_projects(jira_mock)
        
        # Check if the function returns the expected result
        self.assertEqual(result, [project1, project2])
        # Check if the projects method of the mock was called
        jira_mock.projects.assert_called_once()

class TestListStoriesForProject(unittest.TestCase):
    def setUp(self):
        self.mock_jira = MagicMock()

    def test_list_stories_for_project_valid(self):
        # Set up mock behavior for the search_issues function
        mock_issue = MagicMock()
        mock_issue.key = 'PROJ-123'
        mock_issue.fields.issuetype.name = 'Story'  # Correcting this line
        mock_issue.fields.status.name = 'To Do'
        mock_issue.fields.assignee.displayName = None
        mock_issue.fields.summary = 'Test story'

        self.mock_jira.search_issues.return_value = [mock_issue]
        
        # Call the function being tested
        result = list_stories_for_project(self.mock_jira, 'PROJ')
        
        # Check if the function returns the expected result
        self.assertEqual(result, [{
            'Issue Type': 'Story',
            'Issue Key': 'PROJ-123',
            'Status': 'To Do',
            'Assignee': None,
            'Summary': 'Test story'
        }])
        # Check if the search_issues method of the mock was called with the correct argument
        self.mock_jira.search_issues.assert_called_once_with('project = PROJ AND issuetype in (Bug, Task, Story)')


class TestCreateStory(unittest.TestCase):
    @patch('jsl.logging')
    def test_create_story_success(self, mock_logging):
        # Mock JIRA client
        jira_mock = MagicMock()
        jira_mock.create_issue.return_value.key = 'PROJ-123'

        # Call create_story with valid inputs
        result = create_story(jira_mock, 'PROJECT', 'Summary', 'Description')

        # Assert that the function returned the expected result
        self.assertEqual(result.key, 'PROJ-123')

        # Assert that logging was called with the expected message
        mock_logging.info.assert_called_once_with('Story created successfully. Story Key: PROJ-123')

    @patch('jsl.logging')
    def test_create_story_missing_inputs(self, mock_logging):
        # Call create_story with missing inputs
        with self.assertRaises(ValueError) as context:
            create_story(None, '', '', '')

        # Assert that the correct ValueError was raised
        self.assertEqual(str(context.exception), 'Jira connection must be provided.')

        # Assert that logging was called with the expected messages
        mock_logging.error.assert_called_with('Failed to create story: Jira connection not established.')
        self.assertEqual(mock_logging.error.call_count, 1)  # Make sure only one error was logged
    @patch('jsl.logging')
    def test_create_story_unexpected_error(self, mock_logging):
        # Mock JIRA client to raise unexpected error
        jira_mock = MagicMock()
        jira_mock.create_issue.side_effect = Exception

        # Call create_story and expect Exception
        with self.assertRaises(Exception):
            create_story(jira_mock, 'PROJECT', 'Summary', 'Description')

        # Assert that logging was called with the expected message
        mock_logging.error.assert_called_once_with('Unexpected error creating story: ')



class TestUpdateStoryStatus(unittest.TestCase):
    def setUp(self):
        # Create a mock Jira client
        self.jira_mock = MagicMock()

    def test_update_story_status_success(self):
        # Set up mock behavior
        self.jira_mock.issue.return_value = MagicMock()
        self.jira_mock.transitions.return_value = [
            {"id": "1", "to": {"name": "Done"}},
            {"id": "2", "to": {"name": "In Progress"}}
        ]

        # Call the function being tested
        result = update_story_status(self.jira_mock, "PROJ-123", "Done")

        # Check if the function returns True on success
        self.assertTrue(result)
        self.jira_mock.transition_issue.assert_called_once_with(self.jira_mock.issue.return_value, "1")

    def test_update_story_status_invalid_status(self):
        # Set up mock behavior
        self.jira_mock.issue.return_value = MagicMock()
        self.jira_mock.transitions.return_value = [
            {"id": "1", "to": {"name": "In Progress"}},
            {"id": "2", "to": {"name": "Review"}}
        ]

        # Call the function being tested
        result = update_story_status(self.jira_mock, "PROJ-123", "Done")

        # Check if the function returns False on invalid status
        self.assertFalse(result)
        self.jira_mock.transition_issue.assert_not_called()

    def test_update_story_status_no_jira_connection(self):
        with self.assertRaises(ValueError):
            update_story_status(None, "PROJ-123", "Done")

    def test_update_story_status_no_issue_key(self):
        with self.assertRaises(ValueError):
            update_story_status(self.jira_mock, "", "Done")

    def test_update_story_status_no_new_status(self):
        with self.assertRaises(ValueError):
            update_story_status(self.jira_mock, "PROJ-123", "")

    def test_update_story_status_jira_error(self):
        self.jira_mock.issue.side_effect = JIRAError("Jira API error")

        with self.assertRaises(JIRAError):
            update_story_status(self.jira_mock, "PROJ-123", "Done")

    def test_update_story_status_unexpected_error(self):
        self.jira_mock.issue.side_effect = Exception("Unexpected error")

        with self.assertRaises(Exception):
            update_story_status(self.jira_mock, "PROJ-123", "Done")



class TestUpdateStorySummary(unittest.TestCase):
    @patch('jsl.logging')
    def test_update_story_summary_success(self, mock_logging):
        jira_mock = MagicMock()
        issue_mock = MagicMock()
        jira_mock.issue.return_value = issue_mock
        result = update_story_summary(jira_mock, 'PROJ-123', 'New summary')
        issue_mock.update.assert_called_once_with(summary='New summary')
        self.assertEqual(result, issue_mock)
        mock_logging.info.assert_called_with('Story summary updated successfully. Key: PROJ-123')

    @patch('jsl.logging')
    def test_update_story_summary_no_jira_connection(self, mock_logging):
        with self.assertRaises(ValueError):
            update_story_summary(None, 'PROJ-123', 'New summary')
        mock_logging.error.assert_called_with("Failed to update story summary: Jira connection not established.")

    @patch('jsl.logging')
    def test_update_story_summary_no_issue_key(self, mock_logging):
        jira_mock = MagicMock()
        with self.assertRaises(ValueError):
            update_story_summary(jira_mock, '', 'New summary')
        mock_logging.error.assert_called_with("Failed to update story summary: Story key not provided.")

    @patch('jsl.logging')
    def test_update_story_summary_no_new_summary(self, mock_logging):
        jira_mock = MagicMock()
        with self.assertRaises(ValueError):
            update_story_summary(jira_mock, 'PROJ-123', '')
        mock_logging.error.assert_called_with("Failed to update story summary: New summary not provided.")

    @patch('jsl.logging')
    def test_update_story_summary_jira_error(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.side_effect = JIRAError("JIRA API error")
        with self.assertRaises(JIRAError):
            update_story_summary(jira_mock, 'PROJ-123', 'New summary')
        mock_logging.error.assert_called()

    @patch('jsl.logging')
    def test_update_story_summary_general_exception(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.side_effect = Exception("General error")
        with self.assertRaises(Exception):
            update_story_summary(jira_mock, 'PROJ-123', 'New summary')
        mock_logging.error.assert_called_with('Unexpected error updating story summary: General error')


class TestUpdateStoryDescription(unittest.TestCase):
    
    @patch('jsl.logging')
    def test_update_story_description_success(self, mock_logging):
        # Create a mock JIRA client
        mock_jira = MagicMock()
        # Create a mock issue
        mock_issue = MagicMock()
        mock_jira.issue.return_value = mock_issue
        
        # Call the function being tested
        issue_key = 'PROJ-123'
        new_description = 'Updated description'
        result = update_story_description(mock_jira, issue_key, new_description)
        
        # Check if the issue was updated with the correct description
        mock_issue.update.assert_called_once_with(description=new_description)
        # Check if the function returns the updated issue
        self.assertEqual(result, mock_issue)
        # Verify logging
        mock_logging.info.assert_called_with(f"Story description updated successfully. Key: {issue_key}")

    @patch('jsl.logging')
    def test_update_story_description_no_jira(self, mock_logging):
        with self.assertRaises(ValueError) as context:
            update_story_description(None, 'PROJ-123', 'Updated description')
        self.assertEqual(str(context.exception), "Jira connection must be provided.")
        mock_logging.error.assert_called_with(
            "Failed to update story description: Jira connection not established."
        )

    @patch('jsl.logging')
    def test_update_story_description_no_issue_key(self, mock_logging):
        mock_jira = MagicMock()
        with self.assertRaises(ValueError) as context:
            update_story_description(mock_jira, '', 'Updated description')
        self.assertEqual(str(context.exception), "Story key must be provided.")
        mock_logging.error.assert_called_with("Failed to update story description: Story key not provided.")

    @patch('jsl.logging')
    def test_update_story_description_no_description(self, mock_logging):
        mock_jira = MagicMock()
        with self.assertRaises(ValueError) as context:
            update_story_description(mock_jira, 'PROJ-123', '')
        self.assertEqual(str(context.exception), "New description must be provided.")
        mock_logging.error.assert_called_with("Failed to update story description: New description not provided.")

    @patch('jsl.logging')
    def test_update_story_description_jira_error(self, mock_logging):
        mock_jira = MagicMock()
        mock_jira.issue.side_effect = JIRAError('Error occurred')
        with self.assertRaises(JIRAError):
            update_story_description(mock_jira, 'PROJ-123', 'Updated description')
        error_message = mock_logging.error.call_args[0][0]
        self.assertIn("Error updating story description", error_message)
        self.assertIn("Error occurred", error_message)

    @patch('jsl.logging')
    def test_update_story_description_unexpected_exception(self, mock_logging):
        mock_jira = MagicMock()
        mock_jira.issue.side_effect = Exception('Unexpected error')
        with self.assertRaises(Exception):
            update_story_description(mock_jira, 'PROJ-123', 'Updated description')
        mock_logging.error.assert_called_with("Unexpected error updating story description: Unexpected error")



class TestUpdateStoryAssignee(unittest.TestCase):

    @patch('jsl.get_user_account_id')
    @patch('requests.put')
    def test_update_story_assignee_success(self, mock_put, mock_get_user_account_id):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = MagicMock()
        mock_get_user_account_id.return_value = 'valid_account_id'
        mock_put.return_value.status_code = 204

        result = update_story_assignee(jira_mock, 'PROJ-123', 'username')

        self.assertTrue(result)
        jira_mock.issue.assert_called_once_with('PROJ-123')
        mock_get_user_account_id.assert_called_once_with(jira_mock, 'username')
        expected_url = 'https://jirasimplelib.atlassian.net/rest/api/2/issue/PROJ-123/assignee'
        expected_headers = {"Accept": "application/json", "Content-Type": "application/json"}
        expected_payload = json.dumps({"accountId": 'valid_account_id'})
        mock_put.assert_called_once_with(
            expected_url, data=expected_payload, headers=expected_headers, auth=jira_mock._session.auth
        )

    @patch('jsl.get_user_account_id')
    @patch('requests.put')
    def test_update_story_assignee_no_jira(self, mock_put, mock_get_user_account_id):
        with self.assertRaises(ValueError):
            update_story_assignee(None, 'PROJ-123', 'username')

    @patch('jsl.get_user_account_id')
    @patch('requests.put')
    def test_update_story_assignee_no_issue_key(self, mock_put, mock_get_user_account_id):
        jira_mock = MagicMock()
        with self.assertRaises(ValueError):
            update_story_assignee(jira_mock, '', 'username')

    @patch('jsl.get_user_account_id')
    @patch('requests.put')
    def test_update_story_assignee_no_username(self, mock_put, mock_get_user_account_id):
        jira_mock = MagicMock()
        with self.assertRaises(ValueError):
            update_story_assignee(jira_mock, 'PROJ-123', '')

    @patch('jsl.get_user_account_id')
    @patch('requests.put')
    def test_update_story_assignee_invalid_user(self, mock_put, mock_get_user_account_id):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = MagicMock()
        mock_get_user_account_id.return_value = None

        result = update_story_assignee(jira_mock, 'PROJ-123', 'username')

        self.assertFalse(result)
        mock_get_user_account_id.assert_called_once_with(jira_mock, 'username')

    @patch('jsl.get_user_account_id')
    @patch('requests.put')
    def test_update_story_assignee_jira_error(self, mock_put, mock_get_user_account_id):
        jira_mock = MagicMock()
        jira_mock.issue.side_effect = JIRAError('JIRA Error')
        mock_get_user_account_id.return_value = 'valid_account_id'

        result = update_story_assignee(jira_mock, 'PROJ-123', 'username')

        self.assertFalse(result)
        jira_mock.issue.assert_called_once_with('PROJ-123')

    @patch('jsl.get_user_account_id')
    @patch('requests.put')
    def test_update_story_assignee_request_exception(self, mock_put, mock_get_user_account_id):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = MagicMock()
        mock_get_user_account_id.return_value = 'valid_account_id'
        mock_put.side_effect = requests.exceptions.RequestException

        with self.assertRaises(requests.exceptions.RequestException):
            update_story_assignee(jira_mock, 'PROJ-123', 'username')

class TestGetAssignee(unittest.TestCase):
    @patch('jsl.logging')
    def test_get_assignee_with_assignee(self, mock_logging):
        # Create a mock JIRA client
        jira_mock = MagicMock()
        # Create a mock issue
        issue_mock = MagicMock()
        # Create a mock fields object
        fields_mock = MagicMock()
        # Create a mock assignee
        assignee_mock = MagicMock()
        
        # Set up the mock assignee's displayName
        assignee_mock.displayName = 'John Doe'
        fields_mock.assignee = assignee_mock
        issue_mock.fields = fields_mock
        jira_mock.issue.return_value = issue_mock
        
        # Call the function being tested
        get_assignee(jira_mock, 'PROJ-123')
        
        # Check if the logging was called with the correct info message
        mock_logging.info.assert_called_once_with('The assignee of issue PROJ-123 is: John Doe')

    @patch('jsl.logging')
    def test_get_assignee_without_assignee(self, mock_logging):
        # Create a mock JIRA client
        jira_mock = MagicMock()
        # Create a mock issue
        issue_mock = MagicMock()
        # Create a mock fields object with no assignee
        fields_mock = MagicMock()
        fields_mock.assignee = None
        issue_mock.fields = fields_mock
        jira_mock.issue.return_value = issue_mock
        
        # Call the function being tested
        get_assignee(jira_mock, 'PROJ-123')
        
        # Check if the logging was called with the correct info message
        mock_logging.info.assert_called_once_with('Issue PROJ-123 is currently unassigned.')

    @patch('jsl.logging')
    def test_get_assignee_with_error(self, mock_logging):
        # Create a mock JIRA client that raises an error
        jira_mock = MagicMock()
        jira_mock.issue.side_effect = JIRAError('Error message')
        
        # Call the function being tested
        get_assignee(jira_mock, 'PROJ-123')
        
        # Capture the error message logged
        logged_error = mock_logging.error.call_args[0][0]
        
        # Check if the error message contains the expected substring
        self.assertIn('Error viewing assignee: ', logged_error)
        self.assertIn('Error message', logged_error)
    
class TestDeleteStory(unittest.TestCase):
    @patch('jsl.logging')
    def test_delete_story_success_auto_confirm(self, mock_logging):
        jira_mock = MagicMock()
        issue_mock = MagicMock()

        jira_mock.issue.return_value = issue_mock

        result = delete_story(jira_mock, 'PROJ-123', auto_confirm=True)

        issue_mock.delete.assert_called_once()
        mock_logging.info.assert_called_once_with('Story deleted successfully. Key: PROJ-123')
        self.assertTrue(result)

    @patch('jsl.logging')
    @patch('builtins.input', return_value='y')
    def test_delete_story_success_manual_confirm(self, mock_input, mock_logging):
        jira_mock = MagicMock()
        issue_mock = MagicMock()

        jira_mock.issue.return_value = issue_mock

        result = delete_story(jira_mock, 'PROJ-123', auto_confirm=False)

        mock_input.assert_called_once_with('Do you really want to delete the story with key PROJ-123? [y/n]: ')
        issue_mock.delete.assert_called_once()
        mock_logging.info.assert_called_once_with('Story deleted successfully. Key: PROJ-123')
        self.assertTrue(result)

    @patch('jsl.logging')
    @patch('builtins.input', return_value='n')
    def test_delete_story_cancel_manual_confirm(self, mock_input, mock_logging):
        jira_mock = MagicMock()
        issue_mock = MagicMock()

        jira_mock.issue.return_value = issue_mock

        result = delete_story(jira_mock, 'PROJ-123', auto_confirm=False)

        mock_input.assert_called_once_with('Do you really want to delete the story with key PROJ-123? [y/n]: ')
        issue_mock.delete.assert_not_called()
        mock_logging.info.assert_called_once_with('Story deletion cancelled by user. Key: PROJ-123')
        self.assertFalse(result)

    @patch('jsl.logging')
    def test_delete_story_issue_not_found(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = None

        result = delete_story(jira_mock, 'PROJ-123', auto_confirm=True)

        jira_mock.issue.assert_called_once_with('PROJ-123')
        mock_logging.error.assert_called_once_with('Story with key PROJ-123 does not exist.')
        self.assertFalse(result)

    @patch('jsl.logging')
    def test_delete_story_permission_denied(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.side_effect = JIRAError(status_code=403, text='Permission denied')

        result = delete_story(jira_mock, 'PROJ-123', auto_confirm=True)

        jira_mock.issue.assert_called_once_with('PROJ-123')
        mock_logging.error.assert_called_once_with(
            'Permission denied: You do not have permission to delete the story with key PROJ-123. Response text: Permission denied'
        )
        self.assertFalse(result)
    @patch('jsl.logging')
    def test_delete_story_unexpected_error(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.side_effect = Exception('Unexpected error')

        result = delete_story(jira_mock, 'PROJ-123', auto_confirm=True)

        jira_mock.issue.assert_called_once_with('PROJ-123')
        mock_logging.error.assert_called_once_with('An unexpected error occurred: Unexpected error')
        self.assertFalse(result)
        
    
class TestAddComment(unittest.TestCase):
    @patch('jsl.logging')
    def test_add_comment_success(self, mock_logging):
        jira_mock = MagicMock()
        issue_mock = MagicMock()

        jira_mock.issue.return_value = issue_mock

        result = add_comment(jira_mock, 'PROJ-123', 'This is a comment')

        jira_mock.add_comment.assert_called_once_with(issue_mock, 'This is a comment')
        mock_logging.info.assert_called_once_with('Comment added to issue PROJ-123')
        self.assertEqual(result, 1)

    @patch('jsl.logging')
    def test_add_comment_issue_not_found(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = None

        result = add_comment(jira_mock, 'PROJ-123', 'This is a comment')

        jira_mock.issue.assert_called_once_with('PROJ-123')
        jira_mock.add_comment.assert_not_called()
        mock_logging.error.assert_called_once_with('Issue with key PROJ-123 does not exist.')
        self.assertEqual(result, 0)

    
class TestGetStoryDetails(unittest.TestCase):
    @patch('jsl.logging')
    def test_get_story_details_success(self, mock_logging):
        jira_mock = MagicMock()
        story_mock = MagicMock()

        story_mock.key = 'PROJ-123'
        story_mock.fields.summary = 'Story summary'
        story_mock.fields.description = 'Story description'
        story_mock.fields.status.name = 'Open'
        story_mock.fields.assignee.displayName = 'John Doe'
        story_mock.fields.reporter.displayName = 'Jane Doe'
        story_mock.fields.created = '2024-01-01T00:00:00.000+0000'
        story_mock.fields.updated = '2024-01-02T00:00:00.000+0000'

        jira_mock.issue.return_value = story_mock

        get_story_details(jira_mock, 'PROJ-123')

        mock_logging.info.assert_any_call('Key: PROJ-123')
        mock_logging.info.assert_any_call('Summary: Story summary')
        mock_logging.info.assert_any_call('Description: Story description')
        mock_logging.info.assert_any_call('Status: Open')
        mock_logging.info.assert_any_call('Assignee: John Doe')
        mock_logging.info.assert_any_call('Reporter: Jane Doe')
        mock_logging.info.assert_any_call('Created: 2024-01-01T00:00:00.000+0000')
        mock_logging.info.assert_any_call('Updated: 2024-01-02T00:00:00.000+0000')

    @patch('jsl.logging')
    def test_get_story_details_unassigned(self, mock_logging):
        jira_mock = MagicMock()
        story_mock = MagicMock()

        story_mock.key = 'PROJ-123'
        story_mock.fields.summary = 'Story summary'
        story_mock.fields.description = 'Story description'
        story_mock.fields.status.name = 'Open'
        story_mock.fields.assignee = None
        story_mock.fields.reporter = None
        story_mock.fields.created = '2024-01-01T00:00:00.000+0000'
        story_mock.fields.updated = '2024-01-02T00:00:00.000+0000'

        jira_mock.issue.return_value = story_mock

        get_story_details(jira_mock, 'PROJ-123')

        mock_logging.info.assert_any_call('Key: PROJ-123')
        mock_logging.info.assert_any_call('Summary: Story summary')
        mock_logging.info.assert_any_call('Description: Story description')
        mock_logging.info.assert_any_call('Status: Open')
        mock_logging.info.assert_any_call('Assignee: Unassigned')
        mock_logging.info.assert_any_call('Reporter: Unassigned')
        mock_logging.info.assert_any_call('Created: 2024-01-01T00:00:00.000+0000')
        mock_logging.info.assert_any_call('Updated: 2024-01-02T00:00:00.000+0000')

    @patch('jsl.logging')
    def test_get_story_details_issue_not_found(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = None

        get_story_details(jira_mock, 'PROJ-123')

        jira_mock.issue.assert_called_once_with('PROJ-123')
        mock_logging.error.assert_called_once_with('Story with key PROJ-123 does not exist.')
class TestCreateEpic(unittest.TestCase):
    @patch('jsl.logging')
    def test_create_epic_success(self, mock_logging):
        jira_mock = MagicMock()
        new_epic_mock = MagicMock()

        jira_mock.create_issue.return_value = new_epic_mock
        new_epic_mock.key = 'EPIC-123'

        result = create_epic(jira_mock, 'PROJ', 'Epic Name', 'Epic Summary')

        jira_mock.create_issue.assert_called_once_with(
            project='PROJ',
            summary='Epic Summary',
            issuetype={"name": "Epic"}
        )
        mock_logging.info.assert_called_once_with('Epic created successfully. Epic Key: EPIC-123')
        self.assertEqual(result, new_epic_mock)

class TestListEpics(unittest.TestCase):
    @patch('jsl.logging')
    def test_list_epics_success(self, mock_logging):
        jira_mock = MagicMock()
        epics_mock = [MagicMock(), MagicMock()]

        jira_mock.search_issues.return_value = epics_mock

        result = list_epics(jira_mock, 'PROJ')

        jira_mock.search_issues.assert_called_once_with('project = PROJ AND issuetype = Epic')
        self.assertEqual(result, epics_mock)

    @patch('jsl.logging')
    def test_list_epics_exception(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.search_issues.side_effect = Exception('Unexpected error')

        result = list_epics(jira_mock, 'PROJ')

        jira_mock.search_issues.assert_called_once_with('project = PROJ AND issuetype = Epic')
        mock_logging.error.assert_called_once_with('Error listing epics: Unexpected error')
        self.assertIsNone(result)
        

class TestUpdateEpic(unittest.TestCase):
    @patch('jsl.logging')
    def test_update_epic_success(self, mock_logging):
        jira_mock = MagicMock()
        epic_mock = MagicMock()

        jira_mock.issue.return_value = epic_mock

        result = update_epic(jira_mock, 'EPIC-123', 'New Summary', 'New Description')

        epic_mock.update.assert_called_once_with(
            summary='New Summary',
            description='New Description'
        )
        mock_logging.info.assert_called_once_with('Epic updated successfully. Key: EPIC-123')
        self.assertEqual(result, epic_mock)


class TestGetEpicDetails(unittest.TestCase):
    @patch('jsl.logging')
    def test_get_epic_details_success_with_stories(self, mock_logging):
        jira_mock = MagicMock()
        epic_mock = MagicMock()
        story_mock1 = MagicMock()
        story_mock2 = MagicMock()

        epic_mock.key = 'EPIC-123'
        epic_mock.fields.summary = 'Epic Summary'

        story_mock1.key = 'STORY-1'
        story_mock1.fields.summary = 'Story 1 Summary'
        story_mock1.fields.status = 'In Progress'
        story_mock1.fields.assignee = 'John Doe'
        story_mock1.fields.duedate = '2024-07-15'
        story_mock1.fields.customfield_10015 = '2024-07-10'

        story_mock2.key = 'STORY-2'
        story_mock2.fields.summary = 'Story 2 Summary'
        story_mock2.fields.status = 'To Do'
        story_mock2.fields.assignee = None
        story_mock2.fields.duedate = None
        story_mock2.fields.customfield_10015 = None

        jira_mock.issue.side_effect = [epic_mock, story_mock1, story_mock2]
        jira_mock.search_issues.return_value = [story_mock1, story_mock2]

        get_epic_details(jira_mock, 'EPIC-123')

        mock_logging.info.assert_any_call('Epic Key: EPIC-123')
        mock_logging.info.assert_any_call('Summary: Epic Summary')
        mock_logging.info.assert_any_call('Stories in the Epic:')
        mock_logging.info.assert_any_call('Story Key: STORY-1')
        mock_logging.info.assert_any_call('Summary: Story 1 Summary')
        mock_logging.info.assert_any_call('Status: In Progress')
        mock_logging.info.assert_any_call('Assignee: John Doe')
        mock_logging.info.assert_any_call('Due Date: 2024-07-15')
        mock_logging.info.assert_any_call('Start Date: 2024-07-10')
        mock_logging.info.assert_any_call('Story Key: STORY-2')
        mock_logging.info.assert_any_call('Summary: Story 2 Summary')
        mock_logging.info.assert_any_call('Status: To Do')
        mock_logging.info.assert_any_call('Assignee: None')
        mock_logging.info.assert_any_call('Due Date: None')
        mock_logging.info.assert_any_call('Start Date: None')

    @patch('jsl.logging')
    def test_get_epic_details_success_no_stories(self, mock_logging):
        jira_mock = MagicMock()
        epic_mock = MagicMock()

        epic_mock.key = 'EPIC-123'
        epic_mock.fields.summary = 'Epic Summary'

        jira_mock.issue.return_value = epic_mock
        jira_mock.search_issues.return_value = []

        get_epic_details(jira_mock, 'EPIC-123')

        mock_logging.info.assert_any_call('Epic Key: EPIC-123')
        mock_logging.info.assert_any_call('Summary: Epic Summary')
        mock_logging.info.assert_any_call('No stories found in the Epic.')


class TestAddIssuesToEpic(unittest.TestCase):
    @patch('jsl.logging')
    def test_add_issues_to_epic_epic_not_found(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = None

        result = add_issues_to_epic(jira_mock, 'EPIC-123', ['ISSUE-1'])

        jira_mock.issue.assert_called_once_with('EPIC-123')
        mock_logging.error.assert_called_once_with('Epic with key EPIC-123 does not exist.')
        self.assertFalse(result)

    @patch('jsl.logging')
    def test_add_issues_to_epic_issue_not_found(self, mock_logging):
        jira_mock = MagicMock()
        epic_mock = MagicMock()

        epic_mock.key = 'EPIC-123'
        jira_mock.issue.side_effect = [epic_mock, None]

        result = add_issues_to_epic(jira_mock, 'EPIC-123', ['ISSUE-1'])

        jira_mock.issue.assert_any_call('EPIC-123')
        jira_mock.issue.assert_any_call('ISSUE-1')

        mock_logging.error.assert_called_once_with('Issue with key ISSUE-1 does not exist.')
        self.assertFalse(result)


class TestUnlinkStoryFromEpic(unittest.TestCase):
    @patch('jsl.logging')
    def test_unlink_story_from_epic_success(self, mock_logging):
        jira_mock = MagicMock()
        story_mock = MagicMock()

        story_mock.key = 'STORY-1'

        jira_mock.issue.return_value = story_mock

        result = unlink_story_from_epic(jira_mock, 'STORY-1')

        jira_mock.issue.assert_called_once_with('STORY-1')
        story_mock.update.assert_called_once_with(fields={'customfield_10014': None})

        mock_logging.info.assert_called_once_with('Story STORY-1 unlinked from its Epic')
        self.assertTrue(result)

class TestDeleteEpic(unittest.TestCase):
    @patch('jsl.logging')
    @patch('builtins.input', return_value='y')  # Mocking user input to 'y'
    def test_delete_epic_with_auto_confirm(self, mock_input, mock_logging):
        jira_mock = MagicMock()
        epic_mock = MagicMock()

        epic_mock.key = 'EPIC-123'

        jira_mock.issue.return_value = epic_mock

        result = delete_epic(jira_mock, 'EPIC-123', auto_confirm=True)

        jira_mock.issue.assert_called_once_with('EPIC-123')
        epic_mock.delete.assert_called_once()

        mock_logging.info.assert_called_once_with('Epic deleted successfully. Key: EPIC-123')
        self.assertTrue(result)

    @patch('jsl.logging')
    @patch('builtins.input', return_value='y')  # Mocking user input to 'y'
    def test_delete_epic_without_auto_confirm(self, mock_input, mock_logging):
        jira_mock = MagicMock()
        epic_mock = MagicMock()

        epic_mock.key = 'EPIC-123'

        jira_mock.issue.return_value = epic_mock

        result = delete_epic(jira_mock, 'EPIC-123', auto_confirm=False)

        jira_mock.issue.assert_called_once_with('EPIC-123')
        epic_mock.delete.assert_called_once()

        mock_input.assert_called_once()
        mock_logging.info.assert_called_once_with('Epic deleted successfully. Key: EPIC-123')
        self.assertTrue(result)

    @patch('jsl.logging')
    def test_delete_epic_epic_not_found(self, mock_logging):
        jira_mock = MagicMock()
        jira_mock.issue.return_value = None

        result = delete_epic(jira_mock, 'EPIC-123')

        jira_mock.issue.assert_called_once_with('EPIC-123')
        mock_logging.error.assert_called_once_with('Epic with key EPIC-123 does not exist.')
        self.assertFalse(result)
class TestCreateSprint(unittest.TestCase):
    @patch('jsl.logging')
    @patch('jsl.requests.post')
    def test_create_sprint_success(self, mock_post, mock_logging):
        jira_mock = MagicMock()
        jira_mock._options = {'server': 'https://example.com'}
        jira_mock._session.auth = ('username', 'password')

        board_id = 1001
        sprint_name = 'New Sprint'

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 2001}
        mock_post.return_value = mock_response

        result = create_sprint(jira_mock, board_id, sprint_name)

        mock_post.assert_called_once_with(
            'https://example.com/rest/agile/1.0/sprint',
            json={'name': sprint_name, 'originBoardId': board_id},
            auth=('username', 'password')
        )

        mock_logging.info.assert_called_once_with('New Sprint created with ID: 2001')
        self.assertEqual(result, 2001)

    @patch('jsl.logging')
    @patch('jsl.requests.post')
    def test_create_sprint_failure(self, mock_post, mock_logging):
        jira_mock = MagicMock()
        jira_mock._options = {'server': 'https://example.com'}
        jira_mock._session.auth = ('username', 'password')

        board_id = 1001
        sprint_name = 'New Sprint'

        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 400
        mock_response.text = 'Error message'
        mock_post.return_value = mock_response

        result = create_sprint(jira_mock, board_id, sprint_name)

        mock_post.assert_called_once_with(
            'https://example.com/rest/agile/1.0/sprint',
            json={'name': sprint_name, 'originBoardId': board_id},
            auth=('username', 'password')
        )

        mock_logging.error.assert_called_once_with(
            'Failed to create a new Sprint. Status code: 400, Error: Error message'
        )
        self.assertIsNone(result)


class TestListSprints(unittest.TestCase):
    @patch('jsl.logging')
    def test_list_sprints_success(self, mock_logging):
        jira_mock = MagicMock()
        board_id = 1001
        expected_sprints = [
            {'id': 2001, 'name': 'Sprint 1'},
            {'id': 2002, 'name': 'Sprint 2'}
        ]
        jira_mock.sprints.return_value = expected_sprints

        result = list_sprints(jira_mock, board_id)

        jira_mock.sprints.assert_called_once_with(board_id)
        self.assertEqual(result, expected_sprints)
        mock_logging.assert_not_called()  # Ensure no logging occurred on success

    @patch('jsl.logging')
    def test_list_sprints_error(self, mock_logging):
        jira_mock = MagicMock()
        board_id = 1001
        jira_mock.sprints.side_effect = Exception('Connection error')

        result = list_sprints(jira_mock, board_id)

        jira_mock.sprints.assert_called_once_with(board_id)
        mock_logging.error.assert_called_once_with('Error retrieving sprints for board: Connection error')
        self.assertIsNone(result)
        
                      
if __name__ == "__main__":
    unittest.main()
