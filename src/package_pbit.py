"""Package India_Air_Quality_Analysis.pbit (Power BI Template).
This allows users to double-click and open the project directly in Power BI Desktop.
"""

import os
import zipfile
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PBIT_OUTPUT = os.path.join(BASE_DIR, "powerbi", "India_Air_Quality_Analysis.pbit")
BIM_PATH = os.path.join(BASE_DIR, "powerbi", "India_Air_Quality_Analysis.Dataset", "model.bim")
REPORT_PATH = os.path.join(BASE_DIR, "powerbi", "India_Air_Quality_Analysis.Report", "report.json")

with open(BIM_PATH, "r", encoding="utf-8") as f:
    bim_content = f.read()

with open(REPORT_PATH, "r", encoding="utf-8") as f:
    report_content = f.read()

content_types_xml = (
    '<?xml version="1.0" encoding="utf-8"?>\r\n'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\r\n'
    '  <Default Extension="json" ContentType="application/json" />\r\n'
    '  <Default Extension="xml" ContentType="application/xml" />\r\n'
    '  <Override PartName="/DataModelSchema" ContentType="" />\r\n'
    '  <Override PartName="/Report/Layout" ContentType="" />\r\n'
    '  <Override PartName="/Settings" ContentType="" />\r\n'
    '  <Override PartName="/Version" ContentType="" />\r\n'
    '</Types>'
)

version_bytes = "2.128.1000.0".encode("utf-16-le")
settings_bytes = json.dumps({"SecurityVersion": 2}).encode("utf-16-le")
layout_bytes = report_content.encode("utf-16-le")
schema_bytes = bim_content.encode("utf-16-le")

with zipfile.ZipFile(PBIT_OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types_xml.encode("utf-8"))
    z.writestr("Version", version_bytes)
    z.writestr("Settings", settings_bytes)
    z.writestr("Report/Layout", layout_bytes)
    z.writestr("DataModelSchema", schema_bytes)

print(f"✅ Packaged Power BI Template (.pbit): {PBIT_OUTPUT}")
