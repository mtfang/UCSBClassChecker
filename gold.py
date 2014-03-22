# UCSBClassChecker V2 (03/21/14)
# Author of orginal script: efg@umail.ucsb.edu (nando1 on GitHub, http://www.nando1.com/)
# Modded by Michael Fang: mfang@umail.ucsb.edu


from getpass import getpass
from bs4 import BeautifulSoup
import mechanize
import smtplib
import time
import json
import pdb
import re
import time
import datetime



class Gold(object):

    def __init__(self):
        self.notify_email = None
        self.quarter = None
        self.user = None
        self.pw = None
        self.br = mechanize.Browser()
        self.welcome_msg = "UCSB Class Checker (Exit at any time with Ctrl-C)"
        self.exit_msg = "\n\nThanks for using the UCSB Class Checker!\n"
        # Read search file to get username on login screen
        self.search_params = self.read_search_file("search.json")
        self.start()

    def start(self):
        print("\n%s" % self.welcome_msg)
        # Trick to underline my welcome message with the correct # of =
        print("%s" % ''.join(["=" for i in range(len(self.welcome_msg))]))

        while True:
            try:
                self.login()
                if self.check_pass:
                    if self.check_pass_time(self.search_params):
                        self.search(self.search_params)
                else:
                    self.search(self.search_params)
                self.wait()

            except KeyboardInterrupt:
                print(self.exit_msg)
                exit()

    def login(self):
        LOGIN_URL = 'https://my.sa.ucsb.edu/gold/Login.aspx'
        USER_FIELD = 'ctl00$pageContent$userNameText'
        PW_FIELD = 'ctl00$pageContent$passwordText'
        CHECKBOX_FIELD = 'ctl00$pageContent$CredentialCheckBox'
        # Sometimes I get random mechanize errors
        # So try to login til successful
        while True:
            try:
                if not self.pw:
                    print("Logging in as: %s" % self.user)

                    self.pw = getpass("UCSB NetID Password: ")

                ### EDITS FOR HEROKU COMPATIBILITY ###
                # Comment out the above 3 lines relating to the "if" statement
                # Uncomment the following line (NOTE IDK HOW SECURE THIS IS)
                # self.pw = "ENTER_YOUR_GOLD_PW_HERE"
                # Open login page, select login form, modify fields, submit
                self.br.open(LOGIN_URL)
                self.br.select_form(nr=0)
                form = self.br.form
                form[USER_FIELD] = self.user
                form[PW_FIELD] = self.pw
                # Checkbox has weird way of being set
                form[CHECKBOX_FIELD] = ['on']
                # Should not get the login page again after login attempt
                response = self.br.submit()
                soup = BeautifulSoup(response.read())
                if soup.title.string == 'Login':
                    print("> Login unsuccessful. Check credentials.\n")
                    self.pw = None
                else:
                    print("\n> Login successful.\n")
                    break
            except (EOFError, KeyboardInterrupt):
                print(self.exit_msg)
                exit()
            except:
                print("Unexpected error logging in. Trying again...")

    def read_search_file(self, path):
        search_params = None
        with open(path) as f:
            search_file = json.load(f)
            self.user = search_file["ucsb_net_id"]
            self.notify_email = search_file["notify_email"]
            self.mins_to_wait = float(search_file["mins_to_wait"])
            self.quarter = search_file["quarter"]
            self.check_pass = bool(int(search_file["check_pass_time"]))
            search_params = search_file["search_params"]


        # Remove blank/duplicate searches. Fix department string if necessary
        blank = {"enroll_code": "", "department": "", "course_num": ""}
        dupe_free_search_params = []
        for item in search_params:
            # Fix department string by appending a space until it is 5 chars
            while (len(item['department']) < 5) and (item['department'] != ''):
                item['department'] += ' '
            if (item not in dupe_free_search_params) and (item != blank):
                    dupe_free_search_params.append(item)
        return dupe_free_search_params
    
    def read_date_time(self,datetime):
        # Parse the two times
        parsedstr = re.split('/|/| |:|-|/|/| |:| |',datetime)
        for index, item in enumerate(parsedstr):
            if item == '':
                del parsedstr[index]
            elif item == 'AM':
                parsedstr[index] = 0
            elif item == 'PM':
                parsedstr[index] = 1
            else:
                parsedstr[index] = int(parsedstr[index])
        # Repeated loop to clean up extra blank strings
        for index, item in enumerate(parsedstr):
            if item == '':
                del parsedstr[index]
        # Returns a pass window as follows: [M1,D1,Y1,H1,M1,12HR1,M2,D2,Y2,H2,M2,12HR2]
        return parsedstr       

    def check_in_pass_window(self,passwin):
        cur_time = time.time()
        # Converts 12hr to 24hr format
        passwin[3]+=passwin[5]*12
        passwin[9]+=passwin[11]*12
        # Reorder list to convert to datetime format
        myorder=[2,0,1,3,4]
        passwin1 = [ passwin[i] for i in myorder]
        myorder = [x+6 for x in myorder]
        passwin2 = [ passwin[i] for i in myorder]
        tt1 = tuple(passwin1)
        tt2 = tuple(passwin2)
        # Convert to datetime and then to seconds from epoch
        dt1 = datetime.datetime(tt1[0], tt1[1], tt1[2], tt1[3], tt1[4])
        dt2 = datetime.datetime(tt2[0], tt2[1], tt2[2], tt2[3], tt2[4])
        ts1 = time.mktime(dt1.utctimetuple())
        ts2 = time.mktime(dt2.utctimetuple())
        # Compare currrent time to pass times
        if (cur_time - ts1 > 0) and (ts2 - cur_time > 0):
            return 1
        else:
            return 0
        
    def check_pass_time(self,search_params):
        SEARCH_URL = 'https://my.sa.ucsb.edu/gold/RegistrationInfo.aspx'
        QUARTER_FIELD = 'ctl00$pageContent$quarterDropDown'
        print("> Checking pass times...\n")
        # Hack to work around lack of javascript in mechanize #
        self.br.open(SEARCH_URL)
        # Select search form
        self.br.select_form(nr=0)
        form = self.br.form
        # Set search params
        form[QUARTER_FIELD] = [self.quarter]
        self.br.submit().read()
        # #
        try:
            url = self.br.open(SEARCH_URL)
            # Execute search and save result page for parsing
            soup = BeautifulSoup(url.read())
            # Parse results
            pass_one_attrs = {"id": "pageContent_PassOneLabel"}
            pass_one = soup.findAll("span", attrs=pass_one_attrs)
            p_one = pass_one[0].string.replace(u'\xa0', u'')
            passwin1 = self.read_date_time(p_one)
            
            pass_two_attrs = {"id": "pageContent_PassTwoLabel"}
            pass_two = soup.findAll("span", attrs=pass_two_attrs)
            p_two = pass_two[0].string.replace(u'\xa0', u'')
            passwin2 = self.read_date_time(p_two)
            
            pass_three_attrs = {"id": "pageContent_PassThreeLabel"}
            pass_three = soup.findAll("span", attrs=pass_three_attrs)
            p_three = pass_three[0].string.replace(u'\xa0', u'')
            passwin3 = self.read_date_time(p_three)
            
            pass_one = self.check_in_pass_window(passwin1)
            pass_two = self.check_in_pass_window(passwin2)
            pass_three = self.check_in_pass_window(passwin3)

            if pass_one:
                print('> You are within your first pass time!\n')
                return 1
            elif pass_two:
                print('> You are within your second pass time!\n')
                return 1
            elif pass_three:
                print('> You are within your third pass time!\n')
                return 1
            else:
                print('> It is not your pass time...\n')
                return 0
            
        except (mechanize._form.ControlNotFoundError,
                mechanize._form.ItemNotFoundError):
            print("Unknown error. Skipping for now...\n")
        

    def search(self, search_params):
        SEARCH_URL = 'https://my.sa.ucsb.edu/gold/CriteriaFindCourses.aspx'
        QUARTER_FIELD = 'ctl00$pageContent$quarterDropDown'
        ENROLL_CODE_FIELD = 'ctl00$pageContent$enrollcodeTextBox'
        DEPARTMENT_FIELD = 'ctl00$pageContent$departmentDropDown'
        COURSE_NUM_FIELD = 'ctl00$pageContent$courseNumberTextBox'
        print("> Starting search...")
        # Hack to work around lack of javascript in mechanize #
        self.br.open(SEARCH_URL)
        # Select search form
        self.br.select_form(nr=0)
        form = self.br.form
        # Set search params
        form[QUARTER_FIELD] = [self.quarter]
        self.br.submit().read()
        # #
        for s in search_params:
            try:
                print("\n")
                self.br.open(SEARCH_URL)
                # Select search form
                self.br.select_form(nr=0)
                form = self.br.form
                # Set search params
                form[QUARTER_FIELD] = [self.quarter]
                form[ENROLL_CODE_FIELD] = s['enroll_code']
                form[DEPARTMENT_FIELD] = [s['department']]
                form[COURSE_NUM_FIELD] = s['course_num']
                # print(form)
                # Execute search and save result page for parsing
                soup = BeautifulSoup(self.br.submit().read())
                # Parse results
                error_page_attrs = {"id": "pageContent_messageLabel"}
                error_page = soup.findAll("span", attrs=error_page_attrs)
                if error_page:
                    print("Class not found. Will try again next time.")
                    continue
                
                class_title_attrs = {"class": "tableheader"}
                class_title = soup.findAll("span", attrs=class_title_attrs)
                
                info_header_attrs = {"class": "tableheader"}
                info_header = soup.findAll("td", attrs=info_header_attrs)[0:7]


                info_table_attrs = {"class": "clcellprimary"}
                info_table = soup.findAll("td", attrs=info_table_attrs)[0:7]
                
                lectime = info_table[2].string.replace(u'\xa0', u'')
                lecday = info_table[1].string.replace(u'\xa0', u'')
                lecloc = info_table[4].string.replace(u'\xa0', u'')
                lecprof = info_table[3].string.replace(u'\xa0', u'')

                info_dict = {}
                section = False
 
                enroll = int(float(info_table[0].string.replace(u'\xa0', u'')))
                if int(enroll) == int(s['enroll_code']):
                    for title, detail in zip(info_header, info_table):
                        info_dict[title.string] = detail.string
                else:
                    enroll = 0
                    i = 0
                    while True:
                        info_table_attrs = {"class": "clcellsecondary"}
                        info_table= soup.findAll("td", attrs=info_table_attrs)[1+i*20:8+i*20]
                        if info_table == []:
                            break
                        enroll = int(float(info_table[0].string.replace(u'\xa0', u'')))
                        if int(enroll) == int(s['enroll_code']):
                            for title, detail in zip(info_header, info_table):
                                info_dict[title.string] = detail.string
                            section = True
                            break
                        else:
                            i+=1
                    enroll = 0
                    i = 0 
                    while True:
                        info_table_attrs = {"class": "clcellsecondaryalternate"}
                        info_table = soup.findAll("td", attrs=info_table_attrs)[1+i*20:8+i*20]
                        if info_table == []:
                            break
                        enroll = int(float(info_table[0].string.replace(u'\xa0', u'')))
                        if int(enroll) == int(s['enroll_code']):
                            for title, detail in zip(info_header, info_table):
                                info_dict[title.string] = detail.string
                            section = True
                            break
                        else:
                            i+=1

                # Print class title and section
                title = class_title[0].string.replace(u'\xa0', u' ')
                title = ' '.join(title.split())
                lecture = ''.join([lecday,lectime])
                classtitle = "\n%s: %s" %(title,lecprof)
                lectitle = "Lecture: %s    %s" % (lecture,lecloc)
                print(classtitle)
                print(lectitle)
                if section:
                    sectime = info_dict["Time(s)"].string.replace(u'\xa0', u'')
                    secday = info_dict["Day(s)"].string.replace(u'\xa0', u'')
                    secloc = info_dict["Location(s)"].string.replace(u'\xa0', u'')
                    sectionstr = ''.join([secday,sectime])
                    sectitle= "Section: %s    %s" % (sectionstr,secloc)
                    print(sectitle)
                    
                # Trick to underline a string with the correct # of =
                print("%s" % ''.join(["=" for i in range(max(len(sectitle),len(lectitle),len(classtitle)))]))
                
                # Check if full
                
                if info_dict["Space"] == u"Full\xa0":
                    print("Class is full.")
                    continue
                elif info_dict["Space"] == u"Closed\xa0":
                    print("Class is closed.")
                    continue
                elif (info_dict['Day(s)'] == u'T.B.A.\xa0'):
                    if (info_dict['Instructor(s)'] == u'T.B.A.\xa0'):
                        if (info_dict['Time(s)'] == u'T.B.A.\xa0'):
                            print("This class is not available yet.")
                            continue
                elif (float(info_dict["Space"]) / float(info_dict["Max"])) > 0:
                    if self.notify_email:
                        if section:
                            print("Section is OPEN with %d spots! Sending notification to %s..." % (int(float(info_dict["Space"].string.replace(u'\xa0', u''))),self.notify_email))
                        else:
                            print("Lecture is OPEN with %d spots! Sending notification to %s..." % (int(float(info_dict["Space"].string.replace(u'\xa0', u''))),self.notify_email))
                        self.notify(title)
                    else:
                        if section:
                            print("Section is OPEN with %d spots!"% int(float(info_dict["Space"].string.replace(u'\xa0', u''))))
                        else:
                            print("Lecture is OPEN with %d spots!"% int(float(info_dict["Space"].string.replace(u'\xa0', u''))))
                    continue
                else:
                    print("Unknown reason why class is full.")
                
            except (mechanize._form.ControlNotFoundError,
                    mechanize._form.ItemNotFoundError):
                print("Unknown error. Skipping for now...\n")

    def notify(self, class_title):
        # Send email from your UCSB Umail to some other email that you specify
        fromaddr = self.user + "@umail.ucsb.edu"
        toaddrs = [self.notify_email]
        msg = """From: <%s>\n To: <%s>\n Subject: [CLASS OPEN!]\n\n %s IS OPEN""" %(fromaddr,toaddrs, class_title)
        # Use credentials that were previously entered
        username = fromaddr
        password = self.pw
        # UCSB Umail's SMTP server and port
        server = smtplib.SMTP('smtp.office365.com',587)
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
        return self

    def wait(self):
        print("\n")
        raw_time_delta = time.localtime(time.time() + self.mins_to_wait*60)
        check_time = time.asctime(raw_time_delta)
        print("\n> Checking again in %d minute(s) at:\n> %s\n" % (self.mins_to_wait, check_time))
        time.sleep(self.mins_to_wait*60.0)


def main():
    Gold()


if __name__ == "__main__":
    main()
