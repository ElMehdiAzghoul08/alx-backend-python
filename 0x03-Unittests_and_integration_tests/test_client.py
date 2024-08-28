#!/usr/bin/env python3
"""Test client module"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient class"""

    @parameterized.expand([
        ('google',),
        ('abc',)
    ])
    @patch('client.get_json')
    def test_org(self, input, mock_get_json):
        """Test org method"""
        test_class = GithubOrgClient(input)
        test_class.org()
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{input}")

    def test_public_repos_url(self):
        """Test _public_repos_url"""
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            payload = {
                "repos_url": "https://api.github.com/orgs/testorg/repos"}
            mock_org.return_value = payload
            test_class = GithubOrgClient('testorg')
            result = test_class._public_repos_url
            self.assertEqual(result, payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos method"""
        payload = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = (
                "https://api.github.com/orgs/testorg/repos")
            test_class = GithubOrgClient('testorg')
            result = test_class.public_repos()

            expected = [item["name"] for item in payload]
            self.assertEqual(result, expected)

            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license method"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class"""

    @classmethod
    def setUpClass(cls):
        """Set up class"""
        cls.get_patcher = patch('requests.get')
        cls.mock = cls.get_patcher.start()
        cls.mock.return_value.json.side_effect = [
            cls.org_payload, cls.repos_payload,
            cls.org_payload, cls.repos_payload
        ]

    @classmethod
    def tearDownClass(cls):
        """Tear down class"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public repos"""
        test_class = GithubOrgClient("google")
        self.assertEqual(test_class.org, self.org_payload)
        self.assertEqual(test_class.repos_payload, self.repos_payload)
        self.assertEqual(test_class.public_repos(), self.expected_repos)
        self.assertEqual(test_class.public_repos("XLICENSE"), [])
        self.mock.assert_called()

    def test_public_repos_with_license(self):
        """Test repos license"""
        test_class = GithubOrgClient("google")
        self.assertEqual(test_class.public_repos(), self.expected_repos)
        self.assertEqual(test_class.public_repos("XLICENSE"), [])
        self.assertEqual(
            test_class.public_repos(license="apache-2.0"), self.apache2_repos)
        self.mock.assert_called()


if __name__ == '__main__':
    unittest.main()
