# Utils
from utils_config import *
from utils import *
# ================================================== #

# Get watch urls
def get_watch_urls(url, vid, vtype, title, season, episodes):
    watch_urls = []
    if (vtype == "Movie"):
        page = HTMLParser(requests.get(f"{MOVIES_API}{vid}").content)
        w_url = BASE_URL + page.css_first("a.nav-link").attributes["href"]
        watch_urls.append((title, w_url))

    elif (vtype == "TV"):
        s_page = HTMLParser(requests.get(f"{SEASONS_API}{vid}").content)
        seasons = s_page.css("a")
        s_id = seasons[season-1].attributes["data-id"] if (len(seasons) >= season) else None

        if (s_id):
            e_page = HTMLParser(requests.get(f"{EPISODES_API}{s_id}").content)
            eps = e_page.css("a")[episodes[0]:episodes[1]]

            for e in eps:
                e_id = e.attributes["data-id"]
                e_watch_id = HTMLParser(requests.get(f"{EPISODES_WATCH_API}{e_id}").content).css("a")[SERVER-1].attributes['data-id']

                w_url = f"{url}.{e_watch_id}"
                e_name = e.attributes["title"].split(":")
                e_name = " - ".join([f"E{e_name[0].split(' ')[1].zfill(2)}".strip(), e_name[1].strip()])
                watch_urls.append((e_name, w_url))
        else:
            raise Exception(f" Season {season} is not found :( | {len(season)} Seasons")
    
    return watch_urls
# -------------------------------------------------- #

# Write the number of URLs to capture
def create_requests_file(watch_urls):
    with open(os.path.join(FIDDLER_TMP_REQUESTS, "requests_number.txt"), "w") as f:
        f.write(str(len(watch_urls)))
# -------------------------------------------------- #

# Stage files
def stage(vid, vtype, title, season, m3_urls):
    new_data = {vid: {
        "type": vtype,
        "title": title,
        "season": season
    }}
    m3_data = {title: m3_url for title, m3_url in m3_urls}
    new_data[vid].update(m3_data)

    with open(STAGE_FILE, "r+") as f:
        data = f.read()
        data = json.loads(data) if (data) else dict()
        data.update(new_data)
        
        f.seek(0)
        json.dump(data, f)
        f.truncate()
# -------------------------------------------------- #

# Check if `Fiddler` captured the url
def check_file(i, title: str):
    file = os.path.join(FIDDLER_TMP_REQUESTS, f"{i}.txt")
    c = 0
    while True:
        sys.stdout.write(f"\r {title} | {c} checked ...")
        if (os.path.isfile(file)):
            with open(file, "r") as f:
                print(colored(f"\r {title.ljust(100)}", "light_green"))
                m3_url = f.read()
            
            os.remove(file)
            return m3_url
        
        c += 1
        if (c == 200):
            print(colored(f"\r {title.ljust(100)}", "light_red"))
            return None
        sleep(0.2)
# -------------------------------------------------- #

# Open browser and `Fiddler` to capture m3 urls
def get_m3_urls(watch_urls):
    m3_urls = []
    for i, watch_url in enumerate(watch_urls, start=1):
        title, url = watch_url

        # start `Fiddler` at fisrt loop
        if (i == 1):
            subprocess.Popen(os.path.join(FIDDLER_PATH, "Fiddler Classic.lnk"), shell=True)
            wait_for_fiddler()

        # open the url in the browser
        webbrowser.open(url)
        # minimize_browser()

        # get m3 url
        m3_url = check_file(i, title)
        if (m3_url):
            m3_url = "/".join(m3_url.split("/")[:-1])
            m3_urls.append((title, m3_url))
        
        # check final loop
        if (i == len(watch_urls)):
            close_browser()
    
    return m3_urls
# -------------------------------------------------- #

# -- Main Capture & Stage Function -- #
def capture_stage(url, vid, vtype, title, season, episodes):
    watch_urls = get_watch_urls(url, vid, vtype, title, season, episodes)
    create_requests_file(watch_urls)
    m3_urls = get_m3_urls(watch_urls)
    stage(vid, vtype, title, season, m3_urls)
# -------------------------------------------------- #