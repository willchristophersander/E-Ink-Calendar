To use this program you'll have to do a little bit of work setting it up, but I've made the instructions very simple in order for most people to be able to do it.
Currently the calendar only works with iCloud data -- as such you have to use an iCloud limited-access password you get from Apple. Here are the steps for that.

Steps:

1: Go to https://account.apple.com

2: Login

3: Click App-Specific Passwords, select the icon to add a password.

4: Name and create the password. I reccomend naming it "E-Ink Calendar." 

5: Save/copy the password for the next few steps.

6: Download this repository

7: Go to data/credentials.json in your local copy of this repository. 

8: Replace email@gmail.com with your email. Keep the quotation marks. 

9: Replace key with your app-specific password. Keep the quotation marks.

From here you'll need to install the following dependencies on whatever device you're using the calendar on (I've listed them as easy to run pip install commands for your convenience):
pip install icalendar
pip install caldav
pip install requests
pip install pillow

Further, if you will be using this program on a pi/e-ink display, you need to change line 18 of /E-Ink-Calendar/config.yaml -- tesmode should be set to false, not true.

And thats it. The program should be working by this point. I'll write more instructions later for customizing the layout of the calendar. 
