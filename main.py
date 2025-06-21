# SOLAIRIA (Software for Offline Loading of AI by Russ for Interaction and Assistance)
# First written by Russ on 18 Jan 2024 (https://github.com/rrrusst/solairia).

version = "2.0.3"

# From custom modules
import gui
from core_funcs import set_personality

if __name__ == "__main__":
    set_personality()

    gui.root.protocol("WM_DELETE_WINDOW", gui.close_app)
    gui.txt_user.focus_force()
    gui.root.mainloop()
