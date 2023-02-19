import subprocess


def test():
    subprocess.run(["python", "-u", "-m", "unittest", "discover"])
