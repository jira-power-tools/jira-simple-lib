import unittest
from datetime import datetime
import requests
from jira import JIRAError
from unittest.mock import MagicMock, patch, call
from run_test import create_jira_connection, create_jira_project, create_epic, create_story, add_story_to_epic, create_sprint, move_issues_to_sprint, start_sprint
import logging

# Create JIRA connection test case
class TestCreateJiraConnection(unittest.TestCase):
    @patch('run_test.JIRA')  # Mocking the JIRA class used in the function
    def test_create_jira_connection_success(self, mock_jira):
        # Mocking the JIRA instance
        mock_instance = MagicMock()
        mock_jira.return_value = mock_instance

        # Call the function under test
        jira_url = "https://jsl-test.atlassian.net"
        api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
        user = "info@test01.verituslabs.net"
        result = create_jira_connection(jira_url, user, api_token)

        # Assertions
        self.assertEqual(result, mock_instance)

    @patch('run_test.JIRA', side_effect=Exception("Test Exception"))  # Simulate an exception
    def test_create_jira_connection_failure(self, mock_jira):
        # Call the function under test
        jira_url = "https://jsl-test.atlassian.net"
        api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
        user = "info@test01.verituslabs.net"
        result = create_jira_connection(jira_url, user, api_token)
        # Assertions
        self.assertIsNone(result)
#create a project in jira
class TestCreateJiraProject(unittest.TestCase):
    @patch('run_test.JIRA')
    @patch('run_test.logging.error')
    def test_create_jira_project_success(self, mock_logging_error, mock_jira):
        mock_instance = MagicMock()
        mock_jira.return_value = mock_instance

        result = create_jira_project(mock_instance, "Test1", "T1")

        self.assertTrue(result)
        mock_instance.create_project.assert_called_once_with("T1", "Test1")

    @patch('run_test.JIRA')
    @patch('run_test.logging.error')
    def test_create_jira_project_failure(self, mock_logging_error, mock_jira):
        mock_instance = MagicMock()
        mock_jira.return_value = mock_instance

        mock_instance.create_project.side_effect = Exception("Connection error")

        result = create_jira_project(mock_instance, "Test1", "T1")

        self.assertFalse(result)
        mock_instance.create_project.assert_called_once_with("T1", "Test1")
        mock_logging_error.assert_called_once_with("Error creating project: Connection error")
#create epic
class TestCreateEpic(unittest.TestCase):
    def setUp(self):
        self.mock_jira = MagicMock()

    def test_create_epic_success(self):
        # Arrange
        project_key = "PROJ"
        epic_name = "New Epic"
        epic_summary = "Summary of New Epic"
        expected_issue_key = "EPIC-123"

        # Mock the create_issue method to return a predefined issue key
        self.mock_jira.create_issue.return_value.key = expected_issue_key

        # Act
        new_epic = create_epic(self.mock_jira, project_key, epic_name, epic_summary)

        # Assert
        self.assertIsNotNone(new_epic)
        self.assertEqual(new_epic.key, expected_issue_key)
        self.mock_jira.create_issue.assert_called_once_with(
            project=project_key,
            summary=epic_summary,
            issuetype={"name": "Epic"}
        )

    def test_create_epic_failure(self):
        # Arrange
        project_key = "PROJ"
        epic_name = "New Epic"
        epic_summary = "Summary of New Epic"
        error_message = "Error creating epic: Something went wrong"

        # Mock the create_issue method to raise a JIRAError
        self.mock_jira.create_issue.side_effect = JIRAError(error_message)

        # Act
        new_epic = create_epic(self.mock_jira, project_key, epic_name, epic_summary)

        # Assert
        self.assertIsNone(new_epic)
        self.mock_jira.create_issue.assert_called_once_with(
            project=project_key,
            summary=epic_summary,
            issuetype={"name": "Epic"}
        )
#create story
class TestCreateStory(unittest.TestCase):
    def setUp(self):
        self.mock_jira = MagicMock()

    def test_create_story_success(self):
        # Arrange
        project_key = "PROJ"
        summary = "New Story"
        description = "Description of New Story"
        expected_issue_key = "STORY-456"

        # Mock the create_issue method to return a predefined issue key
        self.mock_jira.create_issue.return_value.key = expected_issue_key

        # Act
        new_story = create_story(self.mock_jira, project_key, summary, description)

        # Assert
        self.assertIsNotNone(new_story)
        self.assertEqual(new_story.key, expected_issue_key)
        self.mock_jira.create_issue.assert_called_once_with(
            project=project_key,
            summary=summary,
            description=description,
            issuetype={"name": "Task"}
        )

    def test_create_story_failure(self):
        # Arrange
        project_key = "PROJ"
        summary = "New Story"
        description = "Description of New Story"
        error_message = "Error creating story: Something went wrong"

        # Mock the create_issue method to raise a JIRAError
        self.mock_jira.create_issue.side_effect = JIRAError(error_message)

        # Act
        new_story = create_story(self.mock_jira, project_key, summary, description)

        # Assert
        self.assertIsNone(new_story)
        self.mock_jira.create_issue.assert_called_once_with(
            project=project_key,
            summary=summary,
            description=description,
            issuetype={"name": "Task"}
        )
#add story to epic
class TestAddStoryToEpic(unittest.TestCase):
    def setUp(self):
        self.mock_jira = MagicMock()

    def test_add_story_to_epic_success(self):
        # Arrange
        epic_key = "EPIC-123"
        story_key = "STORY-456"
        mock_epic_issue = MagicMock(id="EPIC-123_ID")
        mock_story_issue = MagicMock(id="STORY-456_ID")

        # Mock jira.issue to return MagicMock objects
        self.mock_jira.issue.side_effect = [mock_epic_issue, mock_story_issue]

        # Act
        result = add_story_to_epic(self.mock_jira, epic_key, story_key)

        # Assert
        self.assertTrue(result)
        self.mock_jira.add_issues_to_epic.assert_called_once_with("EPIC-123_ID", ["STORY-456_ID"])

    def test_add_story_to_epic_failure(self):
        # Arrange
        epic_key = "EPIC-123"
        story_key = "STORY-456"
        error_message = "Error adding story to epic: Something went wrong"

        # Mock jira.issue to raise a JIRAError
        self.mock_jira.issue.side_effect = JIRAError(error_message)

        # Act
        result = add_story_to_epic(self.mock_jira, epic_key, story_key)

        # Assert
        self.assertFalse(result)
        self.mock_jira.add_issues_to_epic.assert_not_called()
#create sprint
class TestCreateSprint(unittest.TestCase):
    @patch('requests.post')
    def test_create_sprint_success(self, mock_post):
        # Arrange
        jira_url = "https://jsl-test.atlassian.net"
        api_token = "your_api_token"
        jira_username = "your_username"
        board_id = "your_board_id"
        sprint_name = "Test Sprint"
        expected_sprint_id = "123456"

        mock_response = requests.Response()
        mock_response.status_code = 201
        mock_response.json = lambda: {"id": expected_sprint_id}  # Patching the json() method to return a predefined value
        mock_post.return_value = mock_response

        # Act
        sprint_id = create_sprint(jira_url, jira_username, api_token, board_id, sprint_name)

        # Assert
        self.assertEqual(sprint_id, expected_sprint_id)
        mock_post.assert_called_once_with(
            f"{jira_url}/rest/agile/1.0/sprint",
            json={"name": sprint_name, "originBoardId": board_id},
            auth=(jira_username, api_token)
        )

    @patch('requests.post')
    def test_create_sprint_failure(self, mock_post):
        # Arrange
        jira_url = "https://jsl-test.atlassian.net"
        api_token = "your_api_token"
        jira_username = "your_username"
        board_id = "your_board_id"
        sprint_name = "Test Sprint"

        mock_response = requests.Response()
        mock_response.status_code = 400
        mock_response._content = b"Error message"  # Set the content directly instead of using the 'text' attribute
        mock_post.return_value = mock_response

        # Act
        sprint_id = create_sprint(jira_url, jira_username, api_token, board_id, sprint_name)

        # Assert
        self.assertIsNone(sprint_id)
        mock_post.assert_called_once_with(
            f"{jira_url}/rest/agile/1.0/sprint",
            json={"name": sprint_name, "originBoardId": board_id},
            auth=(jira_username, api_token)
        )
#move issues to sprint

class TestMoveIssuesToSprint(unittest.TestCase):
    def setUp(self):
        self.mock_jira = MagicMock()

    def test_move_issues_to_sprint(self):
        # Arrange
        start_issue_key = "JST-1"
        end_issue_key = "JST-3"
        target_sprint_id = 12345

        # Mock the issue method to return a MagicMock object
        self.mock_jira.issue.side_effect = lambda x: MagicMock(key=x)

        # Act
        move_issues_to_sprint(self.mock_jira, start_issue_key, end_issue_key, target_sprint_id)

        # Assert
        expected_calls = [
            call(target_sprint_id, ['JST-1']),
            call(target_sprint_id, ['JST-2']),
            call(target_sprint_id, ['JST-3'])
        ]
        self.assertEqual(self.mock_jira.add_issues_to_sprint.call_count, 3)
        self.mock_jira.add_issues_to_sprint.assert_has_calls(expected_calls)

    def test_move_issues_to_sprint_error(self):
        # Arrange
        start_issue_key = "JST-1"
        end_issue_key = "JST-3"
        target_sprint_id = 12345

        # Mock the issue method to raise an exception
        self.mock_jira.issue.side_effect = Exception("Issue not found")

        # Act
        move_issues_to_sprint(self.mock_jira, start_issue_key, end_issue_key, target_sprint_id)

        # Assert
        self.assertEqual(self.mock_jira.add_issues_to_sprint.call_count, 0)
    #start sprint
class TestStartSprint(unittest.TestCase):
    def setUp(self):
        self.mock_jira = MagicMock()

    def test_start_sprint_success(self):
        # Arrange
        sprint_id = 123
        new_summary = "New Sprint Summary"
        start_date = datetime(2024, 2, 15)
        end_date = datetime(2024, 2, 29)

        # Mock the sprint method to return a MagicMock object
        mock_sprint = MagicMock()
        self.mock_jira.sprint.return_value = mock_sprint

        # Act
        result = start_sprint(self.mock_jira, sprint_id, new_summary, start_date, end_date)

        # Assert
        self.assertIsNotNone(result)
        mock_sprint.update.assert_called_once_with(
            name=new_summary,
            state='active',
            startDate=start_date,
            endDate=end_date
        )
        self.assertTrue(mock_sprint.started)

    def test_start_sprint_failure(self):
        # Arrange
        sprint_id = 123
        new_summary = "New Sprint Summary"
        start_date = datetime(2024, 2, 15)
        end_date = datetime(2024, 2, 29)

        # Mock the sprint method to raise a JIRAError
        self.mock_jira.sprint.side_effect = JIRAError("Sprint not found")

        # Act
        result = start_sprint(self.mock_jira, sprint_id, new_summary, start_date, end_date)

        # Assert
        self.assertIsNone(result)
        self.mock_jira.sprint.assert_called_once_with(sprint_id)


if __name__ == "__main__":
    unittest.main()
