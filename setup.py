from cx_Freeze import setup, Executable

setup(
    name = "Exporter",
    version = "0.1",
    description = "App de exportacion",
    executables = [Executable(script="cli.py")]
)