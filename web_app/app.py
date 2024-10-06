# Utils
from root_config import *
from utils import *

from threading import Timer
import webbrowser

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn, signal

from search import Search
# ===================================================================== #

# change the current working directory
os.chdir(os.path.dirname(__file__))

# APP
app = FastAPI(debug=True)

# template setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# --------------------------------------------------------------------- #

# -- Endpoints -- #

# Home
@app.get('/')
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
# --------------------------------------------------------------------- #

# Search
@app.get('/search/')
async def search(search_key: str):
    results = Search(search_key).search()
    return results
# --------------------------------------------------------------------- #

# Download
@app.get('/download/')
async def download(url: str, vtype: str, name: str, year: str, season: str, episodes: str):
    run_python("main.py", args=[url, vtype, name, year, season, episodes, "auto"])
    
    os.kill(os.getpid(), signal.SIGINT)
    return "Maybe I'm the problem"
# --------------------------------------------------------------------- #

# Download from "staged.json"
@app.get('/open-staged')
async def open_staged():
    run_python("main.py", args=["Penalti a favor del Real Madrid"]*6 + ["open-staged"])
    close_browser()
    
    os.kill(os.getpid(), signal.SIGINT)
    return "Penalti a favor del Real Madrid"
# --------------------------------------------------------------------- #

# Manual Subtitle
@app.get('/download-subtitle/')
async def manual_subtitle(vtype: str, url: str, name: str, year: str, season: str):
    title = f"{name} ({year})" if (year) else name
    run_python("subtitles.py", args=[vtype, url, title, season])
    
    os.kill(os.getpid(), signal.SIGINT)
    return "Penalti a favor del Real Madrid"
# --------------------------------------------------------------------- #

# Run App
if (__name__ == "__main__"):
    HOST, PORT = "127.0.0.1", 6969
    Timer(0.5, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    uvicorn.run(app, host=HOST, port=PORT)
# --------------------------------------------------------------------- #