SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance) is a program built on top of the 'llama-cpp-python' package and works completely offline. It loads the '.gguf' LLM model that you place in its \model\ folder to let you perform text-based interaction with the AI model.

-Only '.gguf' model format is supported.
-It has been preset to use Llama2's prompt format (https://huggingface.co/blog/llama2#how-to-prompt-llama-2) and tested with TheBloke's Llama-2-7B-Chat-GGUF model (https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF).
-Your results may vary when using other '.gguf' models. Non-Llama '.gguf' models may give strange replies as they were tuned using a different prompt format.
-The necessary folder structure and files have been zipped into a neat .zip file for ease of installation and use.
-Currently only supports Windows.

HOW TO USE:
1) Download the .zip file and extract the contents to your desired folder (**as always, perform anti-malware scans on files you obtain from the Internet, even from GitHub!**)
2) Get a text-generation type of '.gguf' LLM model from https://huggingface.co/models
3) Place the '.gguf' model into the program's \model\ folder
4) Run the .exe file

WHAT YOU CAN DO WITH SOLAIRIA:
1) You can use it **completely offline** after downloading the .zip and obtaining your desired '.gguf' LLM model. No need to worry about your Q & A and conversations in the program leaking.
2) You can set its context size after starting up the program (1024, 2048-default or 4096). This governs how much context memory SOLAIRIA has to remember your conversation, and also affects your input length limit. Larger size = More chat history for it to refer to before replying = Slower replies as more tokens need to be processed.
3) You can give it a personality so that it responds in the style of that personality.
4) You can use it as your personal Q & A bot, a source of ideas and inspiration, a storyteller, a speechwriter, a temporary virtual confidante etc.
5) To remove SOLAIRIA from your computer, just delete the folders and files that you extracted initially from the .zip file. That's it.

WHAT YOU CANNOT DO WITH SOLARIA:
1) You cannot use non-text-generation type of LLM models as the program does not handle those right now.
2) You cannot save and load your chat session in the program. Once you close it, your conversation is gone. Re-launching will start from a blank slate again.
3) It cannot access the Internet to get info. All info it provides is based on the LLM loaded and the date it was trained (e.g. Llama 2 has a knowledge cutoff date of Dec 2022. It will not be able to give info on anything after Dec 2022).
