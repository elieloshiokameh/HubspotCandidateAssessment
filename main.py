import requests
import json
from datetime import datetime, timedelta

# API keys and URLs
GET_KEY = "getKey"
POST_KEY = "postKey"
GET_URL = "getUrl"

POST_URL = "postUrl"



# Define a function to find the best start date for a given country
def find_best_start_date(country, partners):
    """Find the best start date for a given country.

    Args:
        country (str): The name of the country.
        partners (list): A list of dictionaries containing partner data.

    Returns:
        dict: A dictionary containing the best start date, the number of attendees, and the list of attendees for the country.
    """
    # Filter the partners by country
    country_partners = [partner for partner in partners if partner["country"] == country]

    # Create a dictionary to store the number of attendees for each possible start date
    date_attendees = {}

    # Loop through each partner in the country
    for partner in country_partners:
        # Sort the available dates in ascending order
        availability = sorted(partner["availableDates"])

        # Loop through each pair of consecutive dates
        for i in range(len(availability) - 1):
            # Get the start and end dates
            start = availability[i]
            end = availability[i + 1]

            # Check if the dates are consecutive
            if (datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days == 1:
                # Increment the number of attendees for the start date
                date_attendees[start] = date_attendees.get(start, 0) + 1

    # Initialize the best start date, the maximum number of attendees, and the list of attendees
    best_start_date = None
    max_attendees = 0
    attendees_list = []

    # Loop through each start date and its number of attendees
    for start_date, attendees in date_attendees.items():
        # Convert the start date to a datetime object
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")

        # Check if the number of attendees is greater than the maximum or equal but earlier than the best start date
        if attendees > max_attendees or (attendees == max_attendees and (best_start_date is None or start_date_obj < best_start_date)):
            # Update the best start date, the maximum number of attendees, and the list of attendees
            best_start_date = start_date_obj
            max_attendees = attendees
            attendees_list = [partner["email"] for partner in country_partners if (best_start_date + timedelta(days=1)).strftime("%Y-%m-%d") in partner["availableDates"]]

    # Convert the best start date to a string or null if none
    best_start_date_str = best_start_date.strftime("%Y-%m-%d") if best_start_date else None

    # Return a dictionary with the result for the country
    return {
        "attendeeCount": len(attendees_list),
        "attendees": attendees_list,
        "name": country,
        "startDate": best_start_date_str
    }

# Get partner data from API
try:
    response = requests.get(GET_URL)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    exit()

partners = json.loads(response.text)["partners"]

# Get a list of unique countries from partner data
countries = sorted(set(partner["country"] for partner in partners))

# Create a list to store the result for each country
result = []

# Loop through each country and find the best start date using the function defined above
for country in countries:
    result.append(find_best_start_date(country, partners))

# Format the output to match the sample output exactly
output = {
    "countries": result
}

# Post output to API
try:
    response = requests.post(POST_URL, json=output)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    exit()

print(response.content)

if response.status_code == 200:
    print("Result submitted successfully.")
else:
    print(f"Failed to submit result. Status code: {response.status_code}")
