from __future__ import unicode_literals
import threading
from tkinter import * # pylint: disable=unused-wildcard-import 
import os, sys, logging, configparser
from threading import Thread
from tkinter import scrolledtext  
from tkinter import messagebox  
from tkinter import filedialog
import urllib.request, re # Used in the update function.

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
__version__ = 1.0
potential_resolutions = ["Highest resolution", "2160p", "1440p", "1080p", "720p", "480p","360p", "240p", "Worst resolution"]
#URL vars
github_url = "https://github.com/chakeson/YouTube-dl-GUI"
license_url = "https://github.com/chakeson/YouTube-dl-GUI/blob/main/LICENSE"
version_url = "https://github.com/chakeson/YouTube-dl-GUI/blob/main/version"


# YouTube-dl code

# Intercepts YouTube-dl's output
class MyLogger(object):
    def debug(self, msg):
        status_bar.set(msg[13:])
        logger.debug("GUI updated with status of download.")

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
    if file_path != False or None:
        ydl_opts['outtmpl']= str(file_path) +"/" + "%(title)s.%(ext)s" 


    logger.info("Opts: " + str(ydl_opts))
    return ydl_opts


def downloader( user_input, resolution_setting, file_path, audio_extract):
    logger.debug("Called function downloader with: "+ str(user_input) +" : " + str(resolution_setting))
    index = 0
    ydl_opts = create_opts(resolution_setting, file_path, audio_extract)
    
    for url in user_input:
        logger.info("Downloading: " + str(url))
        
        #Update the progress bar
        buildstr = "Download progress: " + str(index)+ "/" + str(len(user_input))
        progress_bar.set(buildstr)
        logger.debug("GUI updated")
        
        index += 1

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as E:
            logging.exception('YouTube-DL download error')
            custom_popup("Warning YouTube-dl error", Exception)
        
        #Update the status bar 
        status_bar.set("")
        #Update the progress bar 
        buildstr = "Download progress: " + str(index)+ "/" + str(len(user_input))
        progress_bar.set(buildstr)
        logger.debug("GUI updated")

        logger.debug("Finished the download")
        
    return

## UI settings functions

def audio_extract_setting():

    # Get the menu bars current status
    audio_extract_setting_choice = audio_extract_allways_on.get()

    #Update config file.
    config['download_settings']['audio_only'] = audio_extract_setting_choice
    
    
    try:
        with open(config_file, "w") as tobewritten:
            config.write(tobewritten)
    except Exception as E:
        logger.exception("Resolution error open dir")
        custom_popup("Config file Error open dir", Exception)
 
    #Update root TK to ensure menu bar is displaying correctly.
    root.update()
    return

##THEME functions

def get_theme_color(theme_choice):
    # Function that contains themes colors.
    # Takes in lowercase string with the themes name, then matched and the right colors are returned
    # Function call looks like  main_color, second_color, third_color, fourth_color, text_color = get_theme_color("dark")
    # Grey, Dark and Black theme colors are based on https://uxdesign.cc/dark-mode-ui-design-the-definitive-guide-part-1-color-53dcfaea5129

    global main_color
    global second_color
    global third_color
    global fourth_color
    global text_color

    if theme_choice == "light":
        main_color = "SystemButtonFace"
        second_color = "SystemButtonFace"
        third_color = "SystemButtonFace"
        fourth_color = "#ffffff"
        text_color = "#000000"
    
    elif theme_choice == "grey":   
        main_color = "#7e7e7e"
        second_color = "#626262"
        third_color = "#515151"
        fourth_color = "#626262"
        text_color = "#F7F7F7"

    elif theme_choice == "dark":   
        main_color = "#121212"
        second_color = "#212121"
        third_color = "#424242"
        fourth_color = "#212121"
        text_color = "#BDBDBD"

    elif theme_choice == "black":
        main_color = "#000000"
        second_color = "#212121"
        third_color = "#424242"
        fourth_color = "#212121"
        text_color = "#9E9E9E"
    
    else:
        raise Exception("Missing theme option"+str(theme_choice))
    
    return main_color, second_color, third_color, fourth_color, text_color



def set_theme(theme_choice):
    #Fetch theme color
    global main_color
    global second_color
    global third_color
    global fourth_color
    global text_color
    #Fetch colors
    main_color, second_color, third_color, fourth_color, text_color = get_theme_color(theme_choice)

    #Main UI elements, set their color
    root.config(bg=main_color)
    Instructions.config(bg=main_color, fg=text_color)
    input_url.config(bg=fourth_color, fg=text_color)
    max_resolution.config(bg=second_color, fg=text_color, activebackground=third_color, activeforeground=text_color)
    max_resolution["menu"].config(bg=third_color,fg=text_color)
    download_dir_button.config(bg=second_color, fg=text_color, activebackground=third_color)
    audio_extract_checkbox.config(bg=second_color, fg=text_color, activebackground=fourth_color, selectcolor=fourth_color)
    start_download_button.config(bg=second_color, fg=text_color, activebackground=third_color)
    download_progress_statusbar.config(bg=second_color, fg=text_color)
    download_status_bar.config(bg=second_color, fg=text_color)

    #Menubar UI elements, set their color
    menu_bar.config(bg=main_color, fg=text_color, activebackground=third_color)
    file_menu.config(bg=main_color, fg=text_color)
    setting_menu.config(bg=main_color, fg=text_color)
    setting_menu_sub_menu.config(bg=main_color, fg=text_color)
    help_menu.config(bg=main_color, fg=text_color)
    
    #Sometimes colors werent getting updated, so added to ensure it.
    root.update()
    #Save changes
    config['GUI']['theme'] = str(theme_choice)
    try:
        with open(config_file, "w") as tobewritten:
            #config.write(filename)
            config.write(tobewritten)
    except Exception as E:
        logger.exception("Resolution error open dir")
        custom_popup("Config file Error theme select: "+str(theme_choice), Exception)

    return


## UI help functions
def check_update(): #TODO
    logger.debug("Called function check_update")
    #custom_popup("Not impmented", "Not impmented yet.")
    try:
        logger.debug("Version urllib launched.")
        urlib_request = urllib.request.Request( version_url, headers={'User-Agent': 'Mozilla/5.0'} )
        version_website_text_uft8 = urllib.request.urlopen(urlib_request).read()
        version_website_text_uft8 = version_website_text_uft8.decode("utf-8")
    except Exception as E:
        logger.exception("Urllib request failed.")
        custom_popup("Failed to fetch version.", str(E))
        return
    try:
        website_version_regex = re.compile(r'\"__version__ = [0-9+.]*\<')   #(r'(\"productNameBold\":\")([a-zA-Z\s])*(",")')
        version_from_url = website_version_regex.findall(str(version_website_text_uft8))
        version_from_url = float(version_from_url[14:-1])
    except Exception as E:
        logger.exception("Regex on website text failed.")
        custom_popup("Version checkers regex failed.", str(E))
        return
        
    logger.debug("Version checker, url version is: " + version_from_url)

    if version_from_url > __version__:
        logger.debug("Newer version, avaliable.")
        custom_popup("New version out", "Latest version is: "+ str(version_from_url))
        github_open() #Open the github in browerser if newer version is out.

    elif version_from_url <= __version__:
        logger.debug("No new version.")
        custom_popup("No new update released", "Currently running: "+str(__version__) + ". Latest published version: " + str(version_from_url))
    else:
        logger.debug("Version checking failed.")
        custom_popup("Version checking failed", "Version checking failed. Suggest manual look up, on github.")


    return

def check_update_starter():
    check_update_thread = threading.Thread(target=check_update)
    check_update_thread.start()
    return

def check_license():
    logger.debug("Called function check_license")
    webbrowser.open_new(license_url)
    return

def program_not_working():
    logger.debug("Called function program_not_working")
    custom_popup(u"Sorry", "Most likely YouTube has changed something and thus the program needs to be updated with the latest version of one of it's dependencies YouTube-dl. Find out if it's this click \"check for updates\" button. If not this you are probably not putting in correct links to videos.\n If not any of this please report it on GitHub, click the \"GitHub\" button")
    return

def github_open():
    logger.debug("Called function github_open")
    webbrowser.open_new(github_url)
    return



def custom_popup(title_bar, text_to_show):
    logger.debug("Called function custom_popup")
    messagebox.showinfo(title_bar, text_to_show)
    return

def change_download_notification():
    global finish_notification

    #Write to config in memory the saved location
    config['download_settings']['finished_notification'] = finish_notification.get()
    #Write config in memeory to the file.
    try:
        with open(config_file, "w") as tobewritten:
            #config.write(filename)
            config.write(tobewritten)
    except Exception as E:
        logger.exception("Resolution error open dir")
        custom_popup("Config file Error open dir", Exception)

    #Update root TK to ensure menu bar is displaying correctly.
    root.update()
    return


## Chooses the directory to download too, with youtube-dl
def open_dir():
    global directory_name
    user_input = filedialog.askdirectory(initialdir = "/")
    
    #Check if the user choose nothing, and if so does not update.
    if user_input != '' or None:
        directory_name = user_input
    else:
        return

    #Write to config in memory the saved location
    config['download_settings']['file_path'] = directory_name
    #Write config in memeory to the file.
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
## command=threading.Thread(target=main_process).start() isnt used because tkinter on intialising seems to run it.
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
    start_download_button.config(cursor="watch")    #Change the mouse when it hover's over to the OS loading symbol
    

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

    if config.get('download_settings','finished_notification') == "True":
        custom_popup("Download finished", "Download finished.")

    #Turn the button back on.
    start_download_button["state"] = "normal"
    file_menu.entryconfig(0,state=NORMAL)
    start_download_button.config(cursor="arrow") #Change back to the normal mouse cursor when it's hovering over

    return


## Builds the config file with the settings the first time the code is run.
def build_config_file( config, filename):

    
    config['GUI'] = {'theme': 'light'}
    config['download_settings'] = {'standard_resolution': 'Highest resolution',
                                    'file_path': 'False',
                                    'audio_only': 'False',
                                    "finished_notification": "False"}
    try:
        with open(filename, "w") as configfile:
            #config.write(filename)
            config.write(configfile)
    except Exception as E:
        logger.exception("Resolution error")
        custom_popup("Config file Error", Exception)

    return

## Load in config file and validate input 
def load_config_file():
    global start_audio_extract
    global start_resolution
    global start_finish_notification
    #global directory_name
    write_changes = 0
    
    start_resolution = config.get('download_settings','standard_resolution') #config['download_settings']['standard_resolution'] legacy api
    #Validate start resolution config, and if failed set it to the default.
    if start_resolution not in potential_resolutions:
        start_resolution = "Highest resolution"
        config['download_settings']['standard_resolution'] = start_resolution
        write_changes = 1


    start_audio_extract = config.get('download_settings','audio_only')
    #Validate audio extract config, and if failed set it to the default.
    if start_audio_extract != "True" and start_audio_extract != "False":
        start_audio_extract = "False"
        config['download_settings']['audio_only'] = start_audio_extract
        write_changes = 1

    #Check the filepath
    #directory_name = config.get('download_settings','file_path')
    if config.get('download_settings','file_path') == "" or None:
        config['download_settings']['file_path'] = "False"
        write_changes = 1

    start_finish_notification = config.get('download_settings','finished_notification')
    if start_finish_notification != "True" and start_finish_notification != "False":
        config['download_settings']['finished_notification'] = "False"
        write_changes = 1

    #Theme set up
    
    global main_color
    global second_color
    global third_color
    global fourth_color
    global text_color

    theme_choice = config.get('GUI','theme') 
    try:
        main_color, second_color, third_color, fourth_color, text_color = get_theme_color(theme_choice)
    except Exception as E:
        logger.exception("Theme color fetching failed")
        main_color, second_color, third_color, fourth_color, text_color = get_theme_color("light")
        config['GUI']['theme'] = "light"
        write_changes = 1


    if write_changes == 1:
        try:
            with open(config_file, "w") as tobewritten:
                config.write(tobewritten)
        except Exception as E:
            logger.exception("Resolution error open dir")
            custom_popup("Config file Error open dir", Exception)




    return



#TODO
def main():
    #Check for settings
    ## CONFIG
    global config
    config = configparser.ConfigParser()
    config.read(config_file)
    
    if config.sections() == []: # if it's an empty list. Checks if empty config and if yes then builds it with standard settings.
        #Make the settings file.
        build_config_file(config, config_file)
    
    load_config_file() #Load into variables the config values and values associated with them.

    

    return

if __name__ == "__main__":
    main()





##GUI Code bellow

#TK set up
root = Tk()
root.title("YouTube-DL GUI") #Title/Name of program in top bar
path_icon = resource_path('icon.ico') #Program icon path
root.iconbitmap(path_icon) #Icon of the program

root.minsize( 520, 270) #minimum window size
root.geometry("600x300") #Window start up size

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

#potential_resolutions = ["Highest resolution", "2160p", "1440p", "1080p", "720p", "480p","360p", "240p", "Worst resolution"] 
# #Defined earlier with other constants also so configparser has access
working_res = StringVar()
working_res.set(start_resolution) #Standard value is "Highest resolution"
max_resolution = OptionMenu(root, working_res, *potential_resolutions)
max_resolution.configure(width=15) #Sets a constant width of the resolution menu
max_resolution["highlightthickness"] = 0 #Remove highligt border
max_resolution.grid(row=0, column=0, sticky="EW")


#File dialog
download_dir_button = Button( root, text="Download file directory", command=open_dir)
download_dir_button.grid(row=1, column=0, sticky="new")


#Audio extract
audio_extract_selection = BooleanVar()
audio_extract_selection.set(start_audio_extract)
audio_extract_checkbox = Checkbutton(root , text="Extract audio", variable=audio_extract_selection, onvalue=True, offvalue=False, width=15, height=1, anchor=N)
audio_extract_checkbox.grid(row=2, column=0, sticky=N)#, sticky="N")#"NEW")


#Start download button
start_download_button = Button(root, text="Start download", command=start_process, height=10)#, width=18 , height=5) 
start_download_button.grid(row=3, column=0, sticky="NSEW") #, sticky=N+W)

#Download status bar bottom of the window
status_bar = StringVar()
status_bar.set("")
download_status_bar = Label(root, textvariable= status_bar , bd=1, relief=SUNKEN, anchor=E, padx=20) # Test comes from
download_status_bar.grid(row=4, column = 1, sticky=W+E)


#Progress bar bottom of the window
progress_bar = StringVar()
progress_bar.set("Download progress: 0/0")
download_progress_statusbar = Label(root, textvariable= progress_bar , bd=1, relief=SUNKEN, anchor=E)#, padx=20) #text="Download progress: 0/0"
download_progress_statusbar.grid(row=4, column = 0, sticky=W+E)





## TOP bar
menu_bar = Menu(root)
root.config(menu=menu_bar)   #Add menu to root

# tearoff=0 remove line in menu which opens up the menu in a separate window.
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

#Theme submenu
setting_menu_sub_menu = Menu(setting_menu, tearoff=0)
setting_menu_sub_menu.add_command(label="Light", command=lambda: set_theme("light"))
setting_menu_sub_menu.add_command(label="Grey", command=lambda: set_theme("grey"))
setting_menu_sub_menu.add_command(label="Dark", command=lambda: set_theme("dark"))
setting_menu_sub_menu.add_command(label="Black", command=lambda: set_theme("black"))
setting_menu.add_cascade(label="Theme", menu=setting_menu_sub_menu)

#setting_menu.add_command(label="Audio extract always on", command=threading.Thread(target=audio_extract_setting).start()) #TODO 
audio_extract_allways_on = StringVar()
audio_extract_allways_on.set(start_audio_extract)
setting_menu.add_checkbutton(label="Audio extract always on start up", command=audio_extract_setting, onvalue="True", offvalue="False", variable=audio_extract_allways_on)


finish_notification = StringVar()
finish_notification.set(start_finish_notification)
setting_menu.add_checkbutton(label="Finished download nofication", command=change_download_notification, onvalue="True", offvalue="False", variable=finish_notification)

#Help/About
help_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Check for updates", command=check_update_starter)
help_menu.add_command(label="License", command=check_license)
help_menu.add_command(label="Program not working", command=program_not_working)
help_menu.add_command(label="Github", command=github_open)


## Set the colour of the program, colors come from loading of config
root.config(bg=main_color)
Instructions.config(bg=main_color, fg=text_color)
input_url.config(bg=fourth_color, fg=text_color)
max_resolution.config(bg=second_color, fg=text_color, activebackground=third_color, activeforeground=text_color)
max_resolution["menu"].config(bg=third_color,fg=text_color)
download_dir_button.config(bg=second_color, fg=text_color, activebackground=third_color)
audio_extract_checkbox.config(bg=second_color, fg=text_color, activebackground=fourth_color, selectcolor=fourth_color)
start_download_button.config(bg=second_color, fg=text_color, activebackground=third_color)
download_progress_statusbar.config(bg=second_color, fg=text_color)
download_status_bar.config(bg=second_color, fg=text_color)

#Menubar UI elements
menu_bar.config(bg=main_color, fg=text_color, activebackground=third_color)
file_menu.config(bg=main_color, fg=text_color)
setting_menu.config(bg=main_color, fg=text_color)
setting_menu_sub_menu.config(bg=main_color, fg=text_color)
help_menu.config(bg=main_color, fg=text_color)



#TK mainloop
root.mainloop()






