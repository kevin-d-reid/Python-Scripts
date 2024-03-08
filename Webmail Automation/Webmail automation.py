###################################################################
# Webmail Automation Script V1.10
# Written by Kevin D. Reid
# Requirements: pyinputplus, selenium
###################################################################

import sys, os, time, pyinputplus, zipfile, gzip, shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, WebDriverException

# Select domain target
domain = pyinputplus.inputMenu(['<DOMAIN1>', '<DOMAIN2>'], numbered=True, prompt='Please select a domain:\n')
if domain == '<DOMAIN1>':
    webmail_url = '<URL1>'
else:
    webmail_url = '<URL2>'

# Tasks to carry out - All mailboxes
spam_check = pyinputplus.inputYesNo(prompt='Check for spam? ')
if spam_check == 'yes':
    spam_filename = 'spam-check--' + domain + '--' + time.strftime('%Y-%m-%d--%H-%M-%S') + '.txt'   
mailbox_limit_check = pyinputplus.inputYesNo(prompt='Check for mailboxes >75% full? ')
skip_list = pyinputplus.inputYesNo(prompt='Use skip list? ')
if skip_list == 'yes':
    skip_file = open('skip-list.txt').read().splitlines()
# Tasks to carry out - Select mailboxes
DMARC_log_collect = pyinputplus.inputYesNo(prompt='Collect DMARC logs? ')

# Enter username and hidden password
username = pyinputplus.inputEmail(prompt='Enter Email Address: ')
password = pyinputplus.inputPassword(prompt='Enter Password: ')

# Timer start for performance comparisons
print('Execution started at ' + time.strftime('%H-%M-%S'))

# Define browser settings
options = webdriver.ChromeOptions()
prefs = {
    'download.default_directory' : str(Path.cwd()) + "\\temp",
    'download.prompt_for_download' : False,
    'download.directory_upgrade' : True
}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(options)
wait = WebDriverWait(driver, timeout=15)

# Login to portal, navigate to email address list
driver.get(webmail_url + 'portal/')
wait.until(EC.presence_of_element_located((By.ID, 'portal-input-username')))
driver.find_element(By.ID, 'portal-input-username').send_keys(username)
driver.find_element(By.ID, 'portal-input-password').send_keys(password)
driver.find_element(By.XPATH, '//input[@value="Login"]').submit()
# Wait for main page to load first before loading email list, will give HTTP 401 error if email list loaded directly
wait.until(EC.presence_of_element_located((By.ID, 'widget_webmail')))
driver.get(webmail_url + 'nomad/load/849/mailsetup_nomad/en_US_FO#')
wait.until(EC.presence_of_element_located((By.ID, 'email_list_container_next')))

# Define enter mailbox
def mailbox_inspect(row):
    row.find_element(By.LINK_TEXT, 'Webmail').click()
    wait.until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[1])
    # Exceptions happen often here no matter what page element is selected, if that happens the wait will be executed again
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="ng-isolate-scope"]')))
    except WebDriverException:
        wait.until(EC.presence_of_element_located((By.XPATH, '//a[@class="ng-isolate-scope"]')))

# Define exit mailbox
def mailbox_close():
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

# Define script termination
def exit_func():
    print('All tasks complete, exiting now...')
    print('Execution finished at ' + time.strftime('%H-%M-%S'))
    driver.quit()
    sys.exit()

# Define spam check
def task_spam_check(row):
    mailbox_inspect(row)
    try:
        spam_level = driver.find_element(By.XPATH, '//div[@id="foldercore_3"]/div[3]/span').text
        spam_file = open(spam_filename, 'a')
        spam_file.write(driver.find_element(By.XPATH, '//div[@id="panelRealmCore"]/h2/a/div').text + ': ' + spam_level + '\n')
        spam_file.close()
        mailbox_close()
    except NoSuchElementException:
        mailbox_close()

# Iterate through mailboxes performing tasks
while True:
    for row in driver.find_elements(By.XPATH, '//table[@id="email_list_container"]/tbody/tr'):
        # Write mailbox and spam amount to specified file if spam present
        if spam_check == 'yes' and skip_list == 'yes':
            if str(row.find_element(By.PARTIAL_LINK_TEXT, domain).text)[:-len(domain)] not in skip_file:
                task_spam_check(row)
        elif spam_check == 'yes':
            task_spam_check(row)
        # Print mailbox and percentage of limit to console if over 75%
        if mailbox_limit_check == 'yes':
            percentage = str(row.find_element(By.TAG_NAME, 'span').text)[:-1]
            if int(percentage) >= 75:
                print(str(row.find_element(By.PARTIAL_LINK_TEXT, domain).text) + ' is ' + percentage + '% full.')
        # Enter DMARC mailbox and collect logs
        if DMARC_log_collect == 'yes':
            email = row.find_element(By.PARTIAL_LINK_TEXT, domain)
            if str(email.text) == 'dmarc@' + domain:
                print('Collecting DMARC logs...')
                mailbox_inspect(row)
                driver.find_element(By.XPATH, '//ul[@id="corefolders"]/li[6]').click()
                while True:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="divth fcol-spacer cBox"]/span')))
                    driver.find_element(By.XPATH, '//span[@aria-label="Select All"]').click()
                    wait.until(EC.presence_of_element_located((By.ID, 'readingPaneLabel')))
                    try:
                        driver.find_element(By.XPATH, '//a[@title="Download"]').click()
                    except ElementClickInterceptedException:
                        print('No DMARC logs found.')
                        mailbox_close()
                        break
                    try:
                        driver.find_element(By.XPATH, '//button[@aria-label="Next"]').click()
                    except NoSuchElementException:
                        # Go back to Inbox folder and move messages to Aggregate Reports
                        driver.find_element(By.XPATH, '//ul[@id="corefolders"]/li[1]').click()
                        wait.until(EC.presence_of_element_located((By.ID, 'togglePersonalCore')))
                        while True:
                            driver.find_element(By.XPATH, '//span[@aria-label="Select All"]').click()
                            driver.find_element(By.XPATH, '//button[@aria-label="Move to folder"]').click()
                            wait.until(EC.presence_of_element_located((By.XPATH, '//span[@title="Aggregate Reports"]')))
                            driver.find_element(By.XPATH, '//span[@title="Aggregate Reports"]').click()
                            try:
                                driver.find_element(By.XPATH, '//button[@aria-label="Next"]').click()
                            except NoSuchElementException:
                                mailbox_close()
                                break
                    # Define folder locations, extract downloaded archives in temp folder
                    temp_folder = Path.cwd() / Path('temp')
                    log_folder = Path.cwd() / Path('DMARC logs', domain)
                    for attachment in temp_folder.glob('attachment*'):
                        shutil.unpack_archive(attachment, 'temp')
                        os.unlink(attachment)
                    # Extract extracted archives from downloads to log folder
                    # If extracted files are an unrecognized format or unable to extract, leave in temp folder for manual inspection
                    for file in os.listdir(temp_folder):
                        # .zip file extraction while maintaining file modified time if already present
                        if file.endswith('.zip'):
                            try:
                                with zipfile.ZipFile(os.path.join(temp_folder, file), 'r') as f_in:
                                    for fileinfo in f_in.infolist():
                                        name, date_time = fileinfo.filename, fileinfo.date_time
                                        name = os.path.join(log_folder, name)
                                        with open(name, 'wb') as f_out:
                                            f_out.write(f_in.open(fileinfo).read())
                                        epoch_time = time.mktime(date_time + (0, 0, -1))
                                        os.utime(name, (epoch_time, epoch_time))
                                os.unlink(os.path.join(temp_folder, file))
                            except zipfile.BadZipFile:
                                continue
                        # .gz file extraction while maintaining file modified time if already present
                        elif file.endswith('.gz'):
                            try:
                                with gzip.open(os.path.join(temp_folder, file), 'rb') as f_in:
                                    file_xml = file[:-len('.gz')]
                                    with open(os.path.join(log_folder, file_xml), 'wb') as f_out:
                                        shutil.copyfileobj(f_in, f_out)
                                    f_in.peek(100)
                                    epoch_time = float(f_in.mtime)
                                    if epoch_time > 0:
                                        os.utime(os.path.join(log_folder, file_xml), (epoch_time, epoch_time))
                                os.unlink(os.path.join(temp_folder, file))
                            except gzip.BadGzipFile:
                                continue
                        else:
                            continue
                        
                        # Remove duplicate log files and files older than 90 days
                        for file in log_folder.glob('*'):
                            if (file.suffix != '.xml') or (os.path.getmtime(file) + 7776000 < time.time()):
                                os.unlink(file)
                    # Prevent restart of DMARC log collection
                    break

                # Exit if DMARC log collection is only task
                if (spam_check == 'no') and (mailbox_limit_check == 'no'):
                    exit_func()

    # Go to next page if able to, quit script if not
    try:
        driver.find_element(By.XPATH, '//li[@id="email_list_container_next"]/a').click()
        wait.until(EC.invisibility_of_element((By.XPATH, '//div[@class="app_spinner"]')))
    except ElementClickInterceptedException:
        exit_func()