import unittest
from unittest.mock import MagicMock, patch
from run_test import create_jira_connection, create_jira_project
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


if __name__ == "__main__":
    unittest.main()
