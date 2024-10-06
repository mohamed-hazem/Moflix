# Utils
from root_config import *
from utils import *

# Modules 
from glob import glob
import shutil
# ===================================================================== #

class Merger:
    def __init__(self, tmp_path: str, title: str):
        self.tmp_path = tmp_path
        self.output_file = os.path.join(os.path.dirname(self.tmp_path), f"{title}.mp4")
    # ---------------------------------------------- #

    def __merge_files(self, ts_files: list[str], output_file: str):
        cmd = ["ffmpeg", "-i", "concat:"+"|".join(ts_files), "-c", "copy", output_file]
        result = subprocess.run(cmd, cwd=self.tmp_path, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        if (result.returncode != 0):
            raise Exception(f"Merging Failed!\n{result.stderr.decode()}")
    # ---------------------------------------------- #

    def merge(self):
        ts_files = glob(pathname="seg*.ts", root_dir=self.tmp_path)
        
        mid = len(ts_files) // 2
        p1 = ts_files[:mid]
        p2 = ts_files[mid:]
        
        self.__merge_files(p1, "p1.ts")
        self.__merge_files(p2, "p2.ts")
        self.__merge_files(["p1.ts", "p2.ts"], self.output_file)

        shutil.rmtree(self.tmp_path)
# --------------------------------------------------------------------- #