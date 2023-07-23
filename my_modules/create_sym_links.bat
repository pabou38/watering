: v2.0

: : is not displayed. rem is displayed

rem for micropython

rem WARNING !!!! search for COMMAND PROMPT (not powershell) and run as admin
rem WARNING. edit cd to micropython project dir

: to run cut and paste below AFTER updating cd above
: c:\Users\pboud\micropython\"MY MODULES"\create_sym_links.bat


rem sym link generic modules located in ../my modules (ie HOME/micropython/my modules) and ../../Blynk (ie HOME/Blynk)
rem those are Windows directory
rem HOME/Blynk also used for windows (python app) - add to sys.path
rem Home/Blynk also on linux

rem on windows:
rem HOME/micropython
rem HOME/Blynk
rem HOME/DEEP

rem WHY symlink for micropython ?  
rem file needs to be in project folder for pymakr upload (can be in standalone dir if this dir is included in sys.path)
rem AND edits when developping application will ACCUMULATE in a single (cross application) version 

:creates sym link to generic micropython modules
:both my modules and Blynk
:delete before creating


cd c:\users\pboud\micropython


rem please cd to project directory
:WARNING cd to project directory
:cd "modbus PZEM"

cd "watering"

rmdir my_modules
mklink /D my_modules ..\"MY MODULES"\


rem if linking entiere Blynk, pymakr sync project will copy data, START etc ..
rmdir Blynk
:Blynk\Blynk _client is the code to be imported, rest of Blynk is server

mklink /D Blynk ..\..\Blynk\Blynk_client


: Blynk and my_modules are windows dir, to be uploaded to ESP under /

:make sure my_modules and Blynk are in micropython sys.path

:failed to upload c:\Users\pboud\micropython\watering to / 
:Reason: Error: ENOENT: no such file or directory, stat 'c:\Users\pboud\micropython\watering/Blynk/my_blynk_new.py'