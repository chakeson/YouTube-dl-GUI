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
    if file_path != False or None:
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
                logging.exception('msg') #TODO
                custom_popup("Warning YouTube-dl error", Exception)
            

        logger.debug("Finished the download")

        #Update the progress bar
        buildstr = "Download progress: " + str(index)+ "/" + str(len(user_input))
        status_var.set(buildstr)
        root.update()
        logger.debug("GUI updated")


        
    return

## UI settings functions

def audio_extract_setting():
    
    audio_extract_setting_choice = config.get('download_settings','audio_only')
    #Validate audio extract config, and if failed run config loading and validation.
    if audio_extract_setting_choice != "True" or "False":
        load_config_file()
        audio_extract_setting_choice = config.get('download_settings','audio_only') #Over write the new ones.
    
    if audio_extract_setting_choice == "True":
        audio_extract_selection = "False"
    else:
        audio_extract_selection = "True"

    config['download_settings']['audio_only'] = audio_extract_selection
            
    try:
        with open(config_file, "w") as tobewritten:
            config.write(tobewritten)
    except Exception as E:
        logger.exception("Resolution error open dir")
        custom_popup("Config file Error open dir", Exception)
 

    return

##THEME functions
def get_theme_color(theme_choice):
    #Function that contains themes colors

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
    
    elif theme_choice == "dark":   #Dark theme color based on https://uxdesign.cc/dark-mode-ui-design-the-definitive-guide-part-1-color-53dcfaea5129
        main_color = "#121212"
        second_color = "#212121"
        third_color = "#424242"
        fourth_color = "#212121"
        text_color = "#BDBDBD"

    elif theme_choice == "black":   #Dark theme color based on https://uxdesign.cc/dark-mode-ui-design-the-definitive-guide-part-1-color-53dcfaea5129
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
    main_color, second_color, third_color, fourth_color, text_color = get_theme_color(theme_choice)

    #Main UI elements
    root.config(bg=main_color)
    Instructions.config(bg=main_color, fg=text_color)
    input_url.config(bg=fourth_color, fg=text_color)
    max_resolution.config(bg=second_color, fg=text_color, activebackground=third_color, activeforeground=text_color)
    max_resolution["menu"].config(bg=third_color,fg=text_color)
    download_dir_button.config(bg=second_color, fg=text_color, activebackground=third_color)
    audio_extract_checkbox.config(bg=second_color, fg=text_color, activebackground=fourth_color, selectcolor=fourth_color)
    start_download_button.config(bg=second_color, fg=text_color, activebackground=third_color)
    download_progress_statusbar.config(bg=second_color, fg=text_color)

    #Menubar UI elements
    menu_bar.config(bg=main_color, fg=text_color, activebackground=third_color)
    file_menu.config(bg=main_color, fg=text_color)
    setting_menu.config(bg=main_color, fg=text_color)
    setting_menu_sub_menu.config(bg=main_color, fg=text_color)
    help_menu.config(bg=main_color, fg=text_color)

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
    write_changes = 0
    
    start_resolution = config.get('download_settings','standard_resolution') #config['download_settings']['standard_resolution'] legacy api
    #Validate start resolution config, and if failed set it to the default.
    if start_resolution not in potential_resolutions:
        start_resolution = "Highest resolution"
        config['download_settings']['standard_resolution'] = start_resolution
        write_changes = 1


    start_audio_extract = config.get('download_settings','audio_only')
    #Validate audio extract config, and if failed set it to the default.
    if start_audio_extract != "True" or "False":
        start_audio_extract = "False"
        config['download_settings']['audio_only'] = start_audio_extract
        write_changes = 1

    #directory_name = config.get('download_settings','file_path')
    if config.get('download_settings','file_path') == "" or None:
        config['download_settings']['file_path'] = "False"
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
max_resolution["highlightthickness"] = 0 #Remove highligt border
max_resolution.grid(row=0, column=0, sticky="EW")


#File dialog
download_dir_button = Button( root, text="Download file directory", command=open_dir)
download_dir_button.grid(row=1, column=0, sticky="new")


#Audio extract
audio_extract_selection = BooleanVar()
audio_extract_selection.set(start_audio_extract)
audio_extract_checkbox = Checkbutton(root , text="Extract audio", variable=audio_extract_selection, onvalue=True, offvalue=False, width=15, height=1, anchor="n")
audio_extract_checkbox.grid(row=2, column=0, sticky=N)#, sticky="N")#"NEW")


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
setting_menu_sub_menu.add_command(label="Light", command=lambda: set_theme("light")) #TODO
setting_menu_sub_menu.add_command(label="Dark", command=lambda: set_theme("dark")) #TODO
setting_menu_sub_menu.add_command(label="Black", command=lambda: set_theme("black")) #TODO
setting_menu.add_cascade(label="Theme", menu=setting_menu_sub_menu)

setting_menu.add_command(label="Audio extract always on", command=threading.Thread(target=audio_extract_setting).start()) #TODO 



#Help/About
help_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Check for updates", command=check_update)
help_menu.add_command(label="License", command=check_license)
help_menu.add_command(label="Program not working", command=program_not_working)
help_menu.add_command(label="Github", command=github_open)


## Set the colour of the program
root.config(bg=main_color)
Instructions.config(bg=main_color, fg=text_color)
input_url.config(bg=fourth_color, fg=text_color)
max_resolution.config(bg=second_color, fg=text_color, activebackground=third_color, activeforeground=text_color)
max_resolution["menu"].config(bg=third_color,fg=text_color)
download_dir_button.config(bg=second_color, fg=text_color, activebackground=third_color)
audio_extract_checkbox.config(bg=second_color, fg=text_color, activebackground=fourth_color, selectcolor=fourth_color)
start_download_button.config(bg=second_color, fg=text_color, activebackground=third_color)
download_progress_statusbar.config(bg=second_color, fg=text_color)

#Menubar UI elements
menu_bar.config(bg=main_color, fg=text_color, activebackground=third_color)
file_menu.config(bg=main_color, fg=text_color)
setting_menu.config(bg=main_color, fg=text_color)
setting_menu_sub_menu.config(bg=main_color, fg=text_color)
help_menu.config(bg=main_color, fg=text_color)













root.mainloop()






