"""Retrieves information from the National Rail API."""

from os import environ as ENV
import logging

from requests import get
from requests.exceptions import RequestException


def get_data_from_api(apikey: str) -> str | None:
    """Retrieves data from the National Rail API and returns the response as a string."""
    headers = {
        "x-apikey": apikey,
        "User-Agent": "",
    }

    base_url = "https://api1.raildata.org.uk/1010-knowlegebase-incidents-xml-feed1_0/incidents.xml"

    try:
        response = get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        logging.error("Error occurred while fetching data from API: %s", e)
        return None


def save_data_to_file(data: str, filename: str) -> None:
    """Saves the provided data to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(data)


def get_national_rail_data(output_file: str) -> None:
    """Retrieves data from the National Rail API and saves it to a file."""

    data = get_data_from_api(ENV["NATIONAL_RAIL_API_KEY"])
    if data:
        save_data_to_file(data, output_file)
    else:
        logging.error("Failed to retrieve data from the API.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    get_national_rail_data("data.xml")
