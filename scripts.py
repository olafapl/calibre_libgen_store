import subprocess


def test():
    subprocess.run(["python", "-u", "-m", "unittest", "discover"])


def download_calibre_src():
    subprocess.run(["sh", "./download-calibre-src.sh"])
