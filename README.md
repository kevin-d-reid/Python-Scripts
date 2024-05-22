# Python scripts

Small sample of automation scripts I wrote, with identifying data removed.

## SMTP Server Testing

Basic script to test different email header combinations with mail servers. Can login to SMTP mailboxes (unencrypted + SSL + STARTTLS) and select both envelope (RFC5321) and message (RFC5322) headers. Used to test "Send As" functionality with Microsoft Exchange Online.

Uses PyInputPlus for input validation

## Webmail automation script

Automated administration tasks with an externally hosted mail server fronted with a webmail interface. No API available and bulk tasks were severly limited. Reduced twice-daily manual tasks from 45-50 minutes down to a 15 minute script execution and 5 minute manual check after.

Uses Selenium for browser interaction, webdriver-manager to automate updating of webdriver version, and PyInputPlus for input validation