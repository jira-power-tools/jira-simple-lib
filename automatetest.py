import unittest
from jira import JIRAError
from unittest.mock import MagicMock, patch
from run_test import create_jira_connection, create_jira_project, create_epic, create_story, add_story_to_epic
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





if __name__ == "__main__":
    unittest.main()
