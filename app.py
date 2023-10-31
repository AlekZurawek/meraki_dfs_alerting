import requests
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define your API key, organization ID, and base URL
api_key = "x"
organization_id = "x"
base_url = "https://api.meraki.com/api/v1"

# Set up the headers for your API requests
headers = {
    "X-Cisco-Meraki-API-Key": api_key,
    "Content-Type": "application/json"
}

# Email credentials and settings
email_address = "your-gmail-address@gmail.com"
email_password = "your-app-password"
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Function to send email
def send_email(device_name, message):
    subject = f"{device_name} had a DFS event"

    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_address  # Or any other recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)
        text = msg.as_string()
        server.sendmail(email_address, email_address, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

# Function to get networks in the organization
def get_networks():
    url = f"{base_url}/organizations/{organization_id}/networks"
    response = requests.get(url, headers=headers)
    return response.json()

# Function to get events for a specific network
def get_events(network_id, event_types):
    starting_after = (datetime.utcnow() - timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    url = f"{base_url}/networks/{network_id}/events"
    params = {
        "productType": "wireless",
        "includedEventTypes[]": event_types,
        "startingAfter": starting_after
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Main loop
while True:
    networks = get_networks()

    # Filter networks with wireless devices
    wireless_networks = [network for network in networks if "wireless" in network.get("productTypes", [])]

    event_types = ["dfs_event"]

    for network in wireless_networks:
        network_id = network["id"]
        network_name = network["name"]
        events = get_events(network_id, event_types)

        if events and 'events' in events and events['events']:
            print(f"Events found for Network {network_name} ({network_id}):")
            print(events)
            send_email(network_name, str(events))
        else:
            print(f"No events found for Network {network_name} ({network_id})")

    print("\n" + "-"*50 + "\n")
    time.sleep(600)  # Wait for 10 minutes before next iteration
