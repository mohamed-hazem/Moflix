# Utils
from utils_config import *
from utils import *

from API import search_results
# ================================================== #

# APP
app = Flask(__name__)

# -- Home Page -- #
@app.route('/')
def home():
    return render_template("index.html")
# -------------------------------------------------- #

# -- Search -- #
@app.route('/search', methods=['GET'])
def search():
    if (request.method == "GET"):
        search_key = request.args.get("search_key")
        
        return search_results(search_key)
# -------------------------------------------------- #
    
# -- Download -- #
@app.route('/download', methods=['GET'])
def download():
    if (request.method == "GET"):
        url = request.args["id"]
        vtype = request.args["type"]
        name = request.args["name"]
        year = request.args["year"]
        season = request.args["season"]
        episodes = request.args["episodes"]
        run_python("main.py", args=[url, vtype, name, year, season, episodes, "main"])
        
        os.kill(os.getpid(), signal.SIGINT)
        return {"response": "Fuck My Life :("}
# -------------------------------------------------- #

# -- Manual Subtitle -- #
@app.route('/manual-subtitle', methods=['GET'])
def manual_subtitle():
    if (request.method == "GET"):
        url = request.args["id"]
        name = request.args["name"]
        season = request.args["season"]
        run_python("tvshows_subtitle.py", args=[url, name, season])

        os.kill(os.getpid(), signal.SIGINT)
        return {"response": "Fuck Real Madrid"}
# -------------------------------------------------- #

# -- Manual Main -- #
@app.route('/manual-main', methods=['GET'])
def manual_main():
    if (request.method == "GET"):
        args = ["FUCK"]*6 + ["manual_main"]
        run_python("main.py", args=args)

        os.kill(os.getpid(), signal.SIGINT)
        return {"response": "I WANNA GO TO THE US"}
# -------------------------------------------------- #

if (__name__ == "__main__"):
    port = 5000
    threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(port=port)
# -------------------------------------------------- #