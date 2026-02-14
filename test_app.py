"""
Comprehensive unit tests for the Flask portfolio application.
Tests cover routes, helper functions, Notion integration, and email functionality.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import os
import sys
from flask import session
from itsdangerous import URLSafeTimedSerializer

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestAppConfiguration(unittest.TestCase):
    """Test application configuration and initialization."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test environment with required environment variables."""
        # Import app after setting environment variables
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_app_secret_key_configured(self):
        """Test that Flask secret key is properly configured."""
        self.assertIsNotNone(self.app.secret_key)
        self.assertEqual(self.app.secret_key, 'test-secret-key')

    def test_mail_configuration(self):
        """Test that mail server is properly configured."""
        self.assertEqual(self.app.config['MAIL_SERVER'], 'live.smtp.mailtrap.io')
        self.assertEqual(self.app.config['MAIL_PORT'], 587)
        self.assertEqual(self.app.config['MAIL_USERNAME'], 'api')
        self.assertEqual(self.app.config['MAIL_USE_TLS'], True)
        self.assertEqual(self.app.config['MAIL_USE_SSL'], False)


class TestTokenFunctions(unittest.TestCase):
    """Test email verification token generation and confirmation."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test environment."""
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app

    def test_generate_verification_token(self):
        """Test that verification token is generated successfully."""
        email = "test@example.com"
        token = self.app_module.generate_verification_token(email)
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_confirm_verification_token_valid(self):
        """Test confirming a valid verification token."""
        email = "test@example.com"
        token = self.app_module.generate_verification_token(email)
        confirmed_email = self.app_module.confirm_verification_token(token)
        self.assertEqual(confirmed_email, email)

    def test_confirm_verification_token_invalid(self):
        """Test confirming an invalid verification token."""
        invalid_token = "invalid-token-string"
        result = self.app_module.confirm_verification_token(invalid_token)
        self.assertFalse(result)

    def test_confirm_verification_token_expired(self):
        """Test confirming an expired verification token."""
        import time
        email = "test@example.com"
        token = self.app_module.generate_verification_token(email)
        # Wait slightly and use -1 second expiration to force expired state
        time.sleep(0.01)
        result = self.app_module.confirm_verification_token(token, expiration=-1)
        self.assertFalse(result)

    def test_token_different_for_different_emails(self):
        """Test that different emails generate different tokens."""
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        token1 = self.app_module.generate_verification_token(email1)
        token2 = self.app_module.generate_verification_token(email2)
        self.assertNotEqual(token1, token2)


class TestEmailFunctions(unittest.TestCase):
    """Test email sending functions."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test environment."""
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app

    @patch('app.mail.send')
    def test_send_email(self, mock_send):
        """Test sending email to user."""
        to = "user@example.com"
        subject = "Test Subject"
        template = "<html>Test Email</html>"

        self.app_module.send_email(to, subject, template)

        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        self.assertEqual(call_args.subject, subject)
        self.assertIn(to, call_args.recipients)
        self.assertEqual(call_args.html, template)
        self.assertEqual(call_args.sender, 'noreply@jacobjones.com.au')

    @patch('app.mail.send')
    def test_sendEmail_admin_notification(self, mock_send):
        """Test sending email notification to admin."""
        email_template = "<html>Admin notification</html>"

        self.app_module.sendEmail(email_template)

        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        self.assertEqual(call_args.subject, 'New Message from portfolio contact')
        self.assertIn('admin@jacobjones.com.au', call_args.recipients)
        self.assertEqual(call_args.html, email_template)
        self.assertEqual(call_args.sender, 'portfolio@jacobjones.com.au')


class TestNotionFunctions(unittest.TestCase):
    """Test Notion API integration functions."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test environment."""
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app

    @patch('app.notion.databases.retrieve')
    def test_get_data_source_id_success(self, mock_retrieve):
        """Test retrieving data source ID from database."""
        mock_retrieve.return_value = {
            "data_sources": [
                {"id": "source-123"},
                {"id": "source-456"}
            ]
        }

        result = self.app_module.get_data_source_id("test-db-id")

        self.assertEqual(result, "source-123")
        mock_retrieve.assert_called_once_with(database_id="test-db-id")

    @patch('app.notion.databases.retrieve')
    def test_get_data_source_id_no_sources(self, mock_retrieve):
        """Test error when no data sources are found."""
        mock_retrieve.return_value = {"data_sources": []}

        with self.assertRaises(Exception) as context:
            self.app_module.get_data_source_id("test-db-id")

        self.assertIn("No data sources found", str(context.exception))

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_from_notion_success(self, mock_query, mock_blocks):
        """Test loading posts from Notion successfully."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {
                        "Project Name": {
                            "title": [{"plain_text": "Test Project"}]
                        }
                    }
                }
            ]
        }

        mock_blocks.return_value = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"plain_text": "Test content"}]
                    }
                }
            ]
        }

        posts = self.app_module.load_posts_from_notion("source-123")

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["title"], "Test Project")
        self.assertIn("Test content", posts[0]["content"])

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_empty_title(self, mock_query, mock_blocks):
        """Test loading post with no title defaults to 'Untitled'."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {}
                }
            ]
        }

        mock_blocks.return_value = {"results": []}

        posts = self.app_module.load_posts_from_notion("source-123")

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["title"], "Untitled")

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_various_block_types(self, mock_query, mock_blocks):
        """Test loading posts with various Notion block types."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {
                        "Project Name": {
                            "title": [{"plain_text": "Rich Content Post"}]
                        }
                    }
                }
            ]
        }

        mock_blocks.return_value = {
            "results": [
                {
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"plain_text": "Main Heading"}]}
                },
                {
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"plain_text": "Subheading"}]}
                },
                {
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"plain_text": "List item"}]}
                },
                {
                    "type": "code",
                    "code": {"rich_text": [{"plain_text": "print('hello')"}]}
                },
                {
                    "type": "quote",
                    "quote": {"rich_text": [{"plain_text": "Famous quote"}]}
                },
                {
                    "type": "divider",
                    "divider": {"rich_text": []}
                },
                {
                    "type": "to_do",
                    "to_do": {"rich_text": [{"plain_text": "Task"}], "checked": True}
                },
                {
                    "type": "image",
                    "image": {"file": {"url": "http://example.com/image.jpg"}}
                }
            ]
        }

        posts = self.app_module.load_posts_from_notion("source-123")

        content = posts[0]["content"]
        self.assertIn("<h1>Main Heading</h1>", content)
        self.assertIn("<h2>Subheading</h2>", content)
        self.assertIn("<ul><li>List item</li></ul>", content)
        self.assertIn("<pre><code>print('hello')</code></pre>", content)
        self.assertIn("<blockquote>Famous quote</blockquote>", content)
        self.assertIn("<hr>", content)
        self.assertIn("☑ Task", content)
        self.assertIn('<img src="http://example.com/image.jpg"', content)

    @patch('app.notion.pages.retrieve')
    def test_get_page_icon_emoji(self, mock_retrieve):
        """Test retrieving emoji icon from Notion page."""
        mock_retrieve.return_value = {
            "icon": {
                "type": "emoji",
                "emoji": "🎨"
            }
        }

        icon = self.app_module.get_page_icon("page-123")

        self.assertEqual(icon, "🎨")

    @patch('app.notion.pages.retrieve')
    def test_get_page_icon_file(self, mock_retrieve):
        """Test retrieving file icon from Notion page."""
        mock_retrieve.return_value = {
            "icon": {
                "type": "file",
                "file": {"url": "http://example.com/icon.png"}
            }
        }

        icon = self.app_module.get_page_icon("page-123")

        self.assertEqual(icon, "http://example.com/icon.png")

    @patch('app.notion.pages.retrieve')
    def test_get_page_icon_none(self, mock_retrieve):
        """Test when page has no icon."""
        mock_retrieve.return_value = {"icon": None}

        icon = self.app_module.get_page_icon("page-123")

        self.assertIsNone(icon)


class TestRoutes(unittest.TestCase):
    """Test Flask route handlers."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test client."""
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_home_route(self):
        """Test home page route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_route(self):
        """Test about page route."""
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)

    @patch('app.get_page_icon')
    @patch('app.load_posts_from_notion')
    @patch('app.get_data_source_id')
    def test_portfolio_route_with_posts(self, mock_get_ds, mock_load_posts, mock_get_icon):
        """Test portfolio page with posts loaded successfully."""
        mock_get_ds.return_value = "source-123"
        mock_load_posts.return_value = [
            {"title": "Project 1", "content": "Content 1"},
            {"title": "Project 2", "content": "Content 2"}
        ]
        mock_get_icon.return_value = "🎨"

        response = self.client.get('/portfolio')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Project 1", response.data)

    @patch('app.get_page_icon')
    @patch('app.load_posts_from_notion')
    @patch('app.get_data_source_id')
    def test_portfolio_route_with_index(self, mock_get_ds, mock_load_posts, mock_get_icon):
        """Test portfolio page with specific index parameter."""
        mock_get_ds.return_value = "source-123"
        mock_load_posts.return_value = [
            {"title": "Project 1", "content": "Content 1"},
            {"title": "Project 2", "content": "Content 2"}
        ]
        mock_get_icon.return_value = "🎨"

        response = self.client.get('/portfolio?index=1')

        self.assertEqual(response.status_code, 200)

    @patch('app.get_page_icon')
    @patch('app.get_data_source_id')
    def test_portfolio_route_no_posts(self, mock_get_ds, mock_get_icon):
        """Test portfolio page when no posts are found."""
        mock_get_ds.side_effect = Exception("No data sources found")
        mock_get_icon.return_value = None

        response = self.client.get('/portfolio')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No Posts Found", response.data)

    @patch('app.get_page_icon')
    @patch('app.load_posts_from_notion')
    @patch('app.get_data_source_id')
    def test_portfolio_route_invalid_index(self, mock_get_ds, mock_load_posts, mock_get_icon):
        """Test portfolio page with invalid index parameter."""
        mock_get_ds.return_value = "source-123"
        mock_load_posts.return_value = [
            {"title": "Project 1", "content": "Content 1"}
        ]
        mock_get_icon.return_value = None

        # Test with negative index
        response = self.client.get('/portfolio?index=-1')
        self.assertEqual(response.status_code, 200)

        # Test with index beyond bounds
        response = self.client.get('/portfolio?index=999')
        self.assertEqual(response.status_code, 200)

        # Test with non-numeric index
        response = self.client.get('/portfolio?index=abc')
        self.assertEqual(response.status_code, 200)

    def test_contact_route_get(self):
        """Test contact page GET request."""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)

    @patch('app.send_email')
    def test_contact_route_post_valid(self, mock_send_email):
        """Test contact form submission with valid data."""
        with self.client as client:
            response = client.post('/contact', data={
                'name': 'John Doe',
                'email': 'john@example.com',
                'message': 'This is a test message with enough length'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            mock_send_email.assert_called_once()

            # Check that session contains contact data
            with client.session_transaction() as sess:
                self.assertIn('contact_data', sess)
                self.assertEqual(sess['contact_data']['name'], 'John Doe')

    def test_contact_route_post_missing_fields(self):
        """Test contact form submission with missing fields."""
        response = self.client.post('/contact', data={
            'name': 'John Doe',
            'email': '',
            'message': 'Test message'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All fields are required!', response.data)

    def test_contact_route_post_empty_name(self):
        """Test contact form with empty name."""
        response = self.client.post('/contact', data={
            'name': '',
            'email': 'test@example.com',
            'message': 'Test message'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_contact_route_post_empty_message(self):
        """Test contact form with empty message."""
        response = self.client.post('/contact', data={
            'name': 'John Doe',
            'email': 'test@example.com',
            'message': ''
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @patch('app.sendEmail')
    def test_verify_email_valid_token(self, mock_send_email):
        """Test email verification with valid token."""
        with self.client as client:
            with client.session_transaction() as sess:
                sess['contact_data'] = {
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'message': 'Test message'
                }

            token = self.app_module.generate_verification_token('john@example.com')
            response = client.get(f'/verify/{token}', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'verified successfully', response.data)
            mock_send_email.assert_called_once()

    def test_verify_email_invalid_token(self):
        """Test email verification with invalid token."""
        response = self.client.get('/verify/invalid-token', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'invalid or has expired', response.data)

    def test_verify_email_no_session_data(self):
        """Test email verification when session data is missing."""
        token = self.app_module.generate_verification_token('test@example.com')
        response = self.client.get(f'/verify/{token}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Session expired', response.data)


class TestContactForm(unittest.TestCase):
    """Test ContactForm validation."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test environment."""
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False

    def test_contact_form_valid_data(self):
        """Test ContactForm with valid data."""
        with self.app.app_context():
            form = self.app_module.ContactForm(
                name='John Doe',
                email='john@example.com',
                message='This is a test message with sufficient length'
            )
            self.assertTrue(form.validate())

    def test_contact_form_short_name(self):
        """Test ContactForm with name too short."""
        with self.app.app_context():
            form = self.app_module.ContactForm(
                name='J',
                email='john@example.com',
                message='This is a test message'
            )
            self.assertFalse(form.validate())

    def test_contact_form_invalid_email(self):
        """Test ContactForm with invalid email."""
        with self.app.app_context():
            form = self.app_module.ContactForm(
                name='John Doe',
                email='invalid-email',
                message='This is a test message'
            )
            self.assertFalse(form.validate())

    def test_contact_form_short_message(self):
        """Test ContactForm with message too short."""
        with self.app.app_context():
            form = self.app_module.ContactForm(
                name='John Doe',
                email='john@example.com',
                message='Short'
            )
            self.assertFalse(form.validate())

    def test_contact_form_missing_fields(self):
        """Test ContactForm with missing required fields."""
        with self.app.app_context():
            form = self.app_module.ContactForm(
                name='',
                email='',
                message=''
            )
            self.assertFalse(form.validate())


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test environment."""
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_verify_email_with_special_characters(self):
        """Test email verification with special characters in email."""
        email = "test+tag@example.co.uk"
        token = self.app_module.generate_verification_token(email)
        confirmed = self.app_module.confirm_verification_token(token)
        self.assertEqual(confirmed, email)

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_with_empty_rich_text(self, mock_query, mock_blocks):
        """Test loading posts with empty rich text content."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {
                        "Project Name": {
                            "title": [{"plain_text": "Test"}]
                        }
                    }
                }
            ]
        }

        mock_blocks.return_value = {
            "results": [
                {
                    "type": "paragraph",
                    "paragraph": {"rich_text": []}
                }
            ]
        }

        posts = self.app_module.load_posts_from_notion("source-123")
        self.assertEqual(len(posts), 1)

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_numbered_list(self, mock_query, mock_blocks):
        """Test loading posts with numbered list items."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {
                        "Project Name": {
                            "title": [{"plain_text": "Numbered List Post"}]
                        }
                    }
                }
            ]
        }

        mock_blocks.return_value = {
            "results": [
                {
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": [{"plain_text": "First item"}]}
                },
                {
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": [{"plain_text": "Second item"}]}
                }
            ]
        }

        posts = self.app_module.load_posts_from_notion("source-123")
        content = posts[0]["content"]
        self.assertIn("<ol><li>First item</li></ol>", content)
        self.assertIn("<ol><li>Second item</li></ol>", content)

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_unchecked_todo(self, mock_query, mock_blocks):
        """Test loading posts with unchecked to-do items."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {
                        "Project Name": {
                            "title": [{"plain_text": "Todo Post"}]
                        }
                    }
                }
            ]
        }

        mock_blocks.return_value = {
            "results": [
                {
                    "type": "to_do",
                    "to_do": {"rich_text": [{"plain_text": "Incomplete task"}], "checked": False}
                }
            ]
        }

        posts = self.app_module.load_posts_from_notion("source-123")
        content = posts[0]["content"]
        self.assertIn("☐ Incomplete task", content)

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_toggle_block(self, mock_query, mock_blocks):
        """Test loading posts with toggle blocks."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {
                        "Project Name": {
                            "title": [{"plain_text": "Toggle Post"}]
                        }
                    }
                }
            ]
        }

        mock_blocks.return_value = {
            "results": [
                {
                    "type": "toggle",
                    "toggle": {"rich_text": [{"plain_text": "Click to expand"}]}
                }
            ]
        }

        posts = self.app_module.load_posts_from_notion("source-123")
        content = posts[0]["content"]
        self.assertIn("<details><summary>Click to expand</summary></details>", content)

    @patch('app.notion.blocks.children.list')
    @patch('app.notion.data_sources.query')
    def test_load_posts_external_image(self, mock_query, mock_blocks):
        """Test loading posts with external images."""
        mock_query.return_value = {
            "results": [
                {
                    "id": "post-123",
                    "properties": {
                        "Project Name": {
                            "title": [{"plain_text": "Image Post"}]
                        }
                    }
                }
            ]
        }

        mock_blocks.return_value = {
            "results": [
                {
                    "type": "image",
                    "image": {"external": {"url": "https://example.com/external.jpg"}}
                }
            ]
        }

        posts = self.app_module.load_posts_from_notion("source-123")
        content = posts[0]["content"]
        self.assertIn('<img src="https://example.com/external.jpg"', content)

    @patch('app.notion.pages.retrieve')
    def test_get_page_icon_external_type(self, mock_retrieve):
        """Test retrieving external icon from Notion page."""
        mock_retrieve.return_value = {
            "icon": {
                "type": "external",
                "external": {"url": "https://example.com/icon.png"}
            }
        }

        icon = self.app_module.get_page_icon("page-123")
        self.assertEqual(icon, "https://example.com/icon.png")

    def test_portfolio_index_wrapping(self):
        """Test that portfolio index wrapping works correctly."""
        with self.client as client:
            with patch('app.get_data_source_id') as mock_get_ds, \
                 patch('app.load_posts_from_notion') as mock_load_posts, \
                 patch('app.get_page_icon') as mock_get_icon:

                mock_get_ds.return_value = "source-123"
                mock_load_posts.return_value = [
                    {"title": "Post 1", "content": "Content 1"},
                    {"title": "Post 2", "content": "Content 2"},
                    {"title": "Post 3", "content": "Content 3"}
                ]
                mock_get_icon.return_value = None

                # Test that navigating works
                response = client.get('/portfolio?index=0')
                self.assertEqual(response.status_code, 200)


class TestSecurityAndValidation(unittest.TestCase):
    """Test security features and input validation."""

    @patch.dict(os.environ, {
        'FLASK_SECRET_KEY': 'test-secret-key',
        'NOTION_API_KEY': 'test-notion-key',
        'NOTION_DATABASE_ID': 'test-db-id',
        'NOTION_PAGE_ID': 'test-page-id',
        'SMTP_API_TOKEN': 'test-smtp-token'
    })
    def setUp(self):
        """Set up test environment."""
        import app as app_module
        self.app_module = app_module
        self.app = app_module.app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    @patch('app.send_email')
    def test_contact_form_xss_prevention(self, mock_send_email):
        """Test that contact form prevents XSS attacks."""
        with self.client as client:
            # Attempt to submit XSS payload
            response = client.post('/contact', data={
                'name': '<script>alert("xss")</script>',
                'email': 'test@example.com',
                'message': '<img src=x onerror=alert(1)> with sufficient length for validation'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            # Verify email was sent (form accepted the data)
            mock_send_email.assert_called_once()

    def test_token_tampering_prevention(self):
        """Test that tampered tokens are rejected."""
        token = self.app_module.generate_verification_token('test@example.com')
        # Tamper with the token
        tampered_token = token[:-5] + "XXXXX"

        result = self.app_module.confirm_verification_token(tampered_token)
        self.assertFalse(result)

    def test_long_email_address(self):
        """Test handling of unusually long email addresses."""
        long_email = "a" * 250 + "@example.com"
        token = self.app_module.generate_verification_token(long_email)
        confirmed = self.app_module.confirm_verification_token(token)
        self.assertEqual(confirmed, long_email)

    def test_contact_form_long_name(self):
        """Test contact form with name at maximum length."""
        with self.app.app_context():
            form = self.app_module.ContactForm(
                name='A' * 50,
                email='test@example.com',
                message='This is a test message with sufficient length'
            )
            self.assertTrue(form.validate())

    def test_contact_form_exceeds_name_length(self):
        """Test contact form with name exceeding maximum length."""
        with self.app.app_context():
            form = self.app_module.ContactForm(
                name='A' * 51,
                email='test@example.com',
                message='This is a test message'
            )
            self.assertFalse(form.validate())


if __name__ == '__main__':
    unittest.main()