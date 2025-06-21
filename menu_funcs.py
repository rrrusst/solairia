# SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance)
# First written by Russ on 18 Jan 2024 (https://github.com/rrrusst/solairia).

# From built-in libraries
import webbrowser
from tkinter import filedialog as fd, Text, scrolledtext, Label, Toplevel, END, INSERT

def export_chat(root, content):
    file_name = fd.asksaveasfilename(initialfile = "export_chat.txt", defaultextension = ".txt", filetypes=(("Text file", ".txt"), ("All Files","*.*")), parent=root)
    if file_name:
        with open(file_name, "w", encoding = "utf-8") as exported:
            exported.write(content)

def usage_tips(MENU_FONT, MENU_FONT_BOLD):
    top_tips = Toplevel(padx = 5, pady = 5)
    top_tips.title("Usage Tips")
    top_tips.resizable(False, False)
    top_tips.grab_set()   # Grab focus to this window and prevent focus change to lower level windows
    top_tips.focus_force()    # Force focus over to this window

    # Label for title
    lbl_tips_title = Label(top_tips, font = MENU_FONT_BOLD, borderwidth=2, relief="ridge", justify = "center",
                            text = "Usage Tips")
    lbl_tips_title.grid(row = 0, column = 0, sticky = "we")

    # Text box with usage tips
    txt_tips = scrolledtext.ScrolledText(top_tips, font = MENU_FONT, width = 60, height = 23, wrap = "word", spacing3 = 5)
    txt_tips.tag_config("tag_about_header", font = MENU_FONT_BOLD, justify = "center")
    txt_tips.tag_config("tag_about_section", font = MENU_FONT_BOLD)
    txt_tips.insert(END, "Source of Text Generation type LLMs:", "tag_about_section")
    txt_tips.insert(END, "\nhttps://huggingface.co/models?pipeline_tag=text-generation&sort=trending&search=gguf")
    txt_tips.insert(END, "\n\n1) Read tooltips", "tag_about_section")
    txt_tips.insert(END, "\n- Almost all buttons and options have useful tooltips to guide you along.")
    txt_tips.insert(END, "\n\n2) Chat input keybinds", "tag_about_section")
    txt_tips.insert(END, "\n- [Enter] to send message."
                    +"\n- [Shift+Enter] to insert new lines."
                    +"\n- [Esc] to force-stop LLM's reply")
    txt_tips.insert(END, "\n\n3) Assign a personality to the LLM", "tag_about_section")
    txt_tips.insert(END, "\n- Setting a personality in the Config menu can help give more domain-specific replies. You can even use it to restrict its behaviours (to some extent)."
                    +"\n- Under the hood, this is done via 'System' prompt."
                    +"\n- If personality is not being applied to the LLM's replies, input personality in the first chat prompt at start of conversation. "
                    +"This is because the LLM/prompt template may not support 'System' prompts. Note: When using this workaround, personality may be lost "
                    +"as the conversation gets longer due to context management techniques.")
    txt_tips.insert(END, "\n\n4) Improve reply quality by setting Prompt Template", "tag_about_section")
    txt_tips.insert(END, "\n- If you are getting poor-quality replies from an LLM, try changing the Prompt Template option in Config menu from 'auto' to one that the LLM was trained with. "
                    +"Refer to the LLM's model card on HuggingFace website for the correct prompt template to set (e.g. 'alpaca', 'llama-2', etc.).")
    txt_tips.insert(END, "\n\n5) Create Config 'profiles' with Export/Import", "tag_about_section")
    txt_tips.insert(END, "\n- In the Config menu, the Export function lets you export your settings as an '.ini' file, which can later be imported with the Import function."
                    +"\n- This lets you easily create and use multiple 'profiles' which contain different LLM personalities, Custom Prompt Templates etc.")

    
    txt_tips.config(state = "disabled")
    txt_tips.grid(row = 1, column = 0, sticky = "nsew")
    
    # Set only column0 weight to 1 to adapt to horizontal window adjustments
    top_tips.columnconfigure(0, weight=1)

    # Set all row weights to 1 to adapt to vertical window adjustments
    total_rows = top_tips.grid_size()[1]
    for row in range(total_rows):
        top_tips.rowconfigure(row, weight=1)
        
    top_tips.protocol("WM_DELETE_WINDOW", top_tips.destroy)
    
def check_updates():
    webbrowser.open("https://github.com/rrrusst/solairia/releases")
    
def about_info(version, MENU_FONT, MENU_FONT_BOLD):
    top_about = Toplevel(padx = 5, pady = 5)
    top_about.title("About")
    top_about.resizable(False, False)
    top_about.grab_set()   # Grab focus to this window and prevent focus change to lower level windows
    top_about.focus_force()    # Force focus over to this window

    # Label for title
    lbl_about_title = Label(top_about, font = MENU_FONT_BOLD, borderwidth=2, relief="ridge", justify = "center",
                            text = "SOLAIRIA v"+version)
    lbl_about_title.grid(row = 0, column = 0, sticky = "we")

    # Text box with 'About' details 
    txt_about = Text(top_about, font = MENU_FONT, width = 60, height = 23, wrap = "word", spacing3 = 5)
    txt_about.tag_config("tag_about_header", font = MENU_FONT_BOLD, justify = "center")
    txt_about.tag_config("tag_about_section", font = MENU_FONT_BOLD)
    txt_about.insert(END, "SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance) was created by Russell Tan (GitHub: rrrust), 2024."
                     +"\n© 2024 Russell Tan. All rights reserved. "
                     +"\nUploaded on: https://github.com/rrrusst/solairia", "tag_about_header")
    txt_about.insert(END, "\n\nOverview:", "tag_about_section")
    txt_about.insert(END, "\n- Built with 'llama-cpp-python' package and PyInstaller. Only works on Windows OS."
                     +"\n- Runs completely offline on your own hardware. Designed to have no online functionality, apart from the manual 'Check for Updates' feature."
                     +"\n- Does not save or share your conversations. Your chat log can be manually exported if you wish."
                     +"\n- Supports Text Generation type of LLMs (in .gguf format) for chatting and text file analysis."
                     +"\n- Auto-selects the appropriate prompt template based on LLM's metadata."
                     +"\n- Supports manual prompt template setting if LLM produces poor/unusable replies (due to incompatibility with some LLM's metadata).")
    txt_about.insert(END, "\n\nSOLAIRIA comes in two variants:", "tag_about_section")
    txt_about.insert(END, "\n(1) GPU-bound: Generates replies fast (within seconds). Requires NVIDIA GPU released in 2006 or later + NVIDIA CUDA Toolkit installed."
                     +"\n(2) CPU-bound: Generates replies slow (>10-30x slower than GPU-bound). Does not require NVIDIA GPU or NVIDIA CUDA Toolkit.")

    txt_about.config(state = "disabled")
    #txt_about.bindtags((str(txt_about), str(top_about), "all"))    # Disables all binds in the textbox to prevent selection of any text
    txt_about.grid(row = 1, column = 0, sticky = "nsew")
    
    # Set only column0 weight to 1 to adapt to horizontal window adjustments
    top_about.columnconfigure(0, weight=1)

    # Set all row weights to 1 to adapt to vertical window adjustments
    total_rows = top_about.grid_size()[1]
    for row in range(total_rows):
        top_about.rowconfigure(row, weight=1)
        
    top_about.protocol("WM_DELETE_WINDOW", top_about.destroy)
