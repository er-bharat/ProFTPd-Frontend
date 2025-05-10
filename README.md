# ProFTPd-Frontend
this is a GTK GUI frontend for proftp a well known ftp server. It is not connected to proftp project.
![Screenshot From 2025-05-10 16-32-52](https://github.com/user-attachments/assets/0852434d-d3bf-4b46-bc3c-ae1cbc8f8cb3)

i am currently using Arch linux so it works on arch it may need some changes for different systems.
## need
I have always used the ftp server as preferred method of moving files between devices,
i dont like wires.
In windows i was used to filezilla ftp server its a GUI so it was always no hassle open close .

when i got linux installed i looked for ftp servers but none had a GUI to it everything was command line 
so i choose the proftpd, as it was best of recommended and made some scripts to go with it, start close ip addr etc.

But it was always a hassle, because of if it is started or not whether wifi ip changed etc. after long time i forget 
the port no etc. 

So i decided to make a GUI for it bc i didnt find any on the internet.
The current version of it somehow fulfils the basic need of my use case.

## How to use 
1. download folder and move it to 
~/.local/share/applications

open .desktop file and edit path in it to your pc.
reboot and you will find the icon in menu.

2. just put the proftp-gtk.py on desktop and open from it. (you will need to make it executable)
