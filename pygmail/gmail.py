# Google API Specific Imports
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText

import base64
import email
from bs4 import BeautifulSoup


# If modifying these scopes, delete the file token.pickle and it will take you back through authorization for you new scope :)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Kinda thought I should comment on this, so basically the except it changes makes it so it'll raise errors
# under correctly functioning circumstances, the except should pass because it should intentionally break sometimes for some reason, but it only breaks after
# other breaks would happen if you have errors. Hopefully you are more confused now :).
BROKE = False

# TODO: make this automatic, you're better than this, come on bro
PATH = "/home/james/Documents/Programming/gmail-library/"


class GMail:
    # Init sets up all the connection stuff, final service variable that is a collective of
    # all connection and auth stuff is declared and assigned as: self.service
    def __init__(self):
        # Complicated Google example stuff that does auth and other cool complicated stuff, don't ask me how it works :D
        creds = None
        if os.path.exists(PATH + 'token.pickle'):
            with open(PATH + 'token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    PATH + 'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(PATH + 'token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Now the stuff I know :)
        self.service = build('gmail', 'v1', credentials=creds)
        self.emailList = {}


    # Sets up a function to be called with come possible requirements for sorting prior to return
    # This should return a dictionary of all the emails up until max
    def listEmails(self, maxCheck = 100, subjectContains = None, bodyContains = None, sentFrom = None):
        result = self.service.users().messages().list(maxResults=maxCheck, userId='me').execute()
        messages = result.get('messages')
        for msg in messages:
            txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()

            # Use try-except to avoid any Errors
            try:
                # Get value of 'payload' from dictionary 'txt'
                payload = txt['payload']
                headers = payload['headers']

                # Look for Subject and Sender Email in the headers
                for d in headers:
                    if d['name'] == 'Subject':
                        subject = d['value']
                        print(subject)
                    if d['name'] == 'From':
                        sender = d['value']
                        print(sender)

                # Sorts out anything that does not include specified subject content
                # Always use elif because you don't want duplicates duh

                '''
                HORRIBLY BAD: {key: value for key, value in variable} but state machine :D
                '''

                # The none options selected is an important one oops
                if subjectContains is None and bodyContains is None and sentFrom is None:
                    self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                    self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                elif subjectContains is not None and bodyContains is None and sentFrom is None:
                    # sub
                    if subjectContains in subject:
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}}) # This one line should take care of adding any email to the list
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                elif bodyContains is not None and subjectContains is None and sentFrom is None:
                    # body
                    if bodyContains in self.processBody(payload):
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                elif sentFrom is not None and subjectContains is None and bodyContains is None:
                    # sender
                    if sentFrom in sender:
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                elif subjectContains is not None and bodyContains is not None and sentFrom is None:
                    # sub and body
                    if subjectContains in subject and bodyContains in self.processBody(payload):
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                elif subjectContains is not None and sentFrom is not None and bodyContains is None:
                    # sub Sender
                    if subjectContains in subject and sentFrom in sender:
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                elif bodyContains is not None and sentFrom is not None and subjectContains is None:
                    # body and Sender
                    if bodyContains in self.processBody(payload) and sentFrom in sender:
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                elif subjectContains is not None and bodyContains is not None and sentFrom is not None:
                    # all 3
                    if subjectContains in subject and bodyContains in self.processBody(payload) and sentFrom in sender:
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})
                        self.emailList.update({ len(self.emailList) : { "Sender" : sender, "Subject" : subject, "Body" : self.processBody(payload)}})

            # God level manuever here 8)
            except:
                if BROKE:
                    raise
                else:
                    pass

        # Finally return finished list
        return self.emailList

    # Turns payload into string form of body information
    def processBody(self, payload):
        parts = payload.get('parts')[0]
        data = parts['body']['data']
        data = data.replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)
        soup = BeautifulSoup(decoded_data, "lxml")
        body = str(soup.body())
        body = body.replace("[<p>", "")
        cleanBody = body.replace("</p>]", "")

        # Should return body information in form of string if all went well
        return cleanBody



    '''
    --------------------------------------------------------------- NOW STARTING THE OUTGOING SECTION ---------------------------------------------------------------
    '''



    # Sends an email when provided parameters
    def sendEmail(self, sender, to, subject, message_text):
        '''
        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.
        '''

        # Sets up the email body to be sent and assigns it to "toSend"
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
        toSend = {'raw': raw_message.decode("utf-8")}

        # Tries to send the message and upon success it prints what was sent
        message = (self.service.users().messages().send(userId='me', body=toSend).execute())




'''
Example code for testing purposes ONLY :) (Commented out by default for convenience as main purpose would be to use externally)
'''

'''
if __name__ == '__main__':
    # Creates email object
    mail = GMail()

    # Gets data from last 5 emails received
    emails = mail.listEmails(maxCheck = 5)

    # Prints data from emails
    for email in emails:
        print(emails[email]["Sender"])
        print(emails[email]["Subject"])
        print(emails[email]["Body"])
'''
