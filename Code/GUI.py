from __future__ import unicode_literals
from tkinter import * # pylint: disable=unused-wildcard-import 
import os
from tkinter import scrolledtext  
from tkinter import messagebox  


import youtube_dl

import webbrowser #For opening the links in the menus.

root = Tk()
root.title("YouTube-DL GUI") #Title/Name of program in top bar
root.iconbitmap("E:\\Egna projekt\\YTdlGUI\\icon.ico") #Icon for the program


#URL vars
github_url = ""
license_url = ""


# YouTube-dl code

# Intercepts YouTube-dl's output
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


#"Highest resolution", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "Worst resolution"]
def create_opts(resolution_setting):
    if resolution_setting == "Highest resolution":
        video_setting = 'bestvideo+bestaudio/best'

    elif resolution_setting == "2160p":
        video_setting = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'

    elif resolution_setting == "1440p":
        video_setting = 'bestvideo[height<=1440]+bestaudio/best[height<=1440]'

    elif resolution_setting == "1080p":
        video_setting = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'

    elif resolution_setting == "720p":
        video_setting = 'bestvideo[height<=720]+bestaudio/best[height<=720]'

    elif resolution_setting == "480p":
        video_setting = 'bestvideo[height<=480]+bestaudio/best[height<=480]'
        

    elif resolution_setting == "360p":
        video_setting = 'bestvideo[height<=360]+bestaudio/best[height<=360]'

    elif resolution_setting == "240p":
        video_setting = 'bestvideo[height<=240]+bestaudio/best[height<=240]'

    elif resolution_setting == "Worst resolution":
        video_setting = 'worst'



    ydl_opts = {
    'format': str(video_setting),        
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    }

    return ydl_opts


def downloader( user_input, resolution_setting):
    index = 0
    for url in user_input:
        index += 1
        ydl_opts = create_opts(resolution_setting)
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as E:
            print(E)
            custom_popup("Warning YouTube-dl error", Exception)

        #Update the progress bar
        buildstr = "Download progress: " + str(index)+ "/" + str(len(user_input))
        status_var.set(buildstr)
        root.update()

        #download_progress_statusbar.set(buildstr) #Instance of 'Label' has no 'set' member
        #download_progress_statusbar.config(text=buildstr)
        #download_progress_statusbar['text'] = buildstr
        #download_progress_statusbar = Label(root, text="Download progress: "+ str(index)+ "/" + str(len(user_input)), bd=1, relief=SUNKEN, anchor=E, padx=20)
        #download_progress_statusbar.grid(row=2, column = 0, columnspan=2, sticky=W+E)
        
    return



# TODO
def check_update():
    custom_popup("Not impmented", "Not impmented yet.")
    return

# TODO
def check_license(license_url):
    #custom_popup("Not impmented", "Not impmented yet.")
    webbrowser.open_new(license_url)
    return

def program_not_working():
    custom_popup("Sorry", "Most likely YouTube has changed something and thus the program needs to be updated with the latest version of one of it's dependencies YouTube-dl. Find out if it's this click \"check for updates\" button. If not this you are probably not putting in correct links to videos.\n If not any of this please report it on GitHub, click the \"GitHub\ button")
    return

def github_open():
    custom_popup("Not impmented", "Not impmented yet.")
    #webbrowser.open_new(github_url)
    return

##GUI Code bellow

def custom_popup(title_bar, text_to_show):
    messagebox.showinfo(title_bar, text_to_show)
    return



# Kinda like the def main 
def start_process():
    #Turn the button of so no multi clicks
    start_download_button["state"] = "disabled"
    file_menu.entryconfig(0,state=DISABLED)
    
    try:
        user_input = input_url.get("1.0", END)
    except Exception:
        custom_popup("Warning input error", Exception)

    user_input=user_input.split("\n")   #Data comes in with \n in string so split into list


    #Filter out spaces and empty strings in the input list
    user_input = [var.strip(" ") for var in user_input] #Removes all the spaces, no spaces in youtube URLs so it works
    user_input = list(filter(None,user_input))  #Removes the list entries with nothing in them
    
    #Check if no input
    if not user_input:
        custom_popup("Input failure", "No input entered")
        start_download_button["state"] = "normal"
        file_menu.entryconfig(0,state=NORMAL)
        return    

    
    
    try:
        resolution_setting = working_res.get()
    except Exception:
        custom_popup("Warning resolution error", Exception)
    

    downloader(user_input, resolution_setting)


    #Turn the button back on.
    start_download_button["state"] = "normal"
    file_menu.entryconfig(0,state=NORMAL)
    return




Instructions = Label(root, text="Paste your YouTube links for download:")
Instructions.grid(row=0, column=1)

input_url= scrolledtext.ScrolledText(root, width=50, height=20)
input_url.grid(row=1, column=1)

potential_resolutions = ["Highest resolution", "2160p", "1440p", "1080p", "720p", "480p","360p", "240p", "Worst resolution"]
working_res = StringVar()
working_res.set("Highest resolution")
max_resolution = OptionMenu(root, working_res, *potential_resolutions)
max_resolution.configure(width=15) #Sets a constant width of the resolution menu
max_resolution.grid(row=0, column=0)

start_download_button = Button(root, text="Start download", command=start_process, width=18 , height=5) 
start_download_button.grid(row=1, column=0) #, sticky=N+W)

status_var = StringVar()
status_var.set("Download progress: 0/0")
download_progress_statusbar = Label(root, textvariable= status_var , bd=1, relief=SUNKEN, anchor=E, padx=20) #text="Download progress: 0/0"
download_progress_statusbar.grid(row=2, column = 0, columnspan=2, sticky=W+E)


## TOP bar

#button_quit = Button(root, text="Close program", command=root.quit)
menu_bar = Menu(root)
root.config(menu=menu_bar)   #Add menu to root

#Menu Items:
#File
file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Start download", command=start_process)
file_menu.add_separator()
file_menu.add_command(label="Close program", command=root.quit)

#Not working

#Help/About
help_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Check for updates", command=check_update)
help_menu.add_command(label="License", command=check_license)
help_menu.add_command(label="Program not working", command=program_not_working)
help_menu.add_command(label="Github", command=github_open)

root.mainloop()






