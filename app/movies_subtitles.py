# Utils
from utils_config import *
from utils import *
# ================================================== #

# Get movie ID [OpenSubtitles]
def get_movie_id(movie_name):
    response = requests.get(SUBTITLE_MOVIE_SEARCH, params={"MovieName": movie_name})
    movie_id = response.json()[0]["id"]
    return movie_id
# -------------------------------------------------- #

# Get subtitle ID [OpenSubtitles]
def get_sub_id(movie_id):
    sub_url = f"{SUBTITLE_SEARCH}/idmovie-{movie_id}"
    response = requests.get(sub_url)

    # check if it's only one subtitle
    res_url = response.url.split("/")
    if (res_url[4] == "subtitles"):
        sub_id = res_url[5]
        return sub_id
    
    # in case there are many subtitles
    e_page = HTMLParser(response.content)
    subs = e_page.css("tr.change.expandable")
    
    sub_scores = []
    for sub in subs:
        sub_tds = sub.css("td")
        sub_id = sub.attributes["id"][4:]

        # year and FPS
        year_fps = sub_tds[3].text(strip=True)
        year = int(year_fps[6:10])
        fps = int(year_fps[10:12]) if (len(year_fps) > 10) else None
        if (fps != 23) and (fps is not None):
            continue

        # download number
        dl_no = sub_tds[4].text(strip=True)
        dl_no = int("".join([c if c.isnumeric() else "" for c in dl_no]))

        # uploder batch
        uploader = sub_tds[8]
        uploader_name = uploader.text(strip=True)
        uploader_icon = uploader.css_first("img")
        uploader_rank = uploader_icon.attributes["title"] if (uploader_icon) else ""

        # score
        dl_per_year = dl_no / (CURRENT_YEAR - year)

        uploader_score = 0
        if (uploader_name):
            uploader_score += SUB_WEIGHT
            uploader_score += SUBTITLE_RANKS.get(uploader_rank, 0)

        score = dl_per_year + uploader_score
        sub_scores.append((score, sub_id))
    
    sub_scores.sort(reverse=True)
    if (sub_scores):
        return sub_scores[0][1]
    else:
        return None
# -------------------------------------------------- #

# Download subtitle
def dl_sub(sub_id, sub_path, dl_title):
    sub_file = os.path.join(sub_path, dl_title)

    if (os.path.isfile(sub_file+".srt")):
        return

    # download subtitle file
    url = f"https://www.opensubtitles.org/en/subtitleserve/sub/{sub_id}"
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'MyApp/1.0')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, sub_file+".zip")

    # unzip downloaded file
    with zipfile.ZipFile(sub_file+".zip", "r") as zip_ref:
        zip_ref.extractall(sub_path)

        for file in zip_ref.infolist():
            file = os.path.join(sub_path, file.filename)
            if (file.endswith("srt") or file.endswith("txt")):
                os.rename(file, sub_file+".srt")
            else:
                os.remove(file)
    
    # remove zip file
    os.remove(sub_file+".zip")
# -------------------------------------------------- #

# Clean subtitle
def clean_sub(sub_path, dl_title):
    sub_file = os.path.join(sub_path, dl_title+".srt")

    # read subtitle
    for encoder in ENCODERS:
        try:
            with open(sub_file, "r", encoding=encoder) as f:
                subs = list(srt.parse(f.read()))
            break
        except UnicodeDecodeError:
            continue

    # clean subtitle
    sub: srt.Subtitle
    clean_subs = []
    for sub in subs:
        sub_content = str(sub.content).replace("ـ", "").lower()
        if not (re.findall(SUB_FILTER_PATTERN, sub_content)):
            clean_subs.append(sub)
    del subs
    
    # save cleaned subtitle
    with open(sub_file, "w", encoding=MAIN_ENCODER) as f:
        f.write(srt.compose(clean_subs))
# -------------------------------------------------- #

# Main Subtitle Function #
def subtitle(dl_title):
    sub_path = os.path.join(MOVIES_DIR, dl_title)
    
    try:
        movie_id = get_movie_id(movie_name=dl_title)
        sub_id = get_sub_id(movie_id)

        if (sub_id):
            dl_sub(sub_id, sub_path, dl_title)
            clean_sub(sub_path, dl_title)
    
    except Exception as e:
        run_python("ext_alert.py", args=[f"Failed to download subtitle for {dl_title} | {e}"])
# -------------------------------------------------- #