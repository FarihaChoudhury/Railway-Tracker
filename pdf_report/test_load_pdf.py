""" Unit tests to test load PDF functions. """

import unittest
from unittest.mock import MagicMock, patch
from os import environ
from io import BytesIO
from datetime import datetime
from email.mime.multipart import MIMEMultipart

from botocore.exceptions import ClientError
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

from load_pdf import (
    get_connection,
    get_cursor,
    get_subscribers,
    create_ses_client,
    send_email,
    get_s3_client,
    upload_pdf_to_s3
)


@patch.dict(
    environ,
    {
        "DB_IP": "localhost",
        "DB_NAME": "test_db",
        "DB_USERNAME": "test_username",
        "DB_PASSWORD": "test_password",
        "DB_PORT": "test_port",
        "ACCESS_KEY_ID": 'fake_access_key',
        'SECRET_ACCESS_KEY': 'fake_secret_key'
    },
)
class TestLoadPdf(unittest.TestCase):
    """ Tests for loading PDF into email attachment and to S3 bucket. """

    @patch('load_pdf.get_cursor')
    def test_successful_get_subscribers(self, mock_get_cursor):
        """ Tests retrieves list of subscribers from database successfully. """

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'email': 'test1@example.com'}, {'email': 'test2@example.com'}]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        conn = MagicMock()
        result = get_subscribers(conn)

        self.assertEqual(result, ['test1@example.com', 'test2@example.com'])
        mock_cursor.execute.assert_called_once_with(
            "SELECT email FROM subscriber;")
        mock_cursor.fetchall.assert_called_once()

    @patch('load_pdf.client')
    @patch('load_pdf.environ', {'ACCESS_KEY_ID': 'fake_access_key', 'SECRET_ACCESS_KEY': 'fake_secret_key'})
    def test_successful_ses_client_creation(self, mock_boto_client):
        """ Tests creates SES Client successfully. """

        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        result = create_ses_client()

        self.assertEqual(result, mock_client)
        mock_boto_client.assert_called_once_with(
            "ses",
            region_name="eu-west-2",
            aws_access_key_id='fake_access_key',
            aws_secret_access_key='fake_secret_key'
        )

    @patch('load_pdf.client')
    @patch('load_pdf.environ', {'ACCESS_KEY_ID': 'fake_access_key', 'SECRET_ACCESS_KEY': 'fake_secret_key'})
    def test_create_ses_client_failure(self, mock_boto_client):
        """ Tests creates SES Client unsuccessfully. """

        mock_boto_client.side_effect = ClientError(
            {"Error": {"Code": "InvalidClientTokenId",
                       "Message": "The security token included in the request is invalid"}},
            "CreateClient"
        )

        with self.assertRaises(RuntimeError) as context_manager:
            create_ses_client()

        self.assertIn(
            "Error creating SES client: An error occurred (InvalidClientTokenId)", str(context_manager.exception))

    def test_successful_email_send(self):
        """ Tests sends email through SES Client successfully. """

        mock_ses_client = MagicMock()
        mock_ses_client.send_raw_email.return_value = {
            "MessageId": "fake-message-id"}

        test_sender = "test@example.com"
        test_subscribers = ["subscriber1@example.com",
                            "subscriber2@example.com"]
        msg = MIMEMultipart()

        send_email(mock_ses_client, test_sender, test_subscribers, msg)

        calls = [
            unittest.mock.call(
                Source=test_sender,
                Destinations=[subscriber],
                RawMessage={"Data": msg.as_string()},
            ) for subscriber in test_subscribers
        ]
        mock_ses_client.send_raw_email.assert_has_calls(calls)

    @patch('load_pdf.client')
    @patch('load_pdf.environ', {'ACCESS_KEY_ID': 'fake_access_key', 'SECRET_ACCESS_KEY': 'fake_secret_key'})
    def test_successful_get_s3_client(self, mock_boto_client):
        """ Tests creates S3 Client successfully. """

        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        result = get_s3_client()

        self.assertEqual(result, mock_client)
        mock_boto_client.assert_called_once_with(
            's3',
            aws_access_key_id='fake_access_key',
            aws_secret_access_key='fake_secret_key')

    @patch('load_pdf.get_s3_client')
    @patch('load_pdf.datetime')
    @patch.dict('load_pdf.environ', {'S3_BUCKET_NAME': 'test-bucket'})
    def test_upload_pdf_to_s3_successful(self, mock_datetime, mock_get_s3_client):
        """ Tests uploads PDF file to S3 successfully. """

        mock_s3_client = MagicMock()
        mock_get_s3_client.return_value = mock_s3_client
        mock_datetime.now.return_value = '20240101'

        test_report_filename = 'test'
        test_bucket = 'test-bucket'
        test_s3_file_name = f"{test_report_filename}_{mock_datetime.now()}.pdf"

        upload_pdf_to_s3(test_report_filename)

        mock_s3_client.upload_file.assert_called_once_with(
            test_report_filename, test_bucket, test_s3_file_name)
