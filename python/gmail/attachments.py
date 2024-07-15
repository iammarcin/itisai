import os
from datetime import datetime

from main import *


def process_boarding_passes():
    # Authenticate Gmail
    service = authenticate_gmail()
    if not service:
        print("Authentication failed. Exiting.")
        return

    # Define search queries
    queries = [
        'subject:"boarding pass" after:2023/12/31 before:2025/01/01',
        'subject:"boarding card" after:2023/12/31 before:2025/01/01',
        'subject:"flight ticket" after:2023/12/31 before:2025/01/01',
        'from:ryanair.com after:2023/12/31 before:2025/01/01',
        'from:easyjet.com after:2023/12/31 before:2025/01/01',
        'from:vueling.com after:2023/12/31 before:2025/01/01',
        'from:"iberia" after:2023/12/31 before:2025/01/01',
        'from:"wizzair" after:2023/12/31 before:2025/01/01',
        'from:"sata" after:2023/12/31 before:2025/01/01',
        'from:tap.pt after:2023/12/31 before:2025/01/01'
    ]

    all_attachments = []
    processed_ids = set()

    for query in queries:
        emails = search_emails(service, query=query, max_results=300)

        for email in emails:
            if email['id'] not in processed_ids:
                processed_ids.add(email['id'])
                attachments = download_attachments(service, email)
                all_attachments.extend(attachments)

    if all_attachments:
        # Send email with all attachments
        sender = os.getenv('EMAIL_SENDER')
        recipient = os.getenv('EMAIL_TO')
        print("Sender: ", sender)
        sender = sender
        to = recipient
        subject = "Boarding Passes for 2024 Flights"
        message_text = "Please find attached all boarding passes for flights in 2024."

        sent_message = send_email(service, sender, to, subject, message_text, attachments=all_attachments)

        if sent_message:
            print(f"Email sent successfully. Message ID: {sent_message['id']}")
        else:
            print("Failed to send email.")

        # Clean up temporary files
        for attachment in all_attachments:
            if os.path.exists(attachment):
                os.remove(attachment)
    else:
        print("No boarding passes found for 2024 flights.")


if __name__ == "__main__":
    process_boarding_passes()
