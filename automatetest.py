import unittest
from datetime import datetime
import requests
import json
from jira import JIRAError, JIRA
from unittest.mock import MagicMock, patch, call, mock_open
from jirasimplelib import read_config, create_jira_connection, create_jira_project, update_jira_project, delete_all_projects, get_stories_for_project, delete_all_stories_in_project, create_story, update_story_summary, update_story_status, update_story_description, add_comment_to_issues_in_range, read_story_details, delete_story, create_epic, update_epic, read_epic_details, add_story_to_epic, unlink_story_from_epic, delete_epic, list_epics, create_sprint, move_issues_to_sprint, start_sprint, get_stories_in_sprint, complete_stories_in_sprint, complete_sprint, get_sprints_for_board, update_sprint_summary, sprint_report, get_velocity, delete_sprint, delete_all_sprints, create_board, get_board_id

class TestReadConfig(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_read_config(self, mock_open):
        config = read_config('test_config.json')
        self.assertEqual(config, {"key": "value"})

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_read_config_file_not_found(self, mock_open):
        with self.assertRaises(FileNotFoundError):
            read_config('nonexistent_file.json')
class TestCreateJiraConnection(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"jira_url": "http://example.com", "user": "test_user", "api_token": "test_token"}')
    @patch('jirasimplelib.JIRA', return_value=MagicMock())
    def test_create_jira_connection_success(self, mock_jira, mock_open):
        jira = create_jira_connection('config.json')
        self.assertIsNotNone(jira, "Jira connection should not be None")

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_create_jira_connection_file_not_found(self, mock_open):
        jira = create_jira_connection('config.json')
        self.assertIsNone(jira, "Jira connection should be None when config file is not found")

    @patch('builtins.open', new_callable=mock_open, read_data='{"jira_url": "http://example.com", "api_token": "test_token"}')
    def test_create_jira_connection_missing_user(self, mock_open):
        jira = create_jira_connection('config.json')
        self.assertIsNone(jira, "Jira connection should be None when user is missing from config")

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_create_jira_connection_missing_config_fields(self, mock_open):
        jira = create_jira_connection('config.json')
        self.assertIsNone(jira, "Jira connection should be None when required config fields are missing")

    @patch('builtins.open', new_callable=mock_open, read_data='{"jira_url": "http://example.com", "user": "test_user", "api_token": "test_token"}')
    @patch('jirasimplelib.JIRA', side_effect=JIRAError(status_code=404))
    def test_create_jira_connection_jira_error(self, mock_jira, mock_open):
        jira = create_jira_connection('config.json')
        self.assertIsNone(jira, "Jira connection should be None when encountering JIRAError")
class TestCreateJiraProject(unittest.TestCase):
    @patch('jirasimplelib.logging')
    def test_create_jira_project_success(self, mock_logging):
        # Mock JIRA instance
        mock_jira = MagicMock()
        mock_project = MagicMock()
        mock_jira.create_project.return_value = mock_project
        
        # Call the function under test
        result = create_jira_project(mock_jira, 'Test Project', 'TEST')
        
        # Assertions
        self.assertEqual(result, mock_project)
        mock_logging.info.assert_called_once_with("Project 'Test Project' created successfully.")

    @patch('jirasimplelib.logging')
    def test_create_jira_project_failure_jira_error(self, mock_logging):
        # Mock JIRA instance
        mock_jira = MagicMock()
        mock_jira.create_project.side_effect = JIRAError("Test JIRA Error")
        
        # Call the function under test
        result = create_jira_project(mock_jira, 'Test Project', 'TEST')
        
        # Assertions
        self.assertIsNone(result)
        mock_logging.error.assert_called_once()

    @patch('jirasimplelib.logging')
    def test_create_jira_project_failure_general_error(self, mock_logging):
        # Mock JIRA instance
        mock_jira = MagicMock()
        mock_jira.create_project.side_effect = Exception("Test General Error")
        
        # Call the function under test
        result = create_jira_project(mock_jira, 'Test Project', 'TEST')
        
        # Assertions
        self.assertIsNone(result)
        mock_logging.error.assert_called_once()

# # Create JIRA connection test case
# class TestCreateJiraConnection(unittest.TestCase):
#     @patch('jirasimplelib.JIRA')  # Mocking the JIRA class used in the function
#     def test_create_jira_connection_success(self, mock_jira):
#         # Mocking the JIRA instance
#         mock_instance = MagicMock()
#         mock_jira.return_value = mock_instance

#         # Call the function under test
#         jira_url = "https://jsl-test.atlassian.net"
#         api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
#         user = "info@test01.verituslabs.net"
#         result = create_jira_connection(jira_url, user, api_token)

#         # Assertions
#         self.assertEqual(result, mock_instance)

#     @patch('jirasimplelib.JIRA', side_effect=Exception("Test Exception"))  # Simulate an exception
#     def test_create_jira_connection_failure(self, mock_jira):
#         # Call the function under test
#         jira_url = "https://jsl-test.atlassian.net"
#         api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
#         user = "info@test01.verituslabs.net"
#         result = create_jira_connection(jira_url, user, api_token)
#         # Assertions
#         self.assertIsNone(result)
# #create a project in jira
# class TestCreateJiraProject(unittest.TestCase):
#     @patch('jirasimplelib.JIRA')
#     @patch('jirasimplelib.logging.error')
#     def test_create_jira_project_success(self, mock_logging_error, mock_jira):
#         mock_instance = MagicMock()
#         mock_jira.return_value = mock_instance

#         result = create_jira_project(mock_instance, "Test1", "T1")

#         self.assertTrue(result)
#         mock_instance.create_project.assert_called_once_with("T1", "Test1")

#     @patch('jirasimplelib.JIRA')
#     @patch('jirasimplelib.logging.error')
#     def test_create_jira_project_failure(self, mock_logging_error, mock_jira):
#         mock_instance = MagicMock()
#         mock_jira.return_value = mock_instance

#         mock_instance.create_project.side_effect = Exception("Connection error")

#         result = create_jira_project(mock_instance, "Test1", "T1")

#         self.assertFalse(result)
#         mock_instance.create_project.assert_called_once_with("T1", "Test1")
#         mock_logging_error.assert_called_once_with("Error creating project: Connection error")
# #create epic
# class TestCreateEpic(unittest.TestCase):
#     def setUp(self):
#         self.mock_jira = MagicMock()

#     def test_create_epic_success(self):
#         # Arrange
#         project_key = "PROJ"
#         epic_name = "New Epic"
#         epic_summary = "Summary of New Epic"
#         expected_issue_key = "EPIC-123"

#         # Mock the create_issue method to return a predefined issue key
#         self.mock_jira.create_issue.return_value.key = expected_issue_key

#         # Act
#         new_epic = create_epic(self.mock_jira, project_key, epic_name, epic_summary)

#         # Assert
#         self.assertIsNotNone(new_epic)
#         self.assertEqual(new_epic.key, expected_issue_key)
#         self.mock_jira.create_issue.assert_called_once_with(
#             project=project_key,
#             summary=epic_summary,
#             issuetype={"name": "Epic"}
#         )

#     def test_create_epic_failure(self):
#         # Arrange
#         project_key = "PROJ"
#         epic_name = "New Epic"
#         epic_summary = "Summary of New Epic"
#         error_message = "Error creating epic: Something went wrong"

#         # Mock the create_issue method to raise a JIRAError
#         self.mock_jira.create_issue.side_effect = JIRAError(error_message)

#         # Act
#         new_epic = create_epic(self.mock_jira, project_key, epic_name, epic_summary)

#         # Assert
#         self.assertIsNone(new_epic)
#         self.mock_jira.create_issue.assert_called_once_with(
#             project=project_key,
#             summary=epic_summary,
#             issuetype={"name": "Epic"}
#         )
# #create story
# class TestCreateStory(unittest.TestCase):
#     def setUp(self):
#         self.mock_jira = MagicMock()

#     def test_create_story_success(self):
#         # Arrange
#         project_key = "PROJ"
#         summary = "New Story"
#         description = "Description of New Story"
#         expected_issue_key = "STORY-456"

#         # Mock the create_issue method to return a predefined issue key
#         self.mock_jira.create_issue.return_value.key = expected_issue_key

#         # Act
#         new_story = create_story(self.mock_jira, project_key, summary, description)

#         # Assert
#         self.assertIsNotNone(new_story)
#         self.assertEqual(new_story.key, expected_issue_key)
#         self.mock_jira.create_issue.assert_called_once_with(
#             project=project_key,
#             summary=summary,
#             description=description,
#             issuetype={"name": "Task"}
#         )

#     def test_create_story_failure(self):
#         # Arrange
#         project_key = "PROJ"
#         summary = "New Story"
#         description = "Description of New Story"
#         error_message = "Error creating story: Something went wrong"

#         # Mock the create_issue method to raise a JIRAError
#         self.mock_jira.create_issue.side_effect = JIRAError(error_message)

#         # Act
#         new_story = create_story(self.mock_jira, project_key, summary, description)

#         # Assert
#         self.assertIsNone(new_story)
#         self.mock_jira.create_issue.assert_called_once_with(
#             project=project_key,
#             summary=summary,
#             description=description,
#             issuetype={"name": "Task"}
#         )
# #add story to epic
# class TestAddStoryToEpic(unittest.TestCase):
#     def setUp(self):
#         self.mock_jira = MagicMock()

#     def test_add_story_to_epic_success(self):
#         # Arrange
#         epic_key = "EPIC-123"
#         story_key = "STORY-456"
#         mock_epic_issue = MagicMock(id="EPIC-123_ID")
#         mock_story_issue = MagicMock(id="STORY-456_ID")

#         # Mock jira.issue to return MagicMock objects
#         self.mock_jira.issue.side_effect = [mock_epic_issue, mock_story_issue]

#         # Act
#         result = add_story_to_epic(self.mock_jira, epic_key, story_key)

#         # Assert
#         self.assertTrue(result)
#         self.mock_jira.add_issues_to_epic.assert_called_once_with("EPIC-123_ID", ["STORY-456_ID"])

#     def test_add_story_to_epic_failure(self):
#         # Arrange
#         epic_key = "EPIC-123"
#         story_key = "STORY-456"
#         error_message = "Error adding story to epic: Something went wrong"

#         # Mock jira.issue to raise a JIRAError
#         self.mock_jira.issue.side_effect = JIRAError(error_message)

#         # Act
#         result = add_story_to_epic(self.mock_jira, epic_key, story_key)

#         # Assert
#         self.assertFalse(result)
#         self.mock_jira.add_issues_to_epic.assert_not_called()
# #create sprint
# class TestCreateSprint(unittest.TestCase):
#     @patch('requests.post')
#     def test_create_sprint_success(self, mock_post):
#         # Arrange
#         jira_url = "https://jsl-test.atlassian.net"
#         api_token = "your_api_token"
#         jira_username = "your_username"
#         board_id = "your_board_id"
#         sprint_name = "Test Sprint"
#         expected_sprint_id = "123456"

#         mock_response = requests.Response()
#         mock_response.status_code = 201
#         mock_response.json = lambda: {"id": expected_sprint_id}  # Patching the json() method to return a predefined value
#         mock_post.return_value = mock_response

#         # Act
#         sprint_id = create_sprint(jira_url, jira_username, api_token, board_id, sprint_name)

#         # Assert
#         self.assertEqual(sprint_id, expected_sprint_id)
#         mock_post.assert_called_once_with(
#             f"{jira_url}/rest/agile/1.0/sprint",
#             json={"name": sprint_name, "originBoardId": board_id},
#             auth=(jira_username, api_token)
#         )

#     @patch('requests.post')
#     def test_create_sprint_failure(self, mock_post):
#         # Arrange
#         jira_url = "https://jsl-test.atlassian.net"
#         api_token = "your_api_token"
#         jira_username = "your_username"
#         board_id = "your_board_id"
#         sprint_name = "Test Sprint"

#         mock_response = requests.Response()
#         mock_response.status_code = 400
#         mock_response._content = b"Error message"  # Set the content directly instead of using the 'text' attribute
#         mock_post.return_value = mock_response

#         # Act
#         sprint_id = create_sprint(jira_url, jira_username, api_token, board_id, sprint_name)

#         # Assert
#         self.assertIsNone(sprint_id)
#         mock_post.assert_called_once_with(
#             f"{jira_url}/rest/agile/1.0/sprint",
#             json={"name": sprint_name, "originBoardId": board_id},
#             auth=(jira_username, api_token)
#         )
# #move issues to sprint

# class TestMoveIssuesToSprint(unittest.TestCase):
#     def setUp(self):
#         self.mock_jira = MagicMock()

#     def test_move_issues_to_sprint(self):
#         # Arrange
#         start_issue_key = "JST-1"
#         end_issue_key = "JST-3"
#         target_sprint_id = 12345

#         # Mock the issue method to return a MagicMock object
#         self.mock_jira.issue.side_effect = lambda x: MagicMock(key=x)

#         # Act
#         move_issues_to_sprint(self.mock_jira, start_issue_key, end_issue_key, target_sprint_id)

#         # Assert
#         expected_calls = [
#             call(target_sprint_id, ['JST-1']),
#             call(target_sprint_id, ['JST-2']),
#             call(target_sprint_id, ['JST-3'])
#         ]
#         self.assertEqual(self.mock_jira.add_issues_to_sprint.call_count, 3)
#         self.mock_jira.add_issues_to_sprint.assert_has_calls(expected_calls)

#     def test_move_issues_to_sprint_error(self):
#         # Arrange
#         start_issue_key = "JST-1"
#         end_issue_key = "JST-3"
#         target_sprint_id = 12345

#         # Mock the issue method to raise an exception
#         self.mock_jira.issue.side_effect = Exception("Issue not found")

#         # Act
#         move_issues_to_sprint(self.mock_jira, start_issue_key, end_issue_key, target_sprint_id)

#         # Assert
#         self.assertEqual(self.mock_jira.add_issues_to_sprint.call_count, 0)
#     #start sprint
# class TestStartSprint(unittest.TestCase):
#     def setUp(self):
#         self.mock_jira = MagicMock()

#     def test_start_sprint_success(self):
#         # Arrange
#         sprint_id = 123
#         new_summary = "New Sprint Summary"
#         start_date = datetime(2024, 2, 15)
#         end_date = datetime(2024, 2, 29)

#         # Mock the sprint method to return a MagicMock object
#         mock_sprint = MagicMock()
#         self.mock_jira.sprint.return_value = mock_sprint

#         # Act
#         result = start_sprint(self.mock_jira, sprint_id, new_summary, start_date, end_date)

#         # Assert
#         self.assertIsNotNone(result)
#         mock_sprint.update.assert_called_once_with(
#             name=new_summary,
#             state='active',
#             startDate=start_date,
#             endDate=end_date
#         )
#         self.assertTrue(mock_sprint.started)

#     def test_start_sprint_failure(self):
#         # Arrange
#         sprint_id = 123
#         new_summary = "New Sprint Summary"
#         start_date = datetime(2024, 2, 15)
#         end_date = datetime(2024, 2, 29)

#         # Mock the sprint method to raise a JIRAError
#         self.mock_jira.sprint.side_effect = JIRAError("Sprint not found")

#         # Act
#         result = start_sprint(self.mock_jira, sprint_id, new_summary, start_date, end_date)

#         # Assert
#         self.assertIsNone(result)
#         self.mock_jira.sprint.assert_called_once_with(sprint_id)

#     #add comments in a stories
# class TestAddCommentToIssuesInRange(unittest.TestCase):
#     def test_add_comment_to_issues_in_range(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the issue object
#         issue_mock = MagicMock()

#         # Configure the return value of the jira.issue method
#         jira_mock.issue.return_value = issue_mock

#         # Call the function with mock objects
#         start_issue_num = 1
#         end_issue_num = 3
#         comment_body = "Test comment"
#         success_count = add_comment_to_issues_in_range(jira_mock, start_issue_num, end_issue_num, comment_body)

#         # Assertions
#         self.assertEqual(success_count, 3)  # We assume all issues are successfully commented
#         self.assertEqual(jira_mock.issue.call_count, 3)  # Ensure jira.issue is called for each issue
#         jira_mock.add_comment.assert_called_with(issue_mock, comment_body)  # Ensure add_comment is called with the correct arguments

#     def test_no_comment_added(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the issue object
#         issue_mock = MagicMock()

#         # Configure the return value of the jira.issue method
#         jira_mock.issue.return_value = issue_mock

#         # Configure the add_comment method to raise a JIRAError
#         jira_mock.add_comment.side_effect = JIRAError("Failed to add comment")

#         # Call the function with mock objects
#         start_issue_num = 1
#         end_issue_num = 3
#         comment_body = "Test comment"
#         success_count = add_comment_to_issues_in_range(jira_mock, start_issue_num, end_issue_num, comment_body)

#         # Assertions
#         self.assertEqual(success_count, 0)  # No issues should be successfully commented
#         self.assertEqual(jira_mock.issue.call_count, 3)  # Ensure jira.issue is called for each issue
#         jira_mock.add_comment.assert_called_with(issue_mock, comment_body)  # Ensure add_comment is called with the correct arguments

# #get stories in sprint
# class TestGetStoriesInSprint(unittest.TestCase):
#     def test_get_stories_in_sprint(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the search_issues method
#         jira_mock.search_issues.return_value = [
#             MagicMock(key="JST-1", fields=MagicMock(summary="Story 1")),
#             MagicMock(key="JST-2", fields=MagicMock(summary="Story 2"))
#         ]

#         # Call the function with mock objects
#         sprint_id = "SPRINT-1"
#         stories = get_stories_in_sprint(jira_mock, sprint_id)

#         # Assertions
#         self.assertIsNotNone(stories)  # Ensure that stories are not None
#         self.assertEqual(len(stories), 2)  # Ensure that two stories are returned
#         jira_mock.search_issues.assert_called_once_with(f'sprint = {sprint_id} AND issuetype = Task')  # Ensure search_issues is called with the correct JQL

#     def test_no_stories_in_sprint(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the search_issues method to return an empty list
#         jira_mock.search_issues.return_value = []

#         # Call the function with mock objects
#         sprint_id = "SPRINT-1"
#         stories = get_stories_in_sprint(jira_mock, sprint_id)

#         # Assertions
#         self.assertIsNotNone(stories)  # Ensure that stories are not None
#         self.assertEqual(len(stories), 0)  # Ensure that no stories are returned
#         jira_mock.search_issues.assert_called_once_with(f'sprint = {sprint_id} AND issuetype = Task')  # Ensure search_issues is called with the correct JQL
# #update story status
# class TestUpdateStoryStatus(unittest.TestCase):
#     def test_update_story_status_valid_status(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the issue object
#         issue_mock = MagicMock()

#         # Mock the transitions method to return a list of transitions
#         jira_mock.transitions.return_value = [
#             {'id': '1', 'to': {'name': 'In Progress'}},
#             {'id': '2', 'to': {'name': 'Done'}}
#         ]

#         # Configure the return value of the jira.issue method
#         jira_mock.issue.return_value = issue_mock

#         # Call the function with mock objects
#         story_key = "JST-1"
#         new_status = "In Progress"
#         result = update_story_status(jira_mock, story_key, new_status)

#         # Assertions
#         self.assertTrue(result)  # Update should be successful
#         jira_mock.transitions.assert_called_once_with(issue_mock)  # Ensure transitions method is called
#         jira_mock.transition_issue.assert_called_once_with(issue_mock, '1')  # Ensure transition_issue is called with the correct transition id

#     def test_update_story_status_invalid_status(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the issue object
#         issue_mock = MagicMock()

#         # Mock the transitions method to return a list of transitions
#         jira_mock.transitions.return_value = [
#             {'id': '1', 'to': {'name': 'In Progress'}},
#             {'id': '2', 'to': {'name': 'Done'}}
#         ]

#         # Configure the return value of the jira.issue method
#         jira_mock.issue.return_value = issue_mock

#         # Call the function with mock objects
#         story_key = "JST-1"
#         new_status = "Invalid Status"
#         result = update_story_status(jira_mock, story_key, new_status)

#         # Assertions
#         self.assertFalse(result)  # Update should fail due to invalid status
#         jira_mock.transitions.assert_called_once_with(issue_mock)  # Ensure transitions method is called
#         self.assertFalse(jira_mock.transition_issue.called)  # Ensure transition_issue is not called
# #complete stories in sprint
# def test_complete_stories_in_sprint_success(self):
#     # Mock the jira object
#     jira_mock = MagicMock()

#     # Mock the get_stories_in_sprint function to return a list of story keys
#     jira_mock.get_stories_in_sprint.return_value = ["JST-1", "JST-2", "JST-3"]

#     # Mock the update_story_status function to return True
#     jira_mock.update_story_status.return_value = True

#     # Call the function with mock objects
#     sprint_id = "SPRINT-1"
#     result = complete_stories_in_sprint(jira_mock, sprint_id)

#     # Assertions
#     self.assertTrue(result)  # Completion should be successful
#     jira_mock.get_stories_in_sprint.assert_called_once_with(sprint_id)  # Ensure get_stories_in_sprint is called
#     self.assertEqual(jira_mock.update_story_status.call_count, 3)  # Ensure update_story_status is called for each story
# #complete sprint
# class TestCompleteSprint(unittest.TestCase):
#     def test_complete_sprint_success(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the sprint object
#         sprint_mock = MagicMock()
#         sprint_mock.name = "Sprint 1"
#         jira_mock.sprint.return_value = sprint_mock

#         # Call the function with mock objects
#         sprint_id = "SPRINT-1"
#         start_date = "2024-02-20"
#         end_date = "2024-02-28"
#         result = complete_sprint(jira_mock, sprint_id, start_date, end_date)

#         # Assertions
#         self.assertTrue(result)  # Completion should be successful
#         jira_mock.sprint.assert_called_once_with(sprint_id)  # Ensure sprint method is called
#         sprint_mock.update.assert_called_once_with(name="Sprint 1", state='closed', startDate=start_date, endDate=end_date)  # Ensure sprint.update is called with correct arguments

#     def test_complete_sprint_failure(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the sprint object
#         sprint_mock = MagicMock()
#         sprint_mock.name = "Sprint 1"
#         jira_mock.sprint.return_value = sprint_mock

#         # Configure the sprint.update method to raise a JIRAError
#         sprint_mock.update.side_effect = JIRAError("Failed to update sprint")

#         # Call the function with mock objects
#         sprint_id = "SPRINT-1"
#         start_date = "2024-02-20"
#         end_date = "2024-02-28"
#         result = complete_sprint(jira_mock, sprint_id, start_date, end_date)

#         # Assertions
#         self.assertFalse(result)  # Completion should fail due to JIRAError
#         jira_mock.sprint.assert_called_once_with(sprint_id)  # Ensure sprint method is called
#         sprint_mock.update.assert_called_once_with(name="Sprint 1", state='closed', startDate=start_date, endDate=end_date)  # Ensure sprint.update is called with correct arguments
# #delete all stories in project
# def test_delete_all_stories_success(self):
#     # Mock the jira object
#     jira_mock = MagicMock()

#     # Mock the search_issues method to return a list of issues
#     issues_mock = [MagicMock(key=f"STORY-{i}") for i in range(1, 4)]
#     jira_mock.search_issues.return_value = issues_mock

#     # Call the function with mock objects
#     project_key = "PROJECT-1"
#     result = delete_all_stories_in_project(jira_mock, project_key)

#     # Assertions
#     self.assertTrue(result)  # Deletion should be successful
#     jira_mock.search_issues.assert_called_once_with(f'project={project_key}')  # Ensure search_issues is called with correct argument
#     # Ensure delete is called for each issue
#     self.assertEqual(jira_mock.delete.call_count, len(issues_mock))  
#     # Ensure delete is called with each issue
#     jira_mock.delete.assert_called_with(issues_mock[0])  
#     jira_mock.delete.assert_called_with(issues_mock[1])  
#     jira_mock.delete.assert_called_with(issues_mock[2])  
# #delete all sprints
# def test_delete_all_sprints_success(self):
#     # Mock the jira object
#     jira_mock = MagicMock()

#     # Mock the sprints method to return a list of sprints
#     sprints_mock = [MagicMock(id=f"SPRINT-{i}") for i in range(1, 4)]
#     jira_mock.sprints.return_value = sprints_mock

#     # Call the function with mock objects
#     board_id = "BOARD-1"
#     result = delete_all_sprints(jira_mock, board_id)

#     # Assertions
#     self.assertTrue(result)  # Deletion should be successful
#     jira_mock.sprints.assert_called_once_with(board_id)  # Ensure sprints is called with correct argument
#     # Ensure delete is called for each sprint
#     self.assertEqual(jira_mock.delete.call_count, len(sprints_mock))  
#     for sprint in sprints_mock:
#         jira_mock.delete.assert_called_with(sprint)  
# #delete all projects
# class TestDeleteAllProjects(unittest.TestCase):
#     def test_delete_all_projects_success(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Mock the projects method to return a list of projects
#         projects_mock = [MagicMock(key=f"PROJECT-{i}") for i in range(1, 4)]
#         jira_mock.projects.return_value = projects_mock

#         # Call the function with mock objects
#         result = delete_all_projects(jira_mock)

#         # Assertions
#         self.assertTrue(result)  # Deletion should be successful
#         jira_mock.projects.assert_called_once()  # Ensure projects is called

#         # Ensure delete_project is called for each project with correct arguments
#         expected_calls = [call(project.key) for project in projects_mock]
#         jira_mock.delete_project.assert_has_calls(expected_calls, any_order=True)

#     def test_delete_all_projects_failure(self):
#         # Mock the jira object
#         jira_mock = MagicMock()

#         # Configure the projects method to raise an exception
#         jira_mock.projects.side_effect = Exception("Failed to retrieve projects")

#         # Call the function with mock objects
#         result = delete_all_projects(jira_mock)

#         # Assertions
#         self.assertFalse(result)  # Deletion should fail due to exception
#         jira_mock.projects.assert_called_once()  # Ensure projects is called

if __name__ == "__main__":
    unittest.main()
