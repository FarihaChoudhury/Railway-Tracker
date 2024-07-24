""" Loads the PDF summary report of RealTimeTrains data into an S3 bucket. """
from os import environ, path
import logging
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime

from boto3 import client
from botocore.exceptions import NoCredentialsError
from psycopg2 import connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor
import psycopg2
import psycopg2.extras
import botocore.exceptions


def get_s3_client() -> client:
    """ Returns s3 client. """
    load_dotenv()
    try:
        s3_client = client('s3',
                           aws_access_key_id=environ['AWS_ACCESS_KEY'],
                           aws_secret_access_key=environ['AWS_SECRET_KEY'])
        return s3_client
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


def upload_pdf_data_to_s3(s3: client, bucket_name: str, s3_filename: str, pdf: BytesIO):
    """ Uploads pdf of summary report to S3 bucket. """

    s3.upload_fileobj(pdf, bucket_name, s3_filename)
    logging.info(f"pdf file uploaded: {s3_filename}")


def upload_pdf_to_s3():
    """ Uploads a PDF file from local directory into S3 bucket. """
    s3 = get_s3_client()
    bucket = environ['S3_BUCKET_NAME']
    prefix = datetime.now()
    local_file = 'report.pdf'
    s3_file_name = f"{prefix}_{local_file}"

    try:
        s3.upload_file(local_file, bucket, s3_file_name)
        logging.info("Upload Successful: %s, to bucket: %s",
                     s3_file_name, bucket)
    except FileNotFoundError:
        logging.error("The file was not found.")
    except Exception as e:
        logging.error(
            "Error occurred when connecting and uploading to S3 bucket.")


"""" EMAIL REPORTS """


def get_connection() -> connection:
    """ Retrieves connection and returns it. """
    load_dotenv()
    return connect(
        user=environ['DB_USERNAME'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_IP'],
        port=environ['DB_PORT'],
        dbname=environ['DB_NAME']
    )


def get_cursor(conn: connection) -> cursor:
    """ Retrieves cursor and returns it. """
    return conn.cursor(cursor_factory=RealDictCursor)


def get_subscribers(conn: connection) -> list:
    """ Queries the subscriber table, returning a list of all subscriber emails."""

    recipients = []
    try:
        with get_cursor(conn) as cursor:
            cursor.execute("SELECT email FROM subscriber;")
            subscribers = cursor.fetchall()
            recipients = [subscriber['email'] for subscriber in subscribers]

    except psycopg2.Error as e:
        logging.error("Error fetching subscribers: %s", e)

    finally:
        cursor.close()

    return recipients


def create_ses_client() -> client:
    """ Creates and returns an SES client using AWS access keys."""

    try:
        return client(
            "ses",
            region_name="eu-west-2",
            aws_access_key_id=environ['AWS_ACCESS_KEY'],
            aws_secret_access_key=environ['AWS_SECRET_KEY']
        )
    except botocore.exceptions.ClientError as e:
        raise RuntimeError(f"Error creating SES client: {e}") from e


# def send_email_ses(ses_client: client, )


def email_subscribers_report():

    subscribers = get_subscribers(get_connection())
    ses_client = create_ses_client()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    # upload_pdf_to_s3()
    get_subscribers(get_connection())
