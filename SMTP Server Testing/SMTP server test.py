###################################################################
# SMTP server test v1.03
# Written by Kevin D. Reid
# Requirements: pyinputplus
###################################################################

import sys, pyinputplus, smtplib
from datetime import datetime

# Mail server login fields
SMTP_username = pyinputplus.inputEmail(prompt='Enter SMTP login email: ')
SMTP_password = pyinputplus.inputPassword(prompt='Enter SMTP login password: ')
SMTP_server = pyinputplus.inputURL(prompt='Enter SMTP server name: ')
print('SMTP server ports: 25 or 1025 for unencrypted, 465 for SSL, 587 for STARTTLS')
SMTP_port = int(pyinputplus.inputMenu(['25', '1025', '465', '587'], prompt='Enter SMTP server port: \n'))

# Mail server login
if SMTP_port == 465:
    server = smtplib.SMTP_SSL(SMTP_server, SMTP_port)
elif SMTP_port == 25 or 1025 or 587:
    server = smtplib.SMTP(SMTP_server, SMTP_port)
try:
    server.ehlo()
    if SMTP_port == 587:
        server.starttls()
        server.ehlo()
    server.login(SMTP_username, SMTP_password)
except Exception as exception:
    print(exception)
    sys.exit(1)

# Email sending fields
envelope_from = pyinputplus.inputEmail(prompt='Enter address for envelope "MAIL FROM:" header: ')
envelope_to = pyinputplus.inputEmail(prompt='Enter address for envelope "RCPT TO:" header: ')
email_from = pyinputplus.inputEmail(prompt='Enter address for email "From:" header: ')
email_to = pyinputplus.inputEmail(prompt='Enter address for email "To:" header: ')
optional_headers = pyinputplus.inputYesNo(prompt='Set optional headers?: ')
if optional_headers == 'yes':
    email_replyto = pyinputplus.inputEmail(prompt='Enter address for email "Reply-To:" header: ', blank=True)
    email_sender = pyinputplus.inputEmail(prompt='Enter address for email "Sender:" header: ', blank=True)
else:
    email_replyto = email_from
    email_sender = ''

# Email composition, sending, and exiting of script
date = datetime.now().strftime( "%d/%m/%Y %H:%M" )
message_subject = 'Test message'
message_text = '''Test message sent via Python testing script.
    SMTP username: %s
    MAIL FROM: %s
    From: %s''' % (SMTP_username, envelope_from, email_from)
message = 'From: %s\nReply-To: %s\nSender: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s' % ( email_from, email_replyto, email_sender, email_to, message_subject, date, message_text)
try:
    server.sendmail(envelope_from, envelope_to, message)
except Exception as exception:
    print(exception)
    sys.exit(1)
server.quit()
sys.exit()