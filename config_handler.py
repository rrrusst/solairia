# SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance)
# First written by Russ on 18 Jan 2024 (https://github.com/rrrusst/solairia).

# From built-in libraries
import os, sys, traceback
import configparser

class ConfigHandler:
    dirname = ""

    # This if...else needs to occur first before any subsequent references to file directories
    if getattr(sys, 'frozen', False):
        ''' If the application is run as a bundle, the PyInstaller bootloader
        extends the sys module by a flag frozen=True and sets the app 
        path into variable _MEIPASS'.
        Directory of .exe is in os.path.dirname(sys.executable)'''
        dirname = os.path.dirname(sys.executable)
    else:
        dirname = os.path.dirname(__file__)

    # Check/create config.ini on launch
    #cp = configparser.ConfigParser(allow_no_value=True, comment_prefixes='/')
    cp = configparser.ConfigParser()
    default_cfg_ai = {"model_path": "", "context_size": "2048", "personality": "", "history_option": "on", "context_mgmt": "sliding_window",
                      "prompt_template": "auto", "llm_stats_enable": "False"}
    default_cfg_gui = {"bg_grey": "#ABB2B9", "bg_colour": "#2C3E50", "font_size": "13", "font_type": "Verdana",
                       "font_colour_user": "#EAECEE", "font_colour_asst": "#EAECEE"}
    if not os.path.exists("config.ini"):
        cp["AI"] = default_cfg_ai
        cp["GUI"] = default_cfg_gui
        with open("config.ini", "w", encoding = "utf-8") as cfg_file:
           cp.write(cfg_file)
        print("No config.ini found. New config.ini has been created with default settings.")
    else:
        cp.read("config.ini", encoding = "utf-8")
        if dict(cp.items("AI")).keys() !=  default_cfg_ai.keys() or dict(cp.items("GUI")).keys() !=  default_cfg_gui.keys():
            # If some keys are not present = .ini file has different structure. Hence, overwrite with default config.ini. 
            cp["AI"] = default_cfg_ai
            cp["GUI"] = default_cfg_gui
            with open("config.ini", "w", encoding = "utf-8") as cfg_file:
               cp.write(cfg_file)
            print("Some config.ini keys are MISSING. New config.ini has been created with default settings.")
        else:
            # All keys are present = .ini file has same structure. Hence, do nothing
            print("All config.ini keys are PRESENT.")
