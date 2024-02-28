# Utils
from utils_config import *
from utils import *
# ================================================== #

args = sys.argv
if (len(args) > 1):
    msg = args[1]
else:
    msg = "Missing Arguments"

show_step(msg, c="light_red")
input()
# -------------------------------------------------- #