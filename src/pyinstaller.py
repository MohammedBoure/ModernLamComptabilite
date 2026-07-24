# build_exe.py
import os
import shutil
import subprocess
import sys
from pathlib import Path

import mysql.connector


DATA_SEPARATOR = ";" if os.name == "nt" else ":"


def _data_arg(project_dir, source_relative_path, destination_relative_path):
    source_path = (project_dir / source_relative_path).resolve()
    if not source_path.exists():
        print(f"Warning: Missing build asset: {source_path}")
        return None
    return f"--add-data={source_path}{DATA_SEPARATOR}{destination_relative_path}"


def _clean_target(project_dir, exe_name):
    build_path = project_dir / "build"
    if build_path.exists():
        shutil.rmtree(build_path)

    spec_path = project_dir / f"{exe_name}.spec"
    if spec_path.exists():
        spec_path.unlink()

    dist_target = project_dir / "dist" / exe_name
    if dist_target.exists():
        shutil.rmtree(dist_target)


def build_production():
    """
    Build the FINANCELAM executable.
    """
    project_dir = Path(__file__).resolve().parent
    
    # Application specifics
    main_script = "main.py"
    exe_name = "FINANCELAM"

    # MySQL specific paths for bundling
    mysql_path = Path(mysql.connector.__file__).resolve().parent
    plugins_src = mysql_path / "plugins"
    locales_src = mysql_path / "locales"

    _clean_target(project_dir, exe_name)

    data_args = []
    
    # Add UI styles
    styles_arg = _data_arg(project_dir, "ui/styles.qss", "ui")
    if styles_arg:
        data_args.append(styles_arg)

    # Add PDF settings if they exist
    pdf_settings_arg = _data_arg(project_dir, "pdf_settings.json", ".")
    if pdf_settings_arg:
        data_args.append(pdf_settings_arg)

    # Add MySQL components
    if plugins_src.exists():
        data_args.append(f"--add-data={plugins_src}{DATA_SEPARATOR}mysql/connector/plugins")
    if locales_src.exists():
        data_args.append(f"--add-data={locales_src}{DATA_SEPARATOR}mysql/connector/locales")

    # Logo Handling (Use if exists, proceed without if missing)
    icon_arg = None
    possible_logos = ["logo.ico", "logo.png", "icon.ico", "icon.png", "assets/logo.ico", "assets/logo.png"]
    found_logo_path = None
    
    for logo_name in possible_logos:
        logo_path = project_dir / logo_name
        if logo_path.exists():
            found_logo_path = logo_path
            break
            
    if found_logo_path:
        # Add to bundled data so it can be used inside the application UI if necessary
        dest_folder = found_logo_path.parent.relative_to(project_dir) if found_logo_path.parent != project_dir else "."
        logo_data_arg = _data_arg(project_dir, found_logo_path.relative_to(project_dir), dest_folder)
        if logo_data_arg:
             data_args.append(logo_data_arg)
        
        # Add as executable icon
        icon_arg = f"--icon={found_logo_path.resolve()}"
        print(f"Found logo at: {found_logo_path}")
    else:
        print("No logo found. Building without custom icon.")

    # Base PyInstaller command
    command = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onedir",
        f"--name={exe_name}",
        "--clean",
        f"--paths={project_dir}",
        *data_args,
        "--collect-all=PySide6",
        "--collect-all=mysql.connector",
        "--collect-all=reportlab",
        "--collect-all=pandas",
        "--hidden-import=mysql.connector.plugins.mysql_native_password",
        "--hidden-import=sqlalchemy",
        "--hidden-import=openpyxl",
    ]

    # Append icon argument if we found a logo
    if icon_arg:
        command.append(icon_arg)

    # Finally append the main script
    command.append(main_script)

    try:
        print(f"Building {exe_name} for production...\n")
        subprocess.check_call(command, cwd=project_dir)

        dist_path = project_dir / "dist" / exe_name

        # Copy any external config files that shouldn't be bundled inside the exe
        for cfg in (".env", "config.json"):
            cfg_path = project_dir / cfg
            if cfg_path.exists():
                shutil.copy2(cfg_path, dist_path / cfg)
                print(f"Copied external config: {cfg}")

        # Create necessary empty directories
        for folder in ("documents", "exports"):
            (dist_path / folder).mkdir(parents=True, exist_ok=True)

        print("\nSUCCESS!")
        print(f"Application generated in: dist/{exe_name}")

    except subprocess.CalledProcessError as e:
        print("\nPyInstaller failed.")
        print(e)
        raise

    except Exception as e:
        print("\nUnexpected error.")
        print(e)
        raise


if __name__ == "__main__":
    build_production()
