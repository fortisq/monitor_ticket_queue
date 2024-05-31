import requests
import datetime
import json
import time
import itertools
import sys

# Replace with your SyncroMSP API key and subdomain
API_KEY = 'your_api_key'
SUBDOMAIN = 'your_subdomain'

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "accept": "application/json",
    "Content-Type": "application/json"
}

# Function to handle API responses and errors
def handle_response(response):
    try:
        response_data = response.json()
        if response.status_code in [200, 201]:
            return response_data
        else:
            print(f"Error {response.status_code}: {response_data}")
            return None
    except ValueError:
        print("Response is not valid JSON")
        print(response.text)
        return None

# Function to retrieve new tickets
def get_new_tickets():
    response = requests.get(f'https://{SUBDOMAIN}.syncromsp.com/api/v1/tickets?status=New', headers=headers)
    return handle_response(response)

# Function to add a time entry to a ticket
def add_time_entry(ticket_id):
    current_time = datetime.datetime.utcnow()
    start_time = current_time.isoformat() + "Z"
    end_time = (current_time + datetime.timedelta(hours=1)).isoformat() + "Z"
    time_entry_data = {
        "start_at": start_time,
        "end_at": end_time,
        "duration_minutes": 60,
        "user_id": 0,  # Adjust the user_id if necessary
        "notes": "Adding 1 hour of work.",
        "product_id": 0  # Adjust the product_id if necessary
    }
    response = requests.post(f'https://{SUBDOMAIN}.syncromsp.com/api/v1/tickets/{ticket_id}/timer_entry', headers=headers, json=time_entry_data)
    return handle_response(response)

# Function to update the status of a ticket to 'Resolved'
def update_ticket_status(ticket_id):
    update_data = {
        "status": "Resolved"
    }
    response = requests.put(f'https://{SUBDOMAIN}.syncromsp.com/api/v1/tickets/{ticket_id}', headers=headers, json=update_data)
    return handle_response(response)

# Function to monitor the ticket queue
def monitor_ticket_queue():
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    processed_tickets = 0

    while True:
        sys.stdout.write(next(spinner) + '\r')
        sys.stdout.flush()
        new_tickets = get_new_tickets()

        if new_tickets:
            tickets = new_tickets.get('tickets', [])
            for ticket in tickets:
                ticket_id = ticket['id']
                print(f"Found new ticket: ID {ticket_id}, Subject: {ticket['subject']}, Created At: {ticket['created_at']}")

                # Add a time entry to the ticket
                time_entry_result = add_time_entry(ticket_id)
                if time_entry_result:
                    print(f"Time entry added for ticket {ticket_id}")

                    # Update the ticket status to 'Resolved'
                    status_update_result = update_ticket_status(ticket_id)
                    if status_update_result:
                        print(f"Ticket {ticket_id} status updated to 'Resolved'")
                        processed_tickets += 1
                    else:
                        print(f"Failed to update status for ticket {ticket_id}")
                else:
                    print(f"Failed to add time entry for ticket {ticket_id}")

        sys.stdout.write(f"Processed {processed_tickets} tickets so far.\r")
        sys.stdout.flush()
        time.sleep(10)  # Adjust the sleep time as needed

# Run the monitor function
monitor_ticket_queue()
