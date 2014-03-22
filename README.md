UCSBClassChecker
================

Python script for checking if UCSB classes are open.

---

**Clone this repo, edit the search.json file, and run in your terminal.**

**NOTE:  This script requires beautifulsoup4 and mechanize**

Requirements can be installed with:  `pip install -r requirements.txt`

To start searching run: `python gold.py`
  
  
  
You will be prompted to login using the password associated with your UCSBNetID.

Your account info will be used for logging into GOLD and later for sending a notification email.

No login info is saved, but it is kept in session variables until the program quits.


---
  
**Hint:**
To have this script send you a text when a class opens up, use one of these for your `notify_email`:

* T-Mobile: `10digitphonenumber@tmomail.net`
* AT&T:  `10digitphonenumber@txt.att.net`
* Verizon: `10digitphonenumber@vtext.com`
* Sprint: `10digitphonenumber@messaging.sprintpcs.com`

---    
  
**About the `search.json` file:**

1. `ucsb_net_id` : Pretty self-explanatory. Don't include the "@umail.ucsb.edu"  

2. `notify_email` : This is the email that will get a message when a class opens up.  

3. `mins_to_wait` : How long you want to wait before checking GOLD again.  

4. `check_pass_time` : 1 to only check when within one of your three pass times, 0 to disable. 

5. `quarter` : This is a numerical value, internal to UCSB GOLD. The pattern seems to be YYYY# where # is the quarter number. So Winter 2014 is 20141.  

6. `search_params` : The easiest way to search is to just set the `enroll_code` and leave the rest blank. If you want to use the `department` you need to enter the `course_num` as well. You can have more than 5 of those individual searches. Just copy and paste another one into the list:
  
        {  
            "enroll_code" : "31476",  
            "department" : "",   
            "course_num" : ""  
        }  

[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/30f2235cab60b1b9f33e8ff546b33641 "githalytics.com")](http://githalytics.com/nando1/UCSBClassChecker)
