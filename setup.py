import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    'packages': [],
    'includes': [],
    'include_files': ['app_data.db','tb.ico','README.md', 'DejaVuSans-Bold.ttf', 'DejaVuSans.ttf'],
}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # Suppress console window

setup(
    name='dpfpa',
    version='1.0',
    description='Boris Tomka Application',
    options={'build_exe': build_exe_options},
    executables=[Executable(
        'dpfpa.py',
        base=base,
        icon='tb.ico',    # This is where you specify the icon
        target_name='dpfpa.exe'  # Optional: specify the name of the executable
    )]
)

# python setup.py build