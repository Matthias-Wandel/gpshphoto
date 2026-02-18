# Python script to gather GPS info from all the images that contain GPS timestamps.
# creates "gpstagged.txt" which is placed in the digicam directory
# alongside gpsbrowse.html, which loads this file for its data.
import os
import re

ROOT_DIR = "."            # start here
OUTPUT_FILE = "gpstagged.txt"

# Regex patterns
re_filename = re.compile(r"^File name\s*:\s*(.+)$", re.M)
re_datetime = re.compile(r"^Date/Time\s*:\s*(.+)$", re.M)
re_cameramodel = re.compile(r"^Camera model\s*:\s*(.+)$", re.M)
re_lat = re.compile(r"^GPS Latitude\s*:\s*([NS])\s*(\d+)d\s*(\d+)m\s*([\d.]+)s$", re.M)
re_lon = re.compile(r"^GPS Longitude\s*:\s*([EW])\s*(\d+)d\s*(\d+)m\s*([\d.]+)s$", re.M)

def dms_to_decimal(sign, deg, minutes, seconds):
    value = float(deg) + float(minutes) / 60.0 + float(seconds) / 3600.0
    if sign in ("S", "W"):
        value = -value
    return value

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for root, dirs, files in os.walk(ROOT_DIR):
        if "imagedata.cached" not in files:
            continue
        print(root,"has cache")
        cache_path = os.path.join(root, "imagedata.cached")

        with open(cache_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Entries are separated by blank lines
        entries = re.split(r"\n\s*\n", content)

        for entry in entries:
            m_file = re_filename.search(entry)
            m_time = re_datetime.search(entry)
            m_model = re_cameramodel.search(entry)
            m_lat = re_lat.search(entry)
            m_lon = re_lon.search(entry)

            if not (m_file and m_time and m_lat and m_lon):
                continue

            lat = dms_to_decimal(*m_lat.groups())
            lon = dms_to_decimal(*m_lon.groups())

            if lat == 0.0 and lon == 0.0:
                continue

            # Strip any path inside the filename, but keep directory path
            base_filename = os.path.basename(m_file.group(1))
            try:camera_model = m_model.group(1)
            except:camera_model = "????"
            full_path = os.path.join(root, base_filename)
            full_path = full_path.replace("\\","/")
            if full_path.startswith("./"): full_path = full_path[2:]

            out.write(f"{full_path}\n")
            out.write(f"Date/Time: {m_time.group(1)}\n")
            out.write(f"GPS: {lat:.6f},{lon:.6f}\n")
            out.write(f"Camera: {camera_model}\n\n")
