# SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance)
## A program built on top of the 'llama-cpp-python' package and works completely offline.
### Update 17 Jun 2024: Version 2.0.0 is on the way, with a full-fledged GUI, some interface customisation options, user experience improvements, performance optimisations and bug fixes.

### GENERAL INFO:
1) It loads the '.gguf' LLM model that you place in its \model\ folder to let you perform text-based interaction with the AI model.
2) Only '.gguf' model format is supported.
3) It has been preset to use Llama2's prompt format (https://huggingface.co/blog/llama2#how-to-prompt-llama-2) and tested with TheBloke's Llama-2-7B-Chat-GGUF model (https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF).
4) Your results may vary when using other '.gguf' models. Non-Llama '.gguf' models may give strange replies as they were tuned using a different prompt format.
5) SOLAIRIA is packaged into an '.exe' with supporting folders and files using PyInstaller, which are then zipped into a neat .zip file for ease of installation and use.<br>
---NOTE: **The '.exe' may be flagged as malicious by some anti-malware scanners. This is a false positive**. The detection is because malicious actors use PyInstaller (and similar programs) to package their malware, and when these packaged malware are detected by anti-malware scanners, the file behaviour and characteristics are recorded into their database. Because '.exe' files created using PyInstaller share similar characteristics, even innocent programs are falsely flagged by some anti-malware scanners.
6) Currently only supports Windows.
7) **This repository does not contain the Python source code. Only released versions and the [VirusTotal](https://www.virustotal.com) file analysis PDF are uploaded in "Releases".**

### HOW TO USE:
1) Download the CPU or GPU-bound version's .zip file (from "Releases" at right side of this page) and extract the contents to your desired folder
2) (For GPU-bound version only) Download and install NVIDIA CUDA Toolkit from [https://developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads). You only need to install the CUDA-related components.
3) Get a text-generation type of '.gguf' LLM model from [https://huggingface.co/models?pipeline_tag=text-generation&sort=trending&search=gguf](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending&search=gguf).
4) Place the '.gguf' model into the program's \model\ folder
5) Run the .exe file
---You may need to unblock the file via right-click -> properties -> properties, as it is an '.exe' that does not originate from your computer.
---Your anti-malware software might detect it as malicious. This is a false positive, as stated in the note in GENERAL INFO #5 above. The file analysis PDF by [VirusTotal](https://www.virustotal.com) is uploaded in each Release for your reference and peace of mind.

### WHAT YOU CAN DO WITH SOLAIRIA:
1) You can use it **completely offline** after downloading the .zip and obtaining your desired '.gguf' LLM model. No need to worry about your conversations in the program being eavesdropped on.
2) You can set its context size after starting up the program (1024, 2048-default or 4096). This governs how much context memory SOLAIRIA has to remember your conversation, and also affects your input length limit. Larger size = More chat history for it to refer to before replying = Slower replies as more tokens need to be processed.
3) You can give it a personality so that it responds in the style of that personality.
4) You can use it as your personal Q & A bot, a source of ideas and inspiration, a storyteller, a speechwriter, a temporary virtual confidante etc.
5) You can use it to analyse text files (.csv, .log and .txt) and get insights on their contents.
6) You can easily remove SOLAIRIA from your computer by deleting the folders and files that you initially extracted from the .zip file (yup, that easy).

### WHAT YOU CANNOT DO WITH SOLARIA:
1) You cannot use non-text-generation type of LLM models as the program does not handle those right now.
2) You cannot save and load your chat session in the program. Once you close it, your conversation is gone. Re-launching will start from a blank slate again.
3) It cannot access the Internet to get info. All info it provides is based on the LLM loaded and the date it was trained (e.g. Llama 2 has a knowledge cutoff date of Dec 2022. It will not be able to give info on anything after Dec 2022).
4) You cannot input multi-lines of text and have it processed as a whole due to Windows Command Prompt limitation (each line will be treated as a separate input by you. i.e. SOLAIRIA will process and reply your first line, then the 2nd, then 3rd etc... instead of processing and replying it as a whole). WORKAROUND: Save the multi-line text in a .txt file and ask SOLAIRIA to analyse it.

### SOLAIRIA uses the following packages (including their dependencies, which are not listed here):
1) [llama-cpp-python - Python bindings for llama.cpp](https://github.com/abetlen/llama-cpp-python) - For use of llama.cpp in Python to run LLMs
2) [Colorama](https://github.com/tartley/colorama) - For coloured text in Windows Command Prompt
3) [SentencePiece](https://github.com/google/sentencepiece) - For conversion of text to tokens to estimate token count
4) [PyInstaller](https://github.com/pyinstaller/pyinstaller) - For packaging of SOLAIRIA's Python code and dependencies into a single executable file

### TEST RIG SPECS:
1) OS: Windows 10 Pro (version 22H2)
2) Motherboard: Gigabyte Z390 Gaming X
3) CPU: Intel i5-9600K (6 cores @ 4.9GHz)
4) RAM: 16GB
5) GPU (not used for processing in CPU-bound version): NVIDIA RTX 3070 (8GB VRAM)
