import subprocess


OPTIONS = [
    "--onefile",
    "--name=MonApplication",
    "--clean"
]

ENTRY_POINT = "main.py"


def build():
    cmd = ["pyinstaller"] + OPTIONS + [ENTRY_POINT]

    print("🚀 Génération de l'exécutable...")
    subprocess.run(cmd)


if __name__ == "__main__":
    build()
