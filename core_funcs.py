# SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance)
# First written by Russ on 18 Jan 2024 (https://github.com/rrrusst/solairia).

# From built-in libraries
import datetime, time, traceback, math
import tkinter as tk
import threading
from tkinter import filedialog as fd, END
from threading import Thread

# From external libraries
import sentencepiece
from llama_cpp import Llama

# From custom modules
from config_handler import ConfigHandler
import gui

class LlmProcess:
    lock = threading.Lock()
    is_running = []
    thread_list = []    # List to store 'Send' threads, so they can be joined later if a new 'Send' thread needs to be created.
    llm = None
    llm_status = "Idle"

def load_model(llm_path, ct_size, prompt_template):    
    if LlmProcess.is_running == False:
        if llm_path.endswith(".gguf"):
            if prompt_template == "auto":
                prompt_template = None
            try:
                print("Now loading the LLM model...")
                # LOAD THE MODEL
                # n_gpu_layers = -1 to offload all layers to GPU
                # offload_kqv = True to offload kqv to GPU. Else, output will be rubbish when on CUBLAS/GPU
                
                with LlmProcess.lock:
                    LlmProcess.llm = Llama(model_path = llm_path, n_ctx = int(ct_size),
                            n_gpu_layers = -1, offload_kqv = True, chat_format = prompt_template, kv_overrides = {"add_bos_token":False})
                gui.lbl_llm_name_var.set("LLM Loaded: "+LlmProcess.llm.metadata["general.name"])
                return True
            except ValueError:
                tk.messagebox.showinfo("Error",  "Please set a valid LLM file, or check that your file path is correct.")
                return False
            except:
                traceback.print_exc()
                tk.messagebox.showinfo("Error",  "Unable to load the LLM file. Please try another.")
                return False
        elif len(llm_path) == 0 or llm_path.isspace():
            with LlmProcess.lock:
                LlmProcess.llm = None
            gui.lbl_llm_name_var.set("LLM Loaded: None")
            return True
        else:
            tk.messagebox.showinfo("Error",  "Please load a valid LLM file (.gguf format).")
            return False
    else:
        tk.messagebox.showinfo("Error",  "You are trying to load another LLM file while SOLAIRIA is replying. "
                               +"Please wait for SOLAIRIA to finish before trying again.")
        return False

def set_personality():
    personality = ConfigHandler.cp["AI"]["personality"]
    if len(personality) <= gui.root.personality_limit:
        if len(personality) != 0:
            gui.root.default_sys_prompt = personality
        else:
            gui.root.default_sys_prompt = "You are an AI Assistant."
    else:
        str_error = "Your input for Personality was "+str(len(personality))+" characters long. Please keep within "+str(gui.root.personality_limit)+" characters. This limit depends on Context Size"
        tk.messagebox.showinfo("Error",  str_error)
        gui.open_config()

def send(msg):
    with LlmProcess.lock:
        LlmProcess.is_running = True
    my_prompt = msg
    final_result = ""
    context_size_limit = 0
    max_token_limit = 0
    context_size = int(ConfigHandler.cp["AI"]["context_size"])
    prev_prompts = "\n".join([item["content"] for item in gui.root.msglist])
    match(ConfigHandler.cp["AI"]["context_mgmt"]):
        case "sliding_window":  # Truncate prev_prompts in a "sliding window" manner
            context_size_limit = context_size
            max_token_limit = 0
            
            while count_tokens(prev_prompts) >= context_size_limit*0.7: # Truncate prev_prompts when it's more than 70% of context_size_limit
                del gui.root.msglist[0] # Delete oldest/first item in gui.root.msglist
                prev_prompts = "\n".join([item["content"] for item in gui.root.msglist])                
        case "periodic_summary":    # Set limits to facilitate "periodic summary" later
            context_size_limit = int(context_size*0.5)  # Equivalent to 0.5 OF context_size
            max_token_limit = context_size//4    # Equivalent to 0.25 of whole context_size

    # Check if previous_prompts is less than context_size_limit
    if count_tokens(prev_prompts) < context_size_limit:
        gui.txt_user.delete("1.0", "end")
        gui.lbl_input_counter.config(text = "Total characters: 0")

        match(my_prompt):
            case "/r":  # Resets prev_prompts (context memory) to blank
                gui.reset_memory()
                return
            case "/clear":  # Clears chat window
                gui.clear_chat()
                return
            case "/f":  # Analyse text file
                analyse_text_file()
                return
            case _: # Do this if user input is not any of the above '/' commands
                if gui.chat_box.compare("end-1c", "!=", "1.0"):
                    # Insert new line 'separator' if textbox is not empty (i.e. conversation is ongoing)
                    gui.chat_box.insert(END, "\n")
                gui.chat_box.insert(END, "User -> " + my_prompt, "tag_user")
                gui.chat_box.see("end")
                
        gui.root.msglist.append({"role": "user", "content": my_prompt})  # Add my_prompt to gui.root.msglist
        
        # Generate response to user's input, with chat history as prior context.
        # Use llama-cpp-python's auto-detected preset prompt templates for generation
        llm_response = generate_text_from_prompt([{"role": "system", "content": gui.root.default_sys_prompt}] + gui.root.msglist, max_tokens = max_token_limit)
        
        with LlmProcess.lock:
            LlmProcess.llm_status = "Thinking"
        gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
        gui.chat_box.insert(END, "\nAsst -> ", "tag_asst")
        gui.chat_box.see("end")
        gui.root.msglist.append({"role": "assistant", "content": ""})   # Add an empty assistant response. Content will be updated later.
        
        # Stream and print the AI's output
        try:
            for item in llm_response:
                if LlmProcess.is_running == False:
                    if ConfigHandler.cp["AI"]["history_option"] == "on":
                        gui.root.msglist[-1]["content"] = final_result  # Update "content" of last item (which corresponds to assistant's response added earlier)
                    else:
                        gui.root.msglist = []   # Clear gui.root.msglist if history_option is disabled
                    #raise KeyboardInterrupt
                    return
                else:
                    if not LlmProcess.llm_status.startswith("Replying"):
                        with LlmProcess.lock:
                            LlmProcess.llm_status = "Replying (press [Esc] to stop)"
                        gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
                    response_content = ""
                    try:
                        response_content = item['choices'][0]['delta']['content']
                        if gui.root.winfo_exists():
                            gui.chat_box.insert(END, response_content, "tag_asst")
                            gui.chat_box.see("end")                    
                    except KeyError:
                        # Because (1) first and last key's of the ['delta'] dict is not 'content', and (2) 'content' key only appears on second for... interation, this exception is needed
                        pass
                    except tk.TclError as ex:
                        if str(ex) == "can't invoke \"winfo\" command: application has been destroyed":
                            pass
                        else:
                            traceback.print_exc()
                    except:
                        traceback.print_exc()
                    final_result += response_content
        except KeyboardInterrupt:
            # This is needed to catch KeyboardInterrupt in Windows CMD
            print("\n\nYou interrupted the response.")
            return
        except ValueError:
            gui.chat_box.insert(END, "\n---Context/memory exceeded. Wiping context/memory. SOLAIRIA will not be able to reference earlier parts of the conversation.---", "tag_info")
            gui.chat_box.see("end")
            gui.root.msglist = []
            with LlmProcess.lock:
                LlmProcess.llm_status = "Idle"
            gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
            return
        except:
            traceback.print_exc()
        
        with LlmProcess.lock:    
            LlmProcess.llm_status = "Idle"
        gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)

        if ConfigHandler.cp["AI"]["history_option"] == "on":
            gui.root.msglist[-1]["content"] = final_result  # Update "content" of last item (which corresponds to assistant's response added earlier)
        else:
            gui.root.msglist = []   # Clear gui.root.msglist if history_option is disabled
                
    # CHECK IF PREVIOUS PROMPTS IS 1/2 OF CONTEXT SIZE (which increases possibility of next user prompt exceeding limit)
    ####final_result = (llm_response['choices'][0]['message']['content'])  #this response format is for non-streaming output.
    elif ConfigHandler.cp["AI"]["context_mgmt"] == "periodic_summary" and count_tokens(prev_prompts) >= context_size_limit :
        gui.chat_box.insert(END, "\n---Context/memory limit reached. Compressing context/memory...---", "tag_info")
        gui.chat_box.see("end")

        # Duration is based on desktop test rig benchmark. Desktop test rig specs can be found on SOLAIRIA's GitHub page.
        # With 1024 context size, duration is ~60-300secs on CPU, and ~3-5secs on GPU.
        duration_cpu_min = round(60 * (context_size/1024))
        duration_cpu_max = round(300 * (context_size/1024))
        duration_gpu_min = round(3 * (context_size/1024))
        duration_gpu_max = round(5 * (context_size/1024))

        gui.chat_box.insert(END,
                            f"\nThis may take around {duration_cpu_min}-{duration_cpu_max}secs (CPU version)/{duration_gpu_min}-{duration_gpu_max}secs (CUDA GPU version) for {context_size} tokens context size. Please hold on...",
                            "tag_info")
        gui.chat_box.see("end")

        final_summary = ""

        # Generate internal summary of conversation
        gui.root.msglist.append({"role": "user", "content": "Summarise our conversation using less than "+str(gui.root.context_char_limit//4)
                    +" characters.Use short paragraph style."})
        # Use llama-cpp-python's auto-detected preset prompt templates for generation
        llm_summary = generate_text_from_prompt([{"role": "system", "content": "You're a text summariser.Don't reveal your role.You never forget my name and the name I call you."}]
                                                 + gui.root.msglist, max_tokens = context_size - count_tokens(prev_prompts), temperature = 0.2)    # Set a lower temperature for more standardised and less creative replies
        with LlmProcess.lock:
            LlmProcess.llm_status = "Compressing memory"
        gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
        # Stream the AI's output as an internal summary
        try:
            for item in llm_summary:
                if LlmProcess.is_running == False:
                    gui.chat_box.insert(END, "\n---Context/memory compression interrupted. SOLAIRIA may not be able to reference some parts of the earlier conversation.---", "tag_info")
                    gui.chat_box.see("end")
                    return
                else:
                    response_content = ""
                    try:
                        response_content = item['choices'][0]['delta']['content']
                    except KeyError:
                        # Because (1) first and last key's of the ['delta'] dict is not 'content', and (2) 'content' key only appears on second for... interation, this exception is needed
                        pass
                    except:
                        traceback.print_exc()
                    final_summary += response_content
        except ValueError:
            gui.chat_box.insert(END, "\n---Context/memory exceeded. Wiping context/memory. SOLAIRIA will not be able to reference earlier parts of the conversation.---", "tag_info")
            gui.chat_box.see("end")
            gui.root.msglist = []
            with LlmProcess.lock:
                LlmProcess.llm_status = "Idle"
            gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
            return
        except:
            traceback.print_exc()
            
        if(count_tokens(final_summary)<5 or final_summary.isspace() or len(final_summary)==0):
            gui.chat_box.insert(END, "\n" + "---Failed context/memory compression (could be due to LLM getting confused with the preset/custom prompt template). "
                            +"SOLAIRIA will not be able to reference earlier parts of the conversation.---.", "tag_info")
            gui.chat_box.see("end")
            with LlmProcess.lock:
                LlmProcess.llm_status = "Idle"
            gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
        else:
            gui.chat_box.insert(END, "\n---Completed context/memory compression. Some details of the earlier conversation may be lost due to compression.---", "tag_info")
            gui.chat_box.see("end")
            with LlmProcess.lock:
                LlmProcess.llm_status = "Idle"
            gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)

        if ConfigHandler.cp["AI"]["history_option"] == "on":
            gui.root.msglist = [{"role": "assistant", "content": final_summary}]
        else:
            gui.root.msglist = []
    with LlmProcess.lock:        
        LlmProcess.is_running = False
    
# Thread for send() function
def thread_send(msg):
    with LlmProcess.lock:
        LlmProcess.is_running = False  # Set to False to stop LLM from responding while inside its For... loop.
    
        for t in LlmProcess.thread_list:
            t.join()    # Wait for 'Send' thread to finish its tasks before joining the thread.
        else:
            LlmProcess.thread_list.clear() # Clear thread_list once all threads have joined.

        t1 = Thread(target = send, args = (msg,))   # Create thread that runs send(), and pass the argument list containing 'msg' to send().
        t1.start()  # Start the thread.
        LlmProcess.thread_list.append(t1)  # Append the new 'Send' thread into thread_list.
        
def evt_send(event, msg):   
    if LlmProcess.llm is not None:
        match(LlmProcess.llm_status):
            case "Thinking":
                gui.chat_box.insert(END, "\n---Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.---\n", "tag_info")
                gui.chat_box.see("end")
                return "break"  # Need this to prevent default "Enter" key new line behaviour in text box
            case "Reading file":
                gui.chat_box.insert(END, "\n---Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.---\n", "tag_info")
                gui.chat_box.see("end")
                return "break"  # Need this to prevent default "Enter" key new line behaviour in text box
            case "Compressing memory":
                gui.chat_box.insert(END, "\n---Please wait till SOLAIRIA is done with the '"+LlmProcess.llm_status+"' phase.---\n", "tag_info")
                gui.chat_box.see("end")                
                return "break"  # Need this to prevent default "Enter" key new line behaviour in text box
            case _:
                if len(msg) == 0 or msg.isspace():
                    if LlmProcess.is_running == False:
                        if gui.chat_box.compare("end-1c", "!=", "1.0"):
                            # Insert new line if textbox is not empty (i.e. not empty due to conversation ongoing)
                            gui.chat_box.insert(END, "\n")
                        gui.chat_box.insert(END, "User -> " + msg, "tag_user")
                        gui.chat_box.see("end")
                elif len(msg) > gui.root.my_prompt_limit:
                    tk.messagebox.showinfo("Error", "Your input was "+str(len(msg))+" characters long. Please keep within "+str(gui.root.my_prompt_limit)+" characters.")
                else:
                    thread_send(msg)
                return "break"  # Need this to prevent default "Enter" key new line behaviour in text box
    else:
        tk.messagebox.showinfo("No LLM (.gguf) file loaded yet!",  "Please load an LLM file (.gguf format) first."
                               +"\n\nRefer to the Help menu to find out where to download LLM files (.gguf format).")
        gui.open_config()
        return "break"  # Need this to prevent default "Enter" key new line behaviour in text box
    
def generate_text_from_prompt(user_prompt,
                              max_tokens = 0, # Initialise to 0 (equivalent to max_tokens of up to n_ctx parameter of LLM). Specific max_tokens will be set at each call of the function.
                              temperature = 0.5,    # Initially was 0.3. Higher = more creative.
                              repeat_penalty=1.17,
                              top_p = 0.5,  # Initially was 0.1. Higher = wider range of response but may be less accurate in answers.
                              stream = True,    # Enables streaming of output
                              mirostat_mode = 2,
                              stop = ["<user>", "</user>", "<|user", "<<USER>>", "[/INST]", "<history>", "</history>"] # stopwords to prevent LLM from talking to itself
                              ):
    # Define the parameters
    model_output = LlmProcess.llm.create_chat_completion(
        user_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        repeat_penalty=repeat_penalty,
        top_p=top_p,
        stream=stream,
        mirostat_mode=mirostat_mode,
        stop=stop
        )
    return model_output

def count_tokens(text):
    # Using Llama tokenizer.model from https://huggingface.co/hf-internal-testing/llama-tokenizer/blob/main/tokenizer.model , dated 30 Mar 2023
    sp = sentencepiece.SentencePieceProcessor(model_file = ConfigHandler.dirname+"/tokenizer/tokenizer.model")
    prompt_tokens = sp.encode_as_ids(text)
    return len(prompt_tokens)

# Halves a String and splits it based on the newline, period or exclamation mark before the String's midpoint to capture the entire sentence/line.
def text_halver(text):
    split_chunks = ()
    midpoint = len(text)//2
    before_mid = max(text[:midpoint].find("\n"), text[:midpoint].find(". "), text[:midpoint].find("! "))
    if before_mid != -1:
        split_chunks = text[:before_mid+1], text[before_mid+1:]
    else:
        split_chunks = text[:midpoint], text[midpoint:]
    return split_chunks

def file_text_chunker(path):
    # Formula for file token limit
    context_size = int(ConfigHandler.cp["AI"]["context_size"])
    file_token_limit = context_size * 0.65  # Set limit to 0.65 of context_size
    chunk = ""
    chunk_list = []
    start_index = 1
    last_index = 1
    with LlmProcess.lock:
        LlmProcess.llm_status = "Reading file"
    gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
        
    # This With.. loop may have issues with some lines in UTF-16 text/log files.
    with open(path) as file:
        for index, line in enumerate(file, start = 1):
            chunk += line
            if count_tokens(chunk) < context_size:
                if count_tokens(chunk) >= file_token_limit:
                    chunk_list.append(["Ln "+str(start_index)+"-"+str(index), chunk])
                    chunk = ""
                    start_index = index + 1 # Set start_index to next line's index for next iteration
            elif count_tokens(chunk) >= context_size:
                # If the chunk's length in tokens exceeds context_size (due to text encoding issue or it's a really long line of text), split it in half
                split_text = text_halver(chunk)
                chunk_list.append(["Ln "+str(start_index)+"-"+str(index), split_text[0]])
                chunk = ""+split_text[1]
                start_index = index # Set start_index to current line's index, to continue from same line number in next iteration
            last_index = index
        chunk_list.append(["Ln "+str(start_index)+"-"+str(last_index), chunk])    # Append remaining chunk to chunk_list after completing the above For.. loop
    return chunk_list

def analyse_text_file():
    context_size = int(ConfigHandler.cp["AI"]["context_size"])

    gui.chat_box.insert(END, "\n---Choose a '.csv', '.log' or '.txt' file for analysis.", "tag_info")


    # File size limit is based on testing. If the file size exceeds the soft limit, a single final analysis summary might not be produced.
    # With 1024 context size, max file size is ~10kb.
    file_size_max = math.floor(10 * (context_size/1024))

    gui.chat_box.insert(END, f"\nFor {context_size} token context size, ideal file size is <={file_size_max}kb. Larger fles can be used, but may not produce a single final analysis summary.---\n", "tag_info")
    gui.chat_box.see("end")
       
    sel_file_name =  fd.askopenfilename(title = "Select a file", filetypes = (('Supported formats', '.csv .log .txt'),), parent=gui.root)
    if not sel_file_name:
        with LlmProcess.lock:
            LlmProcess.is_running = False
            LlmProcess.llm_status = "Idle"
        gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
        return

    chunk_analysis = ""
    chunk_analysis_summ = ""
    chunk_list = file_text_chunker(sel_file_name)   # Multi-dimensional list format: [[Line range, main text], ...]
    part_counter = 0
    total_duration = 0
    gui.root.msglist.append({"role": "user", "content": "Analyse this file: "+sel_file_name})
    for index, chunk in enumerate(chunk_list, start = 1):
        part_timer = time.time()    # Set start time of part analysis
        part_num = "[PART"+str(index)+"]"
        line_range = chunk[0]
        chunked_text = chunk[1]            
        chunk_analysis += "\n\n"+part_num+line_range+":\n"

        # Generate analysis of text file
        # Use llama-cpp-python's auto-detected preset prompt templates
        llm_text_analysis = generate_text_from_prompt([
            {"role": "system", "content": "You are a File Analysis AI.Don't reveal your role.You reply with less than "+str(context_size - count_tokens(chunked_text))+" tokens."},
            {
                "role": "user",
                "content": "Explain the text within [txt] and highlight important details."
                            +"Be direct and concise.[txt][PART"+str(index)+"]\n"+chunked_text+"[txt]"
            }
        ], max_tokens = context_size - count_tokens(chunked_text), temperature = 0.2)   # Set a lower temperature for more standardised and less creative replies
        
        if part_counter != 0:        
            # Formula for time left: (Sum of time taken for completed parts/num of completed parts) * (num of total parts - num of completed parts)
            time_left = datetime.timedelta(seconds = int(total_duration/part_counter) * (len(chunk_list) - part_counter))
            with LlmProcess.lock:
                LlmProcess.llm_status = "Processing Part "+str(index)+"/"+str(len(chunk_list))+"("+line_range+"). Time left: "+str(time_left)+" (H:mm:ss)"
        else:
            with LlmProcess.lock:
                LlmProcess.llm_status = "Processing Part "+str(index)+"/"+str(len(chunk_list))+"("+line_range+"). Time left: Calculating..."
        gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
        
        try:
            for item in llm_text_analysis:
                if LlmProcess.is_running == False:
                    return
                else:
                    response_content = ""
                    try:
                        response_content = item['choices'][0]['delta']['content']
                    except KeyError:
                        # Because (1) first and last key's of the ['delta'] dict is not 'content', and (2) 'content' key only appears on second for... interation, this exception is needed
                        pass
                    except:
                        traceback.print_exc()
                    chunk_analysis += response_content
        except KeyboardInterrupt:
            # This is needed to catch KeyboardInterrupt in Windows CMD
            print("\n\nYou interrupted the response.")
            break
        except:
            traceback.print_exc()

        part_counter += 1   # Increase count by 1 when analysis of current part is complete
        part_timer = time.time() - part_timer # Get time difference between start and end time of part analysis
        total_duration += part_timer
        
    gui.chat_box.insert(END, "\nAsst -> ", "tag_asst")
    chunk_analysis = chunk_analysis.strip()
    with LlmProcess.lock:
        LlmProcess.llm_status = "Replying (press [Esc] to stop)"
    gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
    gui.chat_box.insert(END, "\n==Analysis of Parts==\n" + chunk_analysis, "tag_asst")
    gui.chat_box.see("end")

    # Summarise all the chunks together if more than 1 chunk
    if len(chunk_list) > 1:
        if count_tokens(chunk_analysis) < context_size:            
            # Generate summary of analysis parts
            # Use llama-cpp-python's auto-detected preset prompt templates
            llm_text_analysis_summ = generate_text_from_prompt([
                {"role": "system", "content": "You are a File Analysis AI.Don't reveal your role.You reply with less than "+str(context_size - count_tokens(chunk_analysis))+" tokens."},
                {
                    "role": "user",
                    "content": "Summarise the analysis within [txt].Be direct and concise.[txt]"+chunk_analysis+"[txt]"
                }
            ], max_tokens = context_size - count_tokens(chunk_analysis), temperature = 0.2)   # Set a lower temperature for more standardised and less creative replies

            with LlmProcess.lock:
                LlmProcess.llm_status = "Thinking"
            gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
            try:
                for item in llm_text_analysis_summ:
                    if LlmProcess.is_running == False:
                        return
                    else:
                        response_content = ""
                        try:
                            response_content = item['choices'][0]['delta']['content']
                        except KeyError:
                            # Because (1) first and last key's of the ['delta'] dict is not 'content', and (2) 'content' key only appears on second for... interation, catchthis exception is needed
                            pass
                        except:
                            traceback.print_exc()
                        chunk_analysis_summ += response_content
            except ValueError:
                gui.chat_box.insert(END, "\n---Analysis Summary not available (the merged Analysis of Parts was too long). Refer to the individual Analysis of Parts above instead.---", "tag_info")
                gui.chat_box.see("end")
            except:
                traceback.print_exc()

            with LlmProcess.lock:
                LlmProcess.llm_status = "Replying (press [Esc] to stop)"
            gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
            gui.chat_box.insert(END, "\n\n==Analysis Summary==\n"+chunk_analysis_summ, "tag_asst")
            gui.chat_box.see("end")
        else:
            chunk_analysis_summ = "I analysed the file but can't give an Analysis Summary as the text in file was too long."
            gui.chat_box.insert(END, "\n---Analysis Summary not available (ran out of context memory when trying to summarise Analysis of Parts). Refer to the individual Analysis of Parts above instead.---", "tag_info")
            gui.chat_box.see("end")
    else:
        with LlmProcess.lock:
            LlmProcess.llm_status = "Replying (press [Esc] to stop)"
        gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
        gui.chat_box.insert(END, "\n\n==Analysis Summary==\n"+chunk_analysis, "tag_asst")
        gui.chat_box.see("end")
        chunk_analysis_summ = chunk_analysis
    if ConfigHandler.cp["AI"]["history_option"] == "on":
        gui.root.msglist.append({"role": "assistant", "content": chunk_analysis_summ})
    else:
        gui.root.msglist = []
    
    with LlmProcess.lock:
        LlmProcess.llm_status = "Idle"
    gui.lbl_status_var.set("SOLARIA is: "+LlmProcess.llm_status)
    with LlmProcess.lock:
        LlmProcess.is_running = False
  