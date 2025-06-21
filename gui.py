# SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance)
# First written by Russ on 18 Jan 2024 (https://github.com/rrrusst/solairia).

# From built-in libraries
import traceback, time, ast
import configparser
import tkinter as tk
from tkinter import filedialog as fd, Entry, Button, Label, Grid, Menu, scrolledtext, Toplevel, Radiobutton, Checkbutton, colorchooser, font, ttk, END, INSERT
from idlelib.tooltip import Hovertip
import threading

# From external libraries
from llama_cpp.llama_chat_format import LlamaChatCompletionHandlerRegistry

# From custom modules
from menu_funcs import export_chat, usage_tips, check_updates, about_info
from config_handler import ConfigHandler
from core_funcs import LlmProcess, load_model, set_personality, evt_send
from main import version

def user_counter(event):
    lbl_input_counter.config(text = "Total characters: " + str(len(event.widget.get("1.0",'end-1c'))))

def pers_counter(event, top_config):
    top_config.pers_counter_var.set("Total characters: " + str(len(event.widget.get("1.0",'end-1c'))))    

def insert_newline(event):
    event.widget.insert("insert", "\n")
    return "break"

def close_app():
    with LlmProcess.lock:
        LlmProcess.is_running = False
    root.destroy()
    for thread in threading.enumerate(): 
        print("Running threads = "+thread.name)

def model_picker(top_config):
    path = fd.askopenfilename(title = "Select an LLM model", filetypes = (("Supported formats", ".gguf"),), parent=top_config)
    if path:
        top_config.path_var.set(path)

def validate_number_input(P):
    return P.isdigit() and len(P) <= 6 or P == ""

def open_config():
    BG_GREY = ConfigHandler.cp["GUI"]["bg_grey"]
    BG_COLOUR = ConfigHandler.cp["GUI"]["bg_colour"]
    FONT_COLOUR_USER = ConfigHandler.cp["GUI"]["font_colour_user"]
    FONT_COLOUR_ASST = ConfigHandler.cp["GUI"]["font_colour_asst"]
    FONT_TYPE = ConfigHandler.cp["GUI"]["font_type"]
    FONT_SIZE = ConfigHandler.cp["GUI"]["font_size"]
    FONT = (FONT_TYPE, FONT_SIZE)
    FONT_BOLD = FONT + ("bold",)
    MENU_FONT = ("Verdana", 11)
    MENU_FONT_BOLD = ("Verdana", 11, "bold")
    
    top_config = Toplevel(padx = 5, pady = 5)
    top_config.title("Config")
    top_config.resizable(False, False)
    top_config.grab_set()   # Grab focus to this window and prevent focus change to lower level windows
    top_config.focus_force()    # Force focus over to this window
    btn_config.config(state = "disabled")

    # Model path config
    frame_model = tk.Frame(top_config)
    frame_model.columnconfigure(0, weight=1)
    top_config.path_var = tk.StringVar()
    lbl_model_path = Label(top_config, text = "LLM Path (.gguf)", font = MENU_FONT_BOLD)
    lbl_model_path.grid(row = 0, column = 0)
    entry_model_path = Entry(frame_model, font = MENU_FONT, width = 40, textvariable = top_config.path_var)
    entry_model_path.grid(row = 0, column = 0, sticky = "we")
    top_config.path_var.set(ConfigHandler.cp["AI"]["model_path"])
    btn_model_picker = Button(frame_model, text = "Choose file", font = MENU_FONT, bg = BG_GREY, command = lambda: model_picker(top_config))
    btn_model_picker.grid(row=0, column=1, sticky = "w")
    frame_model.grid(row = 0, column = 1, sticky = "we")
    Hovertip(frame_model, "To download more Text Generation type LLMs in .gguf format, visit "
             +"\nhttps://huggingface.co/models?pipeline_tag=text-generation&sort=trending&search=gguf")

    # Context size config
    frame_context = tk.Frame(top_config)
    frame_context.columnconfigure(1, weight=1)
    top_config.context_var = tk.StringVar()
    lbl_context = Label(top_config, text = "Context Size", font = MENU_FONT_BOLD, anchor = "n")
    lbl_context.grid(row = 1, column = 0, sticky = "ns")

    val_cmd_context = (top_config.register(validate_number_input), '%P')
    entry_context = Entry(frame_context, font = MENU_FONT, width = 6,  textvariable = top_config.context_var, validate="key", validatecommand = val_cmd_context)
    lbl_context_note = Label(frame_context, text = "(Larger size = slower replies, higher chat memory & input limit)", font = MENU_FONT_BOLD, anchor = "n")
    
    entry_context.grid(row = 0, column = 1, sticky = "w")
    lbl_context_note.grid(row = 0, column = 2, sticky = "w")
    top_config.context_var.set(ConfigHandler.cp["AI"]["context_size"])  # Set context size based on config.ini
    frame_context.grid(row = 1, column = 1, sticky = "nw")
    Hovertip(frame_context, "Context size affects the character limit for your inputs and personality setting,"
             +"\nand the LLM's response length and speed."
             +"\nSetting it higher than what the LLM was tuned for may result in abnormal responses."
             +"\n- For GPU-bound version: If this is set too high and exceeds your VRAM capacity,"
            +"\nthe LLM response will eventually slow down as memory is offloaded to RAM.")
    
    # Personality config
    frame_pers = tk.Frame(top_config)
    lbl_personality = Label(frame_pers, text = "Personality", font = MENU_FONT_BOLD)
    lbl_personality.grid(row = 0, column = 0)
    top_config.txt_personality = scrolledtext.ScrolledText(top_config, bg = BG_COLOUR, fg = FONT_COLOUR_USER, font = MENU_FONT, width = 40, height = 3)
    top_config.txt_personality.grid(row = 2, column = 1, sticky = "we")
    top_config.txt_personality.insert(END, ConfigHandler.cp["AI"]["personality"])    # Set personality text based on config.ini
    top_config.txt_personality.bind("<KeyPress>", lambda event: pers_counter(event, top_config))
    top_config.txt_personality.bind("<KeyRelease>", lambda event: pers_counter(event, top_config))
    # Personality character counter
    top_config.pers_counter_var = tk.StringVar()
    top_config.pers_counter_var.set("Total characters: "+str(len(top_config.txt_personality.get("1.0", "end-1c"))))
    lbl_pers_counter = Label(frame_pers, textvariable = top_config.pers_counter_var)
    lbl_pers_counter.grid(row = 1, column = 0)
    frame_pers.grid(row = 2, column = 0)
    Hovertip(top_config.txt_personality, "Give the LLM a personality or role, or ask it to reply in a certain manner. Leave blank for default. "
             +"\n- e.g. You are a helpful clothes designer who speaks excitedly."
             +"\n- If personality is not being applied, the LLM/prompt template may not support it through"
             +"\nthis config. Instead, you can input it at the start of your chat prompt in the conversation"
             +"\n(longer chats may lead to personality loss with this workaround.)"
             +"\n\n***Changes made will reset chat memory/context.***")

    # Font config
    top_config.font_size_var = tk.IntVar()
    top_config.font_size_var.set(FONT_SIZE) # Initialise the variable with currently-set font size
    top_config.font_type_var = tk.StringVar()
    top_config.font_type_var.set(FONT_TYPE) # Initialise the variable with currently-set font type
    top_config.font_colour_user_var = tk.StringVar()
    top_config.font_colour_user_var.set(FONT_COLOUR_USER)   # Initialise the variable with currently-set colour code
    top_config.font_colour_asst_var = tk.StringVar()
    top_config.font_colour_asst_var.set(FONT_COLOUR_ASST)   # Initialise the variable with currently-set colour code
    top_config.bg_colour_var = tk.StringVar()
    top_config.bg_colour_var.set(BG_COLOUR)   # Initialise the variable with currently-set colour code
    frame_font = tk.Frame(top_config)
    lbl_font = Label(top_config, text = "Chat Font", font = MENU_FONT_BOLD)
    lbl_font.grid(row = 5, column = 0)
    # Font size
    lbl_font_size = Label(frame_font, text = "Size", font = MENU_FONT_BOLD)
    lbl_font_size.grid(row = 0, column = 0)
    combo_font_size = ttk.Combobox(frame_font, textvariable = top_config.font_size_var, state = "readonly")
    font_size_list = []
    for val in range(8, 31):
        font_size_list.append(val)
    combo_font_size["values"] = font_size_list
    combo_font_size.grid(row = 1, column = 0, sticky = "w")
    top_config.font_size_var.set(ConfigHandler.cp["GUI"]["font_size"]) # Set initial font size combobox value based on config.ini
    # Font type
    lbl_font_type = Label(frame_font, text = "Type", font = MENU_FONT_BOLD)
    lbl_font_type.grid(row = 0, column = 1)
    combo_font_type = ttk.Combobox(frame_font, textvariable = top_config.font_type_var, state = "readonly")
    font_type_list = []
    for val in font.families():
        font_type_list.append(val)
    combo_font_type["values"] = font_type_list
    combo_font_type.grid(row = 1, column = 1, sticky = "w")
    # Font colour for User  
    lbl_font_colour_user = Label(frame_font, text = "User Colour", font = MENU_FONT_BOLD)
    lbl_font_colour_user.grid(row = 0, column = 2)
    top_config.lbl_font_colour_user_example = Label(frame_font, text = "Example", font = MENU_FONT, bg = BG_COLOUR, fg = FONT_COLOUR_USER)
    top_config.lbl_font_colour_user_example.grid(row = 1, column = 2)
    btn_font_colour_user = Button(frame_font, text = "Choose colour", font = MENU_FONT, bg = BG_GREY,
                               command = lambda: pick_colour(top_config, "user"))
    btn_font_colour_user.grid(row = 2, column = 2)
    # Font colour for Asst
    lbl_font_colour_asst = Label(frame_font, text = "Asst Colour", font = MENU_FONT_BOLD)
    lbl_font_colour_asst.grid(row = 0, column = 3)
    top_config.lbl_font_colour_asst_example = Label(frame_font, text = "Example", font = MENU_FONT, bg = BG_COLOUR, fg = FONT_COLOUR_ASST)
    top_config.lbl_font_colour_asst_example.grid(row = 1, column = 3)
    btn_font_colour_asst = Button(frame_font, text = "Choose colour", font = MENU_FONT, bg = BG_GREY,
                               command = lambda: pick_colour(top_config, "asst"))
    btn_font_colour_asst.grid(row = 2, column = 3)
    # Background colour
    lbl_bg_colour = Label(frame_font, text = "BG Colour", font = MENU_FONT_BOLD)
    lbl_bg_colour.grid(row = 0, column = 4)
    top_config.lbl_bg_colour_example = Label(frame_font, text = "Example", font = MENU_FONT, fg = BG_COLOUR, bg = BG_COLOUR)
    top_config.lbl_bg_colour_example.grid(row = 1, column = 4)
    btn_bg_colour = Button(frame_font, text = "Choose colour", font = MENU_FONT, bg = BG_GREY,
                               command = lambda: pick_colour(top_config, "bg"))
    btn_bg_colour.grid(row = 2, column = 4)
    frame_font.grid(row = 5, column = 1, sticky = "w")
    ttk.Separator(top_config, orient='horizontal').grid(row = 6, columnspan = 2, sticky = "we")    
    
    # Advanced options label
    lbl_adv_options = Label(top_config, text = "Advanced Options", font = MENU_FONT_BOLD)
    lbl_adv_options.grid(row = 7, columnspan = 2, pady = (10,10))
    ttk.Separator(top_config, orient='horizontal').grid(row = 8, columnspan = 2, sticky = "we")

    # Context management
    top_config.cb_context_mgmt_var = tk.StringVar()
    frame_context_mgmt = tk.Frame(top_config)    
    lbl_context_mgmt = Label(top_config, text = "Context Management", font = MENU_FONT_BOLD)
    lbl_context_mgmt.grid(row = 9, column = 0)
    combo_context_mgmt = ttk.Combobox(frame_context_mgmt, textvariable = top_config.cb_context_mgmt_var, state = "readonly")
    combo_context_mgmt["values"] = ["sliding_window", "periodic_summary"]
    combo_context_mgmt.grid(row = 0, column = 0, sticky = "w")
    top_config.cb_context_mgmt_var.set(ConfigHandler.cp["AI"]["context_mgmt"]) # Set initial combobox value based on config.ini
    frame_context_mgmt.grid(row = 9, column = 1, sticky = "w")
    Hovertip(frame_context_mgmt, "Set the Context Management method that SOLAIRIA will use to keep context/memory "
             +"\nwithin the Context Size."
             +"\n- sliding_window: Uninterrupted chats, but lower context/memory retention "
             +"\n(older parts of chat will gradually be forgotten). Supports lengthier LLM replies."
             +"\n- periodic_summary: Periodically-interrupted chats, but higher context/memory retention "
             +"\nif summarisation is successful (some details may be forgotten). Supports shorter LLM replies.")

    # Enable/disable history tags and reference. Useful to reduce response times, and in cases where <history> tags mess up LLM responses (e.g. in LLMs that need custom prompt templates).
    top_config.cb_history_option_var = tk.StringVar()
    top_config.cb_history_option_var.set(ConfigHandler.cp["AI"]["history_option"])
    lbl_history_option = Label(top_config, text = "Chat History Reference", font = MENU_FONT_BOLD, anchor = "n")
    lbl_history_option.grid(row = 10, column = 0, sticky = "we")
    top_config.cb_history_option = Checkbutton(top_config, text = "Enable", variable = top_config.cb_history_option_var,
                                onvalue = "on", offvalue = "off")
    top_config.cb_history_option.grid(row = 10, column = 1, sticky = "w")
    Hovertip(top_config.cb_history_option, "Enable/disable chat history for the LLM to use as context for its replies."
             +"\n- Enabled: Typical back-and-forth chat experience (with chat history). LLM's response time may be slower."
             +"\n- Disabled: 'Question & Answer' experience (without chat history). LLM's response time may be faster."
             +"\n\n***Changes made will reset chat memory/context.***")


    # Prompt template options
    top_config.cb_p_template_var = tk.StringVar()
    frame_p_template = tk.Frame(top_config)    
    lbl_p_template = Label(top_config, text = "Prompt Template", font = MENU_FONT_BOLD)
    lbl_p_template.grid(row = 11, column = 0)
    combo_p_template = ttk.Combobox(frame_p_template, textvariable = top_config.cb_p_template_var, state = "readonly")
    combo_p_template["values"] = ["auto"]+sorted(list(LlamaChatCompletionHandlerRegistry._chat_handlers.keys())) # Populate values with llama-cpp-python's supported chat handlers (prompt templates)
    combo_p_template.grid(row = 0, column = 0, sticky = "w")
    top_config.cb_p_template_var.set(ConfigHandler.cp["AI"]["prompt_template"]) # Set initial combobox value based on config.ini
    frame_p_template.grid(row = 11, column = 1, sticky = "w")
    Hovertip(frame_p_template, "Set the Prompt Template used by SOLAIRIA. Different LLMs are trained with different prompt templates."
             +"\n- Auto: Default option. Automatically selects based on LLM metadata, if possible."
             +"\n- Other options: Manually set the prompt template. Useful if LLM produces poor/unusable replies. "
             +"\nRefer to the LLM's model card on HuggingFace website for the appropriate prompt template.")

    # Show/hide LLM stats (llm.verbose)
    top_config.cb_llm_stats_var = tk.BooleanVar()
    lbl_llm_stats = Label(top_config, text = "Show LLM Performance", font = MENU_FONT_BOLD, anchor = "n")
    lbl_llm_stats.grid(row = 12, column = 0, sticky = "we")
    top_config.cb_llm_stats = Checkbutton(top_config, text = "Enable", variable = top_config.cb_llm_stats_var,
                                onvalue = True, offvalue = False)
    top_config.cb_llm_stats_var.set(ConfigHandler.cp["AI"]["llm_stats_enable"])
    top_config.cb_llm_stats.grid(row = 12, column = 1, sticky = "w")
    Hovertip(top_config.cb_llm_stats, "Enable/disable display of LLM performance stats."
             +"\nStats vary based on your hardware specs.")

    # Config options
    frame_config_options = tk.Frame(top_config)
    lbl_config_options = Label(top_config, text = "Config Options", font = MENU_FONT_BOLD)
    lbl_config_options.grid(row = 13, column = 0)
    # Export config button
    btn_export_config = Button(frame_config_options, text = "Export", font = MENU_FONT, bg = BG_GREY,
                               command = lambda: export_config(top_config,
                                                               entry_model_path.get(),  #model_path
                                                               str(top_config.context_var.get()),    # context_size
                                                               top_config.txt_personality.get("1.0", "end-1c"),    #personality
                                                               str(top_config.font_size_var.get()), #font_size
                                                               str(top_config.font_type_var.get()), #font_type
                                                               str(top_config.font_colour_user_var.get()), #font_colour_user
                                                               str(top_config.font_colour_asst_var.get()), #font_colour_asst
                                                               str(top_config.bg_colour_var.get()), #bg_colour
                                                               str(top_config.cb_history_option_var.get()), #history option
                                                               str(top_config.cb_context_mgmt_var.get()),   #context management option
                                                               str(top_config.cb_p_template_var.get()), #prompt template option
                                                               str(top_config.cb_llm_stats_var.get())   #llm performance stats option
                                                               ))
    btn_export_config.grid(row=0, column=0)
    # Import config button
    btn_import_config = Button(frame_config_options, text = "Import", font = MENU_FONT, bg = BG_GREY,
                               command = lambda: import_config(top_config))
    btn_import_config.grid(row=0, column=1)    
    # Restore defaults button
    btn_default_config = Button(frame_config_options, text = "Restore defaults", font = MENU_FONT, bg = BG_GREY,
                               command = lambda: default_config(top_config))
    btn_default_config.grid(row=0, column=2)    
    frame_config_options.grid(row = 13, column = 1, sticky = "w")

    # Save config button
    frame_btn_confirm = tk.Frame(top_config)
    btn_save_config = Button(frame_btn_confirm, text = "Ok", font = MENU_FONT_BOLD, bg = BG_GREY, width = 6,
                             command = lambda: save_config(top_config,
                                                           entry_model_path.get(),  #model_path
                                                           str(top_config.context_var.get()),    # context_size
                                                           top_config.txt_personality.get("1.0", "end-1c"),    #personality
                                                           str(top_config.font_size_var.get()), #font_size
                                                           str(top_config.font_type_var.get()), #font_type
                                                           str(top_config.font_colour_user_var.get()), #font_colour_user
                                                           str(top_config.font_colour_asst_var.get()), #font_colour_asst
                                                           str(top_config.bg_colour_var.get()), #bg_colour
                                                           str(top_config.cb_history_option_var.get()), #history option
                                                           str(top_config.cb_context_mgmt_var.get()),   #context management option
                                                           str(top_config.cb_p_template_var.get()), #prompt template option
                                                           str(top_config.cb_llm_stats_var.get())   #llm performance stats option
                                                           ))
    btn_save_config.grid(row=0, column=0, padx = 10)
    # Cancel button
    btn_cancel_config = Button(frame_btn_confirm, text = "Cancel", font = MENU_FONT_BOLD, bg = BG_GREY,
                               command = lambda: [btn_config.config(state="normal"), top_config.destroy()])
    btn_cancel_config.grid(row=0, column=1)
    frame_btn_confirm.grid(row = 14, column = 1, sticky = "e")

    # Config status label
    top_config.lbl_config_status_var = tk.StringVar()
    top_config.lbl_config_status_var.set("Press Ok to apply changes.")
    lbl_config_status = Label(top_config, textvariable = top_config.lbl_config_status_var, borderwidth=2, relief = "ridge", anchor = "w")
    lbl_config_status.grid(row = 15, column = 0, columnspan = 2, sticky = "we")
    
    # Set only column1 weight to 1 to adapt to horizontal window adjustments
    top_config.columnconfigure(1, weight=1)

    # Set all row weights to 1 to adapt to vertical window adjustments
    total_rows = top_config.grid_size()[1]
    for row in range(total_rows):
        top_config.rowconfigure(row, weight=1)
    top_config.protocol("WM_DELETE_WINDOW", lambda: [btn_config.config(state="normal"), top_config.destroy()])

def pick_colour(top_config, role):
    match(role):
        case "user":
            colour = colorchooser.askcolor(title = "Choose User's font colour")[1]  # Set to colour hexadecimal value
            if colour is not None:
                top_config.font_colour_user_var.set(colour)
                top_config.lbl_font_colour_user_example.config(fg = colour)
        case "asst":
            colour = colorchooser.askcolor(title = "Choose Assistant's font colour")[1]
            if colour is not None:
                top_config.font_colour_asst_var.set(colour) # Set to colour hexadecimal value
                top_config.lbl_font_colour_asst_example.config(fg = colour)
        case "bg":
            colour = colorchooser.askcolor(title = "Choose Background colour")[1]
            if colour is not None:
                top_config.bg_colour_var.set(colour) # Set to colour hexadecimal value
                top_config.lbl_bg_colour_example.config(bg = colour, fg = colour)
                top_config.lbl_font_colour_user_example.config(bg = colour)
                top_config.lbl_font_colour_asst_example.config(bg = colour)

def save_config(top_config, m_path, ct_size, pers_val, fsize_val, ftype_val, fcol_user_val, fcol_asst_val, bgcol_val, hist_setting, ct_mgmt, ptemplate_setting, llm_stats_setting):
    edit_flag = True    # If any logic checks fail/fail-equivalent, set edit_flag to False

    if LlmProcess.is_running == True:
        match(LlmProcess.llm_status):
            case "Thinking":
                tk.messagebox.showinfo("SOLAIRIA is still thinking",  "Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.")
                return
            case "Reading file":
                tk.messagebox.showinfo("SOLAIRIA is still reading a file",  "Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.")
                return
            case "Compressing memory":
                tk.messagebox.showinfo("SOLAIRIA is still compressing memory",  "Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.")
                return
            case _:
                with LlmProcess.lock:
                    LlmProcess.is_running = False
                    LlmProcess.llm_status = "Idle (reply stopped to save config settings)"
                time.sleep(0.5) # Sleep 0.5s to allow text generation in send() function to properly stop before proceeding. This allows variables used in send() like memory/context (root.prev_prompts) to be correctly edited by subsequent code.
    else:
        with LlmProcess.lock:
            LlmProcess.llm_status = "Idle"
    lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
    old_personality = ConfigHandler.cp["AI"]["personality"]   # old_personality used for better readability of code later

    # Update context_char_limit, my_prompt_limit and personality_limit
    context_size = int(ct_size)
    root.context_char_limit = context_size*4 # Formula is with reference to context_char_limit declared near start of code
    root.my_prompt_limit = int(root.context_char_limit*0.2)   # Formula is with reference to context_char_limit declared near start of code
    root.personality_limit = int(root.context_char_limit*0.1) # Formula is with reference to context_char_limit declared near start of code
    
    # Check length of personality input
    if len(pers_val) > root.personality_limit:
        str_error = "Your input for Personality was "+str(len(pers_val))+" characters long. Please keep within "+str(root.personality_limit)+" characters. This limit depends on Context Size."
        tk.messagebox.showinfo("Error",  str_error)
        edit_flag = False
        return

    # Update config.ini only if edit_flag is True
    if edit_flag == True:
        # Check if model path or context size is different from config.ini
        if m_path != ConfigHandler.cp["AI"]["model_path"] or int(ct_size) != int(ConfigHandler.cp["AI"]["context_size"]) or ptemplate_setting != ConfigHandler.cp["AI"]["prompt_template"]:
            top_config.lbl_config_status_var.set("LLM, Context Size or Prompt Template was changed. Reloading LLM, please wait...")
            top_config.update_idletasks()

            # Unload existing LLM. This step is needed for GPU-bound version, because if existing LLM + new LLM needs more VRAM than
            # what GPU has, then loading a new LLM without unloading previous one will exceed GPU VRAM and cause new LLM to load
            # partially in GPU VRAM, resulting in partial/full usage of CPU processing for GPU-bound version.
            load_model("", ct_size, ptemplate_setting)
            
            if load_model(m_path, ct_size, ptemplate_setting): # If model loaded successfully, or unloaded successfully due to empty model path
                ConfigHandler.cp.set("AI", "model_path", m_path)
                ConfigHandler.cp.set("AI", "context_size", ct_size)
                ConfigHandler.cp.set("AI", "prompt_template", ptemplate_setting)
            else:
                return

        # Check if old and new personality is different
        if old_personality.strip() != pers_val.strip():
            ConfigHandler.cp.set("AI", "personality", pers_val)
            root.msglist = []
            set_personality()
            chat_box.insert(END, "\n---Personality change detected. Memory/context has been reset.---", "tag_info")
            chat_box.see("end")

        # Check if chat history checkbox option is different from config.ini
        if hist_setting != ConfigHandler.cp["AI"]["history_option"]:
            root.msglist = []
            chat_box.insert(END, "\n---Chat History Reference setting was changed. Memory/context has been reset.---", "tag_info")
            chat_box.see("end")

        # Check if LLM has been loaded first. If not loaded, the llm.verbose setting does not exist and cannot be set   
        if LlmProcess.llm is not None:
            LlmProcess.llm.verbose = ast.literal_eval(llm_stats_setting)   # Turns on or off display of LLM stats

        # Set config parameters with values that are to be written to config.ini
        ConfigHandler.cp.set("GUI", "font_size", fsize_val)
        ConfigHandler.cp.set("GUI", "font_type", ftype_val)
        ConfigHandler.cp.set("GUI", "font_colour_user", fcol_user_val)
        ConfigHandler.cp.set("GUI", "font_colour_asst", fcol_asst_val)
        ConfigHandler.cp.set("GUI", "bg_colour", bgcol_val)
        ConfigHandler.cp.set("AI", "history_option", hist_setting)
        ConfigHandler.cp.set("AI", "context_mgmt", ct_mgmt)
        ConfigHandler.cp.set("AI", "llm_stats_enable", llm_stats_setting)
        with open("config.ini", "w", encoding = "utf-8") as cfg_file:
           ConfigHandler.cp.write(cfg_file)
           
        # Update root UI elements with new settings
        FONT_TYPE = ftype_val
        FONT_SIZE = fsize_val
        FONT = (FONT_TYPE, FONT_SIZE)
        FONT_BOLD = FONT + ("bold",)
        FONT_COLOUR_USER = fcol_user_val
        FONT_COLOUR_ASST = fcol_asst_val
        BG_COLOUR = bgcol_val

        chat_box.config(font = FONT, background = BG_COLOUR)
        txt_user.config(font = FONT, foreground = FONT_COLOUR_USER, background = BG_COLOUR)
        chat_box.tag_config("tag_user", font = FONT_BOLD, foreground = FONT_COLOUR_USER)
        chat_box.tag_config("tag_asst", foreground = FONT_COLOUR_ASST)
        chat_box.tag_config("tag_info", foreground = FONT_COLOUR_USER)
        print("Wrote to config.ini")

    btn_config.config(state = "normal")
    top_config.destroy()

def export_config(top_config, m_path, ct_size, pers_val, fsize_val, ftype_val, fcol_user_val, fcol_asst_val, bgcol_val, hist_setting, ct_mgmt, ptemplate_setting, llm_stats_setting):
    cp_export = configparser.ConfigParser()
    cp_export["AI"] = {}
    cp_export["GUI"] = {}

    # Set AI config parameters with values that are to be exported
    cp_export.set("AI", "model_path", m_path)
    cp_export.set("AI", "context_size", ct_size)
    cp_export.set("AI", "personality", pers_val)
    cp_export.set("AI", "history_option", hist_setting)
    cp_export.set("AI", "context_mgmt", ct_mgmt)
    cp_export.set("AI", "prompt_template", ptemplate_setting)
    cp_export.set("AI", "llm_stats_enable", llm_stats_setting)
    
    # Initialise these GUI config parameters as they are not in Config menu
    cp_export.set("GUI", "bg_grey", ConfigHandler.cp["GUI"]["bg_grey"])

    # Set GUI config parameters with values that are to be exported
    cp_export.set("GUI", "font_size",  fsize_val)
    cp_export.set("GUI", "font_type", ftype_val)
    cp_export.set("GUI", "font_colour_user", fcol_user_val)
    cp_export.set("GUI", "font_colour_asst", fcol_asst_val)
    cp_export.set("GUI", "bg_colour",  bgcol_val)
    
    file_name = fd.asksaveasfilename(initialfile = "export_config.ini", defaultextension = ".ini", filetypes=(("INI file", ".ini"), ("All Files","*.*")), parent=top_config)
    if file_name:
        with open(file_name, "w", encoding = "utf-8") as cfg_file:
           cp_export.write(cfg_file)

def import_config(top_config):
    cp_import = configparser.ConfigParser()
    file_name =  fd.askopenfilename(title = "Select a file", filetypes = (("INI file", ".ini"),), parent=top_config)
    if file_name:
        cp_import.read(file_name, encoding = "utf-8")
        try:
            # AI Settings
            top_config.path_var.set(cp_import["AI"]["model_path"])
            top_config.context_var.set(cp_import["AI"]["context_size"])
            top_config.txt_personality.delete("1.0", END)
            top_config.txt_personality.insert(END, cp_import["AI"]["personality"])
            top_config.cb_history_option_var.set(cp_import["AI"]["history_option"])
            top_config.cb_context_mgmt_var.set(cp_import["AI"]["context_mgmt"])
            top_config.cb_p_template_var.set(cp_import["AI"]["prompt_template"])
            top_config.cb_llm_stats_var.set(cp_import["AI"]["llm_stats_enable"])

            # GUI Settings
            top_config.font_size_var.set(cp_import["GUI"]["font_size"])
            top_config.font_type_var.set(cp_import["GUI"]["font_type"]) 
            top_config.font_colour_user_var.set(cp_import["GUI"]["font_colour_user"])
            top_config.lbl_font_colour_user_example.config(fg = cp_import["GUI"]["font_colour_user"], bg = cp_import["GUI"]["bg_colour"])
            top_config.font_colour_asst_var.set(cp_import["GUI"]["font_colour_asst"])
            top_config.lbl_font_colour_asst_example.config(fg = cp_import["GUI"]["font_colour_asst"], bg = cp_import["GUI"]["bg_colour"])
            top_config.bg_colour_var.set(cp_import["GUI"]["bg_colour"])
            top_config.lbl_bg_colour_example.config(bg = cp_import["GUI"]["bg_colour"], fg = cp_import["GUI"]["bg_colour"])
        except KeyError as e:
            tk.messagebox.showinfo("Incomplete Config Import",  "The "+str(e)+" setting is missing from your imported config. Some settings may not have been imported over.")
        except:
            traceback.print_exc()

def default_config(top_config):
    # AI settings in Config window
    top_config.context_var.set(ConfigHandler.default_cfg_ai["context_size"])
    top_config.txt_personality.delete("1.0", END)
    top_config.txt_personality.insert(END, ConfigHandler.default_cfg_ai["personality"])
    top_config.pers_counter_var.set("Total characters: 0")
    top_config.cb_history_option_var.set(ConfigHandler.default_cfg_ai["history_option"])
    top_config.cb_context_mgmt_var.set(ConfigHandler.default_cfg_ai["context_mgmt"])
    top_config.cb_p_template_var.set(ConfigHandler.default_cfg_ai["prompt_template"])
    top_config.cb_llm_stats_var.set(ConfigHandler.default_cfg_ai["llm_stats_enable"])

    # GUI settings in Config window
    top_config.font_size_var.set(ConfigHandler.default_cfg_gui["font_size"])
    top_config.font_type_var.set(ConfigHandler.default_cfg_gui["font_type"])
    top_config.font_colour_user_var.set(ConfigHandler.default_cfg_gui["font_colour_user"])
    top_config.lbl_font_colour_user_example.config(fg = ConfigHandler.default_cfg_gui["font_colour_user"], bg = ConfigHandler.default_cfg_gui["bg_colour"])
    top_config.font_colour_asst_var.set(ConfigHandler.default_cfg_gui["font_colour_asst"])
    top_config.lbl_font_colour_asst_example.config(fg = ConfigHandler.default_cfg_gui["font_colour_asst"], bg = ConfigHandler.default_cfg_gui["bg_colour"])
    top_config.bg_colour_var.set(ConfigHandler.default_cfg_gui["bg_colour"])
    top_config.lbl_bg_colour_example.config(bg = ConfigHandler.default_cfg_gui["bg_colour"], fg = ConfigHandler.default_cfg_gui["bg_colour"])

def clear_chat():
    if LlmProcess.llm_status != "Reading file":
        with LlmProcess.lock:
            LlmProcess.is_running = False
        chat_box.delete("1.0", END)
        with LlmProcess.lock:
            LlmProcess.llm_status = "Idle"
        lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
    else:
        chat_box.insert(END, "\n---Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.---\n", "tag_info")
        chat_box.see("end")

def force_stop(event):
    if LlmProcess.llm_status != "Reading file":
        with LlmProcess.lock:
            LlmProcess.is_running = False
            LlmProcess.llm_status = "Idle"
        lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
    else:
        chat_box.insert(END, "\n---Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.---\n", "tag_info")
        chat_box.see("end")

def reset_memory():
    with LlmProcess.lock:
        LlmProcess.is_running = False    
    answer = tk.messagebox.askyesno("Reset Memory", "Are you sure you want to reset memory? Previous conversation memory/context will be gone.")
    if answer:
        root.msglist = []
        chat_box.insert(END, "\n---Memory/context has been reset---", "tag_info")
        chat_box.see("end")
    with LlmProcess.lock:
        LlmProcess.llm_status = "Idle"
    lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)

# Create Tkinter object 
root = tk.Tk()
root.title("SOLAIRIA v"+version)
Grid.rowconfigure(root, 1, weight=1)
Grid.columnconfigure(root, 0, weight=1)

with LlmProcess.lock:
    LlmProcess.is_running = False
root.msglist = []

# Create GUI variables in root object
root.BG_GREY = ConfigHandler.cp["GUI"]["bg_grey"]
root.BG_COLOUR = ConfigHandler.cp["GUI"]["bg_colour"]
root.FONT_COLOUR_USER = ConfigHandler.cp["GUI"]["font_colour_user"]
root.FONT_COLOUR_ASST = ConfigHandler.cp["GUI"]["font_colour_asst"]
root.FONT_TYPE = ConfigHandler.cp["GUI"]["font_type"]
root.FONT_SIZE = ConfigHandler.cp["GUI"]["font_size"]
root.FONT = (root.FONT_TYPE, root.FONT_SIZE)
root.FONT_BOLD = root.FONT + ("bold",)
root.MENU_FONT = ("Verdana", 11)
root.MENU_FONT_BOLD = ("Verdana", 11, "bold")

# Formula for context character limit
# 1 token = ~4 to 4.5 characters
# This helps inform User if their prompts are too long in terms of characters, since informing with token count is not easily understood and remedied.
root.context_char_limit = int(ConfigHandler.cp["AI"]["context_size"])*4

# Formulas for personality and prompt limit
# Context size allocation: 0.1 to personality, 0.2 to my_prompt (user prompt), 0.25 to output (set in generate_text_from_prompt() function). Remaining in prev_prompts and buffer.
# This gives buffer for summarisation to keep within context_size.
root.personality_limit = int(root.context_char_limit*0.1)
root.my_prompt_limit = int(root.context_char_limit*0.2)

# Create a menu bar
menu_bar = Menu(root)
root.config(menu = menu_bar)

# File menu
file_menu = Menu(menu_bar, tearoff = False)
file_menu.add_command(label = "Export chat log", command = lambda: export_chat(root, chat_box.get("1.0", END)))
file_menu.add_separator()
file_menu.add_command(label = "Exit", command = close_app)
menu_bar.add_cascade(label = "File", menu = file_menu)

# Help menu
help_menu = Menu(menu_bar, tearoff = False)
help_menu.add_command(label = "Usage tips", command = lambda: usage_tips(root.MENU_FONT, root.MENU_FONT_BOLD))
help_menu.add_command(label = "Check for updates", command = check_updates)
help_menu.add_command(label = "About", command = lambda: about_info(version, root.MENU_FONT, root.MENU_FONT_BOLD))
menu_bar.add_cascade(label = "Help", menu = help_menu)

# Upper screen status and buttons
frame_status = tk.Frame(root)
frame_status.rowconfigure((0,1), weight=1)
frame_status.columnconfigure((0,1,2,3), weight=1)

# Config button
btn_config = Button(frame_status, text = "Config", font = root.MENU_FONT_BOLD, bg = root.BG_GREY,
              command = open_config)
btn_config.grid(row = 0, column = 0, sticky = "we")
Hovertip(btn_config, "Configure various functional and interface settings."
         +"\nThis is also where you select an LLM to load and customise.")
# Analyse Text File  button
btn_analyse_tf = Button(frame_status, text = "Analyse Text File", font = root.MENU_FONT_BOLD, bg = root.BG_GREY,
              command = lambda: evt_send(None, "/f"))   # Pass the '/f' command to evt_send() function to run analyse_text_file() in the 'Send' thread
btn_analyse_tf.grid(row = 0, column = 1, sticky = "we")
Hovertip(btn_analyse_tf, "Analyses a text file. Current task/reply will be stopped."
         +"\nThe file will be split into parts and an analysis provided for each part."
         +"\nIf SOLAIRIA has sufficient context/memory, a summary of the analysis will be given at the end."
         +"\n\nShortcut commmand: /f")
# Clear chat window button
btn_clr_chat = Button(frame_status, text = "Clear Chat", font = root.MENU_FONT_BOLD, bg = root.BG_GREY,
              command = clear_chat)
btn_clr_chat.grid(row = 0, column = 2, sticky = "we")
Hovertip(btn_clr_chat, "Clears chat window. Current task/reply will be stopped."
         +"\nConversation memory is not affected."
         +"\n\nShortcut command: /clear")
# Reset memory button
btn_reset_mem = Button(frame_status, text = "Reset Memory", font = root.MENU_FONT_BOLD, bg = root.BG_GREY,
              command = reset_memory)
btn_reset_mem.grid(row = 0, column = 3, sticky = "we")
Hovertip(btn_reset_mem, "Resets SOLAIRIA's memory/context. Current task/reply will be stopped."
         +"\nSOLAIRIA will not be able to reference earlier parts of the conversation."
         +"\n\nShortcut command: /r")
# LLM name
lbl_llm_name_var = tk.StringVar()
lbl_llm_name_var.set("LLM Loaded: None")
lbl_llm_name = Label(frame_status, textvariable = lbl_llm_name_var, borderwidth=2, relief="ridge", anchor = "w")
lbl_llm_name.grid(row = 1, column = 0, columnspan = 4, sticky = "we")
frame_status.grid(row=0, columnspan = 2, sticky = "we")

# Main chat message box
chat_box = scrolledtext.ScrolledText(root, bg = root.BG_COLOUR, fg = root.FONT_COLOUR_USER, font = root.FONT, width = 60, wrap = "word")
chat_box.grid(row=1, column=0, columnspan=2, sticky = "nsew")
chat_box.tag_config("tag_user", font = root.FONT_BOLD, foreground = root.FONT_COLOUR_USER, spacing1 = 10, spacing3 = 5)
chat_box.tag_config("tag_asst", foreground = root.FONT_COLOUR_ASST)
chat_box.tag_config("tag_info", foreground = root.FONT_COLOUR_USER, justify = "center")
chat_box.bind("<Key>", "break")
chat_box.bind("<Escape>", force_stop)
chat_box.bind("<Control-c>", lambda event: None)
chat_box.bind("<Control-a>", lambda event: None)

# Status text
ttk.Separator(root, orient='horizontal').grid(row = 2, column = 0, columnspan = 2, pady = 10, sticky = "we")
lbl_status_var = tk.StringVar()
lbl_status_var.set("SOLARIA is: Idle")
lbl_status = Label(root, textvariable = lbl_status_var, font = root.MENU_FONT, borderwidth=2, relief="ridge")
lbl_status.grid(row=2, column = 0, columnspan = 2, sticky = "w")    # Placed above the Separator

# User chat input box
txt_user = scrolledtext.ScrolledText(root, bg = root.BG_COLOUR, fg = root.FONT_COLOUR_USER, font = root.FONT, width = 55, height = 3, wrap = "word")
txt_user.grid(row=3, column=0, sticky = "NSEW")
txt_user.bind("<Return>", "break")
txt_user.bind("<Return>", lambda event: evt_send(event, txt_user.get("1.0", "end-1c")))
txt_user.bind("<KeyPress>", user_counter)
txt_user.bind("<KeyRelease>", user_counter)
txt_user.bind("<Shift-Return>", insert_newline)
txt_user.bind("<Escape>", force_stop)

# Send button
btn_send = Button(root, text = "Send", font = root.MENU_FONT_BOLD, bg = root.BG_GREY,
              command = lambda: evt_send(None, txt_user.get("1.0", "end-1c")))
btn_send.grid(row=3, column=1, sticky = "nsew")
Hovertip(btn_send, "Sends your message, which will be processed offline "
         +"\nusing your computer's hardware."
         +"\n- [Enter] to send."
         +"\n- [Shift+Enter] to insert new lines."
         +"\n- [Esc] to force-stop LLM's reply")

# User input character counter
lbl_input_counter = Label(root, text = "Total characters: 0")
lbl_input_counter.grid(row=4, sticky = "w")

# Load model, and if unable to load successfully, open the config window
if not load_model(ConfigHandler.cp["AI"]["model_path"], ConfigHandler.cp["AI"]["context_size"], ConfigHandler.cp["AI"]["prompt_template"]):
    open_config()

# Set llm.verbose parameter if LLM object is not None
if LlmProcess.llm is not None:
    LlmProcess.llm.verbose = ast.literal_eval(ConfigHandler.cp["AI"]["llm_stats_enable"])    # Turns on or off display of LLM stats
