# Alphabetic Keyboarding Revived

A Windows 11 typing tutor with a retro-inspired interface and **independently written lessons**. This is a new, independent application inspired by classroom keyboarding software of the 1990s—not a copy of the original DOS program.

## Features

- 18 lessons with 90 exercises covering home-row typing, additional keys, numbers, punctuation, and fluency.
- On-screen keyboard with next-key highlighting and finger guides.
- Practice and Timed Test modes. For lesson lines, timing begins with the first typed character and stops when you press **Enter**; it stays paused between lines.
- Keyboard Sprint, sentence-based speed tests, and speed goals.
- Student profiles, WPM and accuracy reports, CSV export, and record backup/restore.
- **Progress and Settings** for viewing results, clearing selected students' reports or all reports, and resetting the application.
- Clickable **Help & About** topics.

## For users: run the finished Windows app (no Python needed)

If a Windows executable has been published under the repository's **Releases** page:

1. Download `AlphabeticKeyboardingRevived.exe` from the release assets.
2. Save it somewhere convenient on your Windows 11 computer.
3. Double-click the EXE to launch the application.

**You do not need to install Python, run a `.bat` file, or use DOSBox to run the compiled EXE.** The EXE is a standalone build made with PyInstaller. This source repository/ZIP does **not** itself contain a prebuilt EXE; a maintainer must build and upload one to Releases.

## For developers: build the Windows EXE from source

**Requirements on the build computer:** Windows, Python 3.10 or later with `pip` and Tkinter, and an internet connection to install PyInstaller. Python is required **only on the computer building from source**, not on computers running the resulting EXE.

1. Download the repository ZIP and extract it, or clone the repository.
2. Install Python from <https://www.python.org/downloads/windows/> if needed. During setup, enable the Python launcher (`py`) or add Python to PATH. Standard Windows Python installations include Tkinter.
3. Open the extracted project folder.
4. Double-click **`BUILD_WINDOWS_EXE.bat`**.
5. The script checks Python, runs the automated tests, installs PyInstaller, and builds the executable. If a test or build step fails, read the error in the command window; no successful EXE is guaranteed.
6. If the build succeeds, find the executable at **`dist\AlphabeticKeyboardingRevived.exe`**. Double-click it to test it, then copy or upload that file for other Windows users.

### Build manually (optional)

Open PowerShell in the project folder and run:

```powershell
py -3 -m unittest discover -p "test_*.py" -v
py -3 -m pip install pyinstaller
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name AlphabeticKeyboardingRevived --version-file version_info.txt app.py
```

If `py` isn't available, substitute `python` if it points to a compatible Python installation. PyInstaller must be run **on Windows** to produce the Windows EXE; it does not cross-compile Windows executables from macOS or Linux.

The executable's **Product version** and **File version** are set to **1.0.0.0** in `version_info.txt` (visible in Windows File Properties after building).

## For developers: run the source without building

If you want to test or modify the Python code, install Python 3.10+ with Tkinter, then either:

- Double-click **`START_WINDOWS.bat`**, or
- Run `py -3 app.py` in the project folder.

**This source-code launch method requires Python.** It is not how end users run the finished EXE. The app itself uses Python's standard library; no additional runtime packages are needed for source execution.

## Project files

| File | Purpose |
|---|---|
| `app.py` | Application screens, navigation, student reports, and settings |
| `lesson_content.py` | Independently written lessons and exercises |
| `typing_content.py` | Keyboard Sprint content, sentence tests, and scoring helpers |
| `START_WINDOWS.bat` | Runs the Python source; **requires Python** |
| `BUILD_WINDOWS_EXE.bat` | Tests and builds the standalone Windows EXE; **requires Python** |
| `version_info.txt` | Windows EXE product/file metadata (1.0.0.0) |
| `test_*.py` | Automated tests |
| `.gitignore` | Excludes generated build files and local data from Git |

## Historical inspiration

This project began as an effort to revisit 1990s classroom keyboarding software. With appreciation to **Haugo, Hausmann, and Jackson**, credited as authors of the 1994 DOS *Alphabetic Keyboarding* program, whose work helped inspire this independent project.

This acknowledgment does not imply affiliation, sponsorship, or endorsement by those authors or the original publisher. No original DOS executables, proprietary lessons, menus, overlays, or graphics are required or bundled. The lessons in this repository were independently written.
