import subprocess


def test():
    subprocess.run(["python", "-u", "-m", "unittest", "discover", "-s", "./tests"])


def download_calibre_src():
    subprocess.run(["./scripts/download-calibre-src.sh"])
