# Scripts-WebmailAutomation

This is a sanitized version of a script I used to automate management of a webmail portal. Doing these tasks manually would take 40-50 minutes in the morning and afternoon, mindless point-and-click. Automation reduced overall task time down to 20 minutes, with a 5 minute manual check after execution concluded. With this script, I also added a third midday spam check during lunch as a fair amount of spam would show up 9-10am, missing the morning 8am spam check.

Functions with this version:
1. Check individual mailboxes for spam
    With aggressive spam quarantine polices and POP3 mail everywhere, there would eventually be legit mail that gets caught in the filters. There was no global collection location either, had to go mailbox to mailbox to check.
2. Check mailbox capacity levels
    Mailboxes had a 3GB limit each, large PDF files were common, and even with POP3 connections erasing messages older than 2 weeks, there would be the occasional mailbox that would breach the limit. This task would report if any mailbox went over 75%.
3. Collect and process DMARC logs
    Added this as a bonus, minimal time saving. Collected logs had to be decompressed depending on filetype (typically .zip or .gz). Main trouble point was extracting the archives while retaining the timestamps if they were present.
