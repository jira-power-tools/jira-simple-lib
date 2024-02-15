import unittest
from unittest.mock import MagicMock, patch
from jirasimplelib import create_jira_connection

class TestJiraConnection(unittest.TestCase):
    @patch('jirasimplelib.JIRA')
    def test_create_jira_connection_success(self, mock_jira):
        # Set up mock JIRA instance
        mock_instance = MagicMock()
        mock_jira.return_value = mock_instance

        # Call the function under test
        jira_url = "https://jsl-test.atlassian.net"
        api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
        user = "info@test01.verituslabs.net"
        result = create_jira_connection(jira_url, user, api_token)

        # Assertions
        self.assertEqual(result, mock_instance)

    @patch('jirasimplelib.JIRA', side_effect=Exception("Test Exception"))
    def test_create_jira_connection_failure(self, mock_jira):
        # Call the function under test
        jira_url = "https://jsl-test.atlassian.net"
        api_token = "ATATT3xFfGF0H-GarbaOXH5XrBh5TaLhnv-QZ9ygdWpuemV737fsZF7enXxQuV7uU0QLvpqWk3GYOAorlwMaujiCsgwfND5rqanZOMm9ac8BJUYQBqz3rVyX8xhu9sgvbZ-0E2jI3_nR_ePruAJdocVK9jIctyVeqWl5x1NSOYawM79lW9Yo-ak=B918462D"
        user = "info@test01.verituslabs.net"
        result = create_jira_connection(jira_url, user, api_token)

        # Assertions
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
