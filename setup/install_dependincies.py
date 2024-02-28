# -- Install dependincies -- #
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(__file__))
os.chdir(ROOT)

subprocess.run("pip install -r requirements.txt", shell=True)

input("\n All dependincies has been installed")
# ================================================== #