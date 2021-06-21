from __future__ import unicode_literals
import threading
from tkinter import * # pylint: disable=unused-wildcard-import 
import os, sys, logging, configparser
from threading import Thread
from tkinter import scrolledtext  
from tkinter import messagebox  
from tkinter import filedialog

import youtube_dl

import webbrowser #For opening the links in the menus.



## LOGGER FOR THE CODE BECAUSE tkinter and pyinstaller break in new ways and to ease that debugging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_format = " %(asctime)s: %(Levelname)s - %(message)s"
file_handler = logging.FileHandler("log.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)

#logger.level("Message here")
#logger.exception("Message here") #For try except


# Capture stdout
sys.stdout = open('stdout.txt', 'w')  # Redirect all the prints when we run the program. Relevant when the program runs with no console. This happens when program is built with pyinstaller -windowed tag






"""
def resource_path(relative_path):   #for pyinstaller to work with extra files
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
"""
def resource_path(relative_path): #for pyinstaller to work with extra files
    logger.debug("Called function resource_path with: "+ str(relative_path))
    try: 
        base_path = sys._MEIPASS    # pylint: disable=no-member
    except Exception:
        logger.exception("ResourcePathing error")
        base_path = os.path.abspath(".")
    logger.info("Resource path"  + str(os.path.join(base_path, relative_path)))
    return os.path.join(base_path, relative_path)


## CONSTANTS
config_file="settings.ini"
ffmpeg_path = resource_path("ffmpeg.exe")
version = "1.0"
potential_resolutions = ["Highest resolution", "2160p", "1440p", "1080p", "720p", "480p","360p", "240p", "Worst resolution"]
#URL vars
github_url = "https://github.com/chakeson/YouTube-dl-GUI"
license_url = "https://github.com/chakeson/YouTube-dl-GUI/blob/main/LICENSE"
version_url = "https://github.com/chakeson/YouTube-dl-GUI/blob/main/version"


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
def create_opts( resolution_setting, file_path, audio_extract):
    logger.debug("Called function create_opts with: "+ str(resolution_setting) + " " + str(file_path) + " " + str(audio_extract))


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


    #Build the youtube-dl options
    ydl_opts = {
    'format': str(video_setting),           
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'ffmpeg_location': str(ffmpeg_path),
    }

    #Check if audio extractions is on and add it to the youtube-dl options
    if audio_extract == True:
         ydl_opts['postprocessors']= [{'key': 'FFmpegExtractAudio'}]

    #Check if custom filepath is on and add it to the youtube-dl options
    if file_path != False:
        ydl_opts['outtmpl']= str(file_path) +"/" + "%(title)s.%(ext)s" 


    logger.info("Opts: " + str(ydl_opts))
    return ydl_opts


def downloader( user_input, resolution_setting, file_path, audio_extract):
    logger.debug("Called function downloader with: "+ str(user_input) +" : " + str(resolution_setting))
    index = 0
    for url in user_input:
        logger.info("Downloading: " + str(url))
        index += 1
        ydl_opts = create_opts(resolution_setting, file_path, audio_extract)
        
        if 1:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as E:
                print(E)
                logging.exception()
                custom_popup("Warning YouTube-dl error", Exception)
            

        logger.debug("Finished the download")

        #Update the progress bar
        buildstr = "Download progress: " + str(index)+ "/" + str(len(user_input))
        status_var.set(buildstr)
        root.update()
        logger.debug("GUI updated")


        
    return




def check_update():
    logger.debug("Called function check_update")
    custom_popup("Not impmented", "Not impmented yet.")
    return

def check_license():
    logger.debug("Called function check_license")
    #custom_popup("Not impmented", "Not impmented yet.")
    webbrowser.open_new(license_url)
    return

def program_not_working():
    logger.debug("Called function program_not_working")
    custom_popup(u"Sorry", "Most likely YouTube has changed something and thus the program needs to be updated with the latest version of one of it's dependencies YouTube-dl. Find out if it's this click \"check for updates\" button. If not this you are probably not putting in correct links to videos.\n If not any of this please report it on GitHub, click the \"GitHub\" button")
    return

def github_open():
    logger.debug("Called function github_open")
    #custom_popup("Not impmented", "Not impmented yet.")
    webbrowser.open_new(github_url)
    return



def custom_popup(title_bar, text_to_show):
    logger.debug("Called function custom_popup")
    messagebox.showinfo(title_bar, text_to_show)
    return



#TODO
## Chooses the directory to download too, with youtube-dl
def open_dir():
    global directory_name
    directory_name = filedialog.askdirectory(initialdir = "/")

    #config['download_settings'] = {'file_path': directory_name}
    config['download_settings']['file_path'] = directory_name
    try:
        with open(config_file, "w") as tobewritten:
            #config.write(filename)
            config.write(tobewritten)
    except Exception as E:
        logger.exception("Resolution error open dir")
        custom_popup("Config file Error open dir", Exception)


    return

## Handles starting the thread which will do the downloading work.
## This frees up the GIL so you can still interact with the GUI which the download is happening.
def start_process():
    downloader_thread = threading.Thread(target=main_process)
    downloader_thread.start()
    return


## The function which does the link parsing and then passes them to the downloader function.
def main_process():    
    logger.debug("Called function start_process")
    
    #Turn the button of so no multi clicks
    start_download_button["state"] = "disabled"
    file_menu.entryconfig(0,state=DISABLED)
    
    logger.debug("Disabled start buttons")

    try:
        user_input = input_url.get("1.0", END)
    except Exception:
        logger.exception("User input exception")
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

    
    # Get resolution
    try:
        resolution_setting = working_res.get()
    except Exception:
        logger.exception("Resolution error")
        custom_popup("Warning resolution error", Exception)
    
    #Get file path
    try:
        try:
            file_path = config.get('download_settings','file_path')
        except:
            file_path = False
    except Exception:
        logger.exception("File path error")
        custom_popup("Warning file path error", Exception)

    #Get if audio extract is on
    try:
        audio_extract = audio_extract_selection.get()
    except Exception:
        logger.exception("Audio extract error")
        custom_popup("Warning audio extract error", Exception)

    downloader(user_input, resolution_setting, file_path, audio_extract)


    #Turn the button back on.
    start_download_button["state"] = "normal"
    file_menu.entryconfig(0,state=NORMAL)
    return


## Builds the config file with the settings the first time the code is run.
def build_config_file( config, filename):
    """ # LEGACY API
    config.add_section("gui")
    config.add_section("download_settings")

    config.set( "gui", "theme", "light")

    config.set( "download_settings", "standard_resolution", "Highest resolution")
    config.set( "download_settings", "file_path", "None")
    config.set( "download_settings", "audio_only", "no")
    """
    
    config['GUI'] = {'theme': 'light'}
    config['download_settings'] = {'standard_resolution': 'Highest resolution',
                                    'file_path': 'False',
                                    'audio_only': 'False'}
    try:
        with open(filename, "w") as configfile:
            #config.write(filename)
            config.write(configfile)
    except Exception as E:
        logger.exception("Resolution error")
        custom_popup("Config file Error", Exception)

    return

## Load in config file and validate input #TODO add validation
def load_config_file():
    global start_audio_extract
    global start_resolution
    #global directory_name
    start_resolution = config.get('download_settings','standard_resolution') #config['download_settings']['standard_resolution'] legacy api
    start_audio_extract = config.get('download_settings','audio_only')
    #directory_name = config.get('download_settings','file_path')


    return


global config
config = configparser.ConfigParser()
config.read(config_file)
#TODO
def main():
    #Check for settings
    ## CONFIG

    if config.sections() == []: # if it's an empty list.
        #Make the settings file.
        build_config_file(config, config_file)
    
    load_config_file() 

    

    return

if __name__ == "__main__":
    main()





##GUI Code bellow

#TK set up
root = Tk()
root.title("YouTube-DL GUI") #Title/Name of program in top bar
#root.iconbitmap("E:\\Egna projekt\\YTdlGUI\\icon.ico") #Icon for the program
path_icon = resource_path('icon.ico')
root.iconbitmap(path_icon)

root.minsize( 520, 270) #minimum window size
root.geometry("600x300")

## UI scaling with window resizing
Grid.rowconfigure(root, 0, weight=0)
Grid.rowconfigure(root, 1, weight=1)
Grid.columnconfigure(root, 0, weight=0)
Grid.columnconfigure(root, 1, weight=1)
#Scales the grid with window size/resolution

#Window GUI
Instructions = Label(root, text="Paste your YouTube links for download:")
Instructions.grid(row=0, column=1, sticky="NSEW")

input_url= scrolledtext.ScrolledText(root)#, width=50, height=20)
input_url.grid(row=1, column=1, rowspan=3, sticky="NSEW")

#potential_resolutions = ["Highest resolution", "2160p", "1440p", "1080p", "720p", "480p","360p", "240p", "Worst resolution"] #Defined earlier with other constants also so configparser has access
working_res = StringVar()
working_res.set(start_resolution) #Standard value is "Highest resolution"
max_resolution = OptionMenu(root, working_res, *potential_resolutions)
max_resolution.configure(width=15) #Sets a constant width of the resolution menu
max_resolution.grid(row=0, column=0, sticky="EW")


#File dialog
download_dir_button = Button( root, text="Download file directory", command=open_dir)
download_dir_button.grid(row=1, column=0, sticky="new")


#Audio extract
audio_extract_selection = BooleanVar()
audio_extract_selection.set(start_audio_extract)
audio_extract_checkbox = Checkbutton(root , text="Extract audio", variable=audio_extract_selection, onvalue=True, offvalue=False, width=15, height=1, anchor="n")
audio_extract_checkbox.grid(row=2, column=0, sticky="NEW")


#Start download button
start_download_button = Button(root, text="Start download", command=start_process, height=10)#, width=18 , height=5) 
start_download_button.grid(row=3, column=0, sticky="NSEW") #, sticky=N+W)


#Status bar bottom of the window
status_var = StringVar()
status_var.set("Download progress: 0/0")
download_progress_statusbar = Label(root, textvariable= status_var , bd=1, relief=SUNKEN, anchor=E, padx=20) #text="Download progress: 0/0"
download_progress_statusbar.grid(row=4, column = 0, columnspan=2, sticky=W+E)





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

#Settings
setting_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Settings", menu=setting_menu)
setting_menu.add_command(label="Theme")#, command=start_process) ¤TODO
setting_menu.add_command(label="Audio extract always on")#, command=start_process) #TODO



#Help/About
help_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Check for updates", command=check_update)
help_menu.add_command(label="License", command=check_license)
help_menu.add_command(label="Program not working", command=program_not_working)
help_menu.add_command(label="Github", command=github_open)

root.mainloop()






