""" PDF report pipeline generates a PDF report of yesterday's UK railway performance,
    emails to subscribed users and stores in S3 bucket. """

import logging
from dotenv import load_dotenv

from transform_pdf import transform_pdf
from load_pdf import load_pdf

REPORT_FILENAME = "/tmp/performance_report.pdf"


def main(_event, _context):
    """ Lambda handler to run the PDF report pipeline. """

    logging.getLogger().setLevel(logging.INFO)
    load_dotenv()
    try:
        logging.info("Report PDF pipeline has started")

        transform_pdf(REPORT_FILENAME)
        logging.info(
            "Extracting & Transforming to create a PDF Summary Report complete.")

        load_pdf(REPORT_FILENAME)
        logging.info("Loading to S3 and sending emails complete.")

    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error(
            "An error occurred during the PDF Report pipeline execution: %s", e)

    logging.info("Report pipeline has ended.")


if __name__ == "__main__":
    main(None, None)
