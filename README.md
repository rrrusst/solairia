# SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance)
## Load and interact with text-generation LLMs easily and privately using your computer's own hardware. Built with 'llama-cpp-python'.

#### Known Issues:
  - 6 Nov 2024: Ctrl+A (select all) and Ctrl+C (copy) key combination temporarily disabled in main chat window. Working to re-enable it in the next update. CPU-bound version hangs sometimes if user prompts rapidly during LLM's replies.

#### Updates (latest 3):
  - 5 Nov 2024: Version 2.0.1 has been released! Compatibility with different text-generation LLMs (.gguf format) has been improved with the reworked custom prompt template feature (now uses llama-cpp-python's preset prompt templates and auto-selection, with the option to manually select from a list of preset templates).
  - 26 Jun 2024: Version 2.0.0 has been released! Enjoy a full-fledged GUI, some interface customisation options, user experience improvements, performance optimisations and bug fixes.
  - 22 Jul 2024: Readme has been updated for Version 2.0.0.

### OVERVIEW:
1) SOLAIRIA is an **offline, private and customisable** alternative to ChatGPT (and other similar products) that supports text interactions and **runs 100% on your computer's own hardware**.
2) It lets you load a text-generation LLM of your choice (in .gguf format only) and interact with it, all without needing any internet connection. You will need to download a text-generation type of LLM from the HuggingFace website before loading it into SOLAIRIA.
3) Currently only supports Windows OS.
4) Available in two variants:
    1) GPU-bound: Uses your computer's NVIDIA GPU for LLM inference/processing. Performs >10-20x faster than CPU-bound version. Requires CUDA components from [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) to be installed before use and supports NVIDIA GPUs released in 2006 or later/newer.
    2) CPU-bound: Uses your computer's CPU for LLM inference/processing. Performs slower than GPU-bound version. Does not require any additional components to be installed and widely compatible with Windows systems.
5) **This repository does not contain the Python source code. Only released versions and the [VirusTotal](https://www.virustotal.com) file analysis PDF are uploaded in [Releases](https://github.com/rrrusst/solairia/releases).**
   
![image](https://github.com/user-attachments/assets/cea7d16b-ce1f-489d-9d7a-51e2a28df920)

### GENERAL INFO:
1) As of v2.0.1, SOLAIRIA auto-selects the correct prompt template from a list of presets to use with your LLM based on the LLM's metadata.
2) An LLM you can start off with is [TheBloke's Llama-2-7B-Chat-GGUF model](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF).
3) If SOLAIRIA produces weird replies with a specific LLM, it is possible that the LLM's metadata (or lack of) does not contain enough info for SOLAIRIA to auto-select the correct template. In that case, just manually select from a list of preset prompt templates based on the LLM's model card on HuggingFace (e.g. 'alpaca', 'llama-2' etc.).
4) SOLAIRIA is packaged into an '.exe' with supporting folders and files using [PyInstaller](https://github.com/pyinstaller/pyinstaller), which are then compressed into .zip file for ease of installation and use.
    1) **The '.exe' may be flagged as malicious by some anti-malware scanners. This is a false positive**. The detection is because apart from legitimate developers, PyInstaller (and similar programs) is also used by malicious actors to package and hide their malware, and when these packaged malware are detected by anti-malware scanners, the file behaviour and characteristics are recorded into their database. Since '.exe' files created using PyInstaller share similar characteristics, even innocent programs can be falsely flagged by some anti-malware scanners.
    2) Each realease of SOLAIRIA is accompanied with a scan report from [VirusTotal](https://www.virustotal.com/) for transparency and peace of mind.

### HOW TO USE:
1) Download the CPU or GPU-bound version's .zip file (from [Releases](https://github.com/rrrusst/solairia/releases) at the right side of this page) and extract the contents to your desired folder.
2) (For GPU-bound version only) Download and install the [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads). You only need to install the CUDA-related components.
3) Download a text-generation type LLM model ('.gguf' format only) from [HuggingFace - an online hub for Machine Learning and Data Science](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending&search=gguf).
    1) Use an LLM that best matches your hardware specs. Popular LLMs such as [TheBloke's Llama-2-7B-Chat-GGUF model](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF) state their system requirements on their HuggingFace model card. If you use an LLM that exceeds the required specs (e.g. loading an LLM that uses 12GB RAM into a NVIDIA GPU that only has 8GB VRAM), it may not load successfully.
5) Run the 'main.exe' file located inside the earlier-extracted SOLAIRIA folder (before v2.0.0, the '.exe' was named along the lines of 'SOLAIRIA 1.02 (GPU-bound).exe').
    1) You may need to unblock the '.exe' file by right-clicking on it -> Properties -> Unblock, as it is an '.exe' that does not originate from your computer.
    2) Some anti-malware software may detect it as malware. However, **this is a false positive**, as stated in GENERAL INFO #4 above. The file analysis PDF by [VirusTotal](https://www.virustotal.com) is uploaded with each Release for your reference. You can upload the '.exe' yourself to [VirusTotal](https://www.virustotal.com) if you wish to perform your own scan.
6) Click on the 'Config' button in SOLAIRIA's GUI and point the 'LLM Path' to your downloaded '.gguf' LLM. You can also adjust various other settings in the 'Config' panel, such as:
    1) LLM's context size, personality, context management method and chat history reference.
    2) GUI font type, size and colour
5) Helpful tooltips can be viewed by hovering over most options/buttons in SOLAIRIA. Additionaly, usage tips can be found inside SOLAIRIA's menu via Help > Usage Tips

### WHAT YOU CAN DO WITH SOLAIRIA:
1) You can use it **completely offline** after downloading your desired text-generation '.gguf' LLM model from [HuggingFace - an online hub for Machine Learning and Data Science](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending&search=gguf). No need to worry about your conversations in the program being eavesdropped on.
    1) There are no plans to incorporate LLM downloading features into SOLAIRIA as it goes against the 'compeletely offline' design philosphy of SOLAIRIA.
2) You can use it to introduce beginners to the world of text-generation LLMs, or to refine your prompt engineering skills on different LLMs.
3) You can give it a personality so that it responds in the style of that personality, or give it rules to govern its responses.
4) You can use it as your personal and private Q & A companion, a source of ideas and inspiration, a storyteller, a speechwriter, a temporary virtual confidante and more.
5) You can export/import config settings, which can be used as config 'profiles' for different LLMs (e.g. set a specific personality and context size for a specific LLM)
6) You can export your chat log in '.txt' format from SOLAIRIA's menu via File > Export chat log.
7) You can use it to analyse text files (.csv, .log and .txt) and get insights on their contents.
    1) Best used with GPU-bound version for much faster analysis time.
8) You can easily remove SOLAIRIA from your computer by deleting the folders and files that you extracted from the SOLAIRIA '.zip' file (yup, that easy).

### WHAT YOU CANNOT DO WITH SOLAIRIA:
1) You cannot use non-text-generation type of LLM models as the program cannot handle those right now.
    1) This may change in future updates, as support for multi-modal LLMs (e.g. LLaVa) is being looked into.
2) You cannot save and load your chat session. Once you close SOLAIRIA, your conversation is gone. Re-launching will start the conversation from a blank slate.
3) It cannot access the Internet to get info. All info it provides is based on the LLM loaded and the date it was trained with (e.g. Llama 2 has a knowledge cutoff date of Dec 2022 and hence, it will not be able to give info on anything that transpired after Dec 2022).

### SOLAIRIA uses the following packages (including their dependencies, which are not listed here):
1) [llama-cpp-python - Python bindings for llama.cpp](https://github.com/abetlen/llama-cpp-python) - For use of llama.cpp in Python to run LLMs.
2) [SentencePiece](https://github.com/google/sentencepiece) - For conversion of text to tokens to estimate token count.
3) [PyInstaller](https://github.com/pyinstaller/pyinstaller) - For packaging of SOLAIRIA's Python code and dependencies into a single executable file.

### TEST RIG SPECS:
1) OS: Windows 10 Pro (version 22H2)
2) Motherboard: ASUS Z790-F
3) CPU: Intel i5-14600K (6 P-cores @ 3.5GHz)
    1) Only used for processing in CPU-bound version
4) RAM: 32GB DDR5
5) GPU: NVIDIA RTX 3070 (8GB VRAM)
    1) Only used for processing in GPU-bound version
