# Utils
from utils_config import *
from utils import *
# ================================================== #

# Input data
if (len(sys.argv) != 4):
    show_step("Missing Arguments", c="light_red")
    input()
else:
    _, url, name, input_season = sys.argv
    pyperclip.copy(name)
    vid = url.split("-")[-1]
    if (input_season == ""):
        input_season = int(input("Season: ").strip())
    else:
        input_season = int(input_season)
# -------------------------------------------------- #

# Get episodes names
s_page = HTMLParser(requests.get(f"{SEASONS_API}{vid}").content)
seasons = s_page.css("a")
s_id = seasons[input_season-1].attributes["data-id"] if (len(seasons) >= input_season) else None

if (s_id):
    e_page = HTMLParser(requests.get(f"{EPISODES_API}{s_id}").content)
    episodes = []
    for e in e_page.css("a"):
        e_num, e_name = e.text(strip=True).split(":", 1)
        if (e_num != "Eps 0"):
            episodes.append(f"E{e_num[4:].zfill(2)} - {e_name.replace(':', '')}")
else:
    print(s_id)
    show_step(f"Season {input_season} isn't found!", c="light_red")
    input()

show_title(f"{name} S{str(input_season).zfill(2)} | {len(episodes)} Episodes", c="light_yellow")
sleep(1)
# -------------------------------------------------- #

# Open `subscene.com`
webbrowser.open(SUBSCENE_URL)

sub_file = input(" Subtitle file: ").strip('"')
close_browser()
# -------------------------------------------------- #

# Extract the subtitle file
sub_path = os.path.join(TVSHOWS_DIR, name, f"Season {input_season}", "subs")
os.makedirs(sub_path, exist_ok=True)

# Unzip downloaded file
with zipfile.ZipFile(sub_file, "r") as zip_ref:
    zip_ref.extractall(sub_path)
    files = [x.filename for x in zip_ref.infolist()]
    files.sort()

    # check if subtitle files don't match episodes number
    ex = None
    if (len(files) != len(episodes)):
        print(colored(" Subtitle files don't match episodes number", color="light_red"))
        print(colored(f" {len(episodes)} Episodes | {len(files)} Files", color="light_red"))

        o = input(" Continue/Exit (c/e): ")
        if (o == "c"):
            ex = list(map(int, input("Episodes to exclude?: ").strip().split()))

            # check that the excluded files are the right number
            if (abs(len(episodes) - len(files)) != len(ex)):
                input("Episode to exclude number is incorrect :(")
                exit()
        else:
            exit()
    
    e_idx = 0
    for i in range(len(files)):
        if (ex is not None):
            if (i+1 in ex):
                e_idx += 1
            
        file_path_old = os.path.join(sub_path, files[i])
        file_path_new = os.path.join(sub_path, filter_name(episodes[e_idx])+".srt")
        os.rename(file_path_old, file_path_new)
        e_idx += 1

os.remove(sub_file)
quit()
# -------------------------------------------------- #