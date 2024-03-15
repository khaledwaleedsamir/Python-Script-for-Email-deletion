import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Variable to define the scopes required
SCOPES = ['https://mail.google.com/']

def create_service():
    """Authenticate and create Gmail service."""
    creds = None

    # Load or create credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service

def delete_emails(service, query):
    """Delete emails based on query."""
    try:
        # Initialize variables for pagination
        page_token = None
        messages_deleted = 0

        # Loop through pages of results
        while True:
            # Get message IDs for the current page
            response = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
            messages = response.get('messages', [])

            if messages == []:
                print("No messages found matching the selected criteria.")
                break # Exit the loop if no matches are found
            
            if messages:
                for message in messages:
                    # Delete message
                    service.users().messages().delete(userId='me', id=message['id']).execute()
                    messages_deleted += 1

                print(f"Deleted {len(messages)} emails. Total deleted so far: {messages_deleted}")
                
            # Check if there are more pages of results
            if 'nextPageToken' in response:
                page_token = response['nextPageToken']
            else:
                print('All matching emails deleted successfully.')
                break  # Exit the loop if there are no more pages

    except Exception as e:
        print('An error occurred:', e)

def main():
    # Authenticate and create Gmail service
    service = create_service()

    # Select Category to delete
    print("Select a Category to Delete. (1, 2 or 3)")
    print("Options: 1- Promotions 2- Social 3- Both")
    selection = input("Selection : ")
    
    # Define Promtions and Social queries
    promotions_query = 'label:Promotions'
    social_query = 'label:Social'
    
    # Delete based on user input
    if   selection == "1":
        delete_emails(service, promotions_query)
    elif selection == "2":
        delete_emails(service, social_query)
    elif selection == "3":
        delete_emails(service, promotions_query)
        delete_emails(service, social_query)
if __name__ == '__main__':
    main()
