import subprocess


def test():
    subprocess.run(["python", "-u", "-m", "unittest", "discover", "-s", "./tests"])


def download_calibre_src():
    subprocess.run(["./scripts/download-calibre-src.sh"])


def create_release():
    subprocess.run(["./scripts/create-release.sh"])
