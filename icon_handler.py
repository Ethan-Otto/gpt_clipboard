import os
import sys
from PyQt5.QtGui import QIcon
from cairosvg import svg2png
from PIL import Image
import io

def create_program_icon():
    """Create program icon from SVG and return QIcon"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
    <rect x="56" y="56" width="400" height="400" rx="48" fill="#4a90e2" />
    <g transform="translate(128, 128)">
        <rect x="20" y="20" width="200" height="240" rx="12" fill="#ffffff" opacity="0.6"/>
        <rect x="40" y="10" width="200" height="240" rx="12" fill="#ffffff" opacity="0.8"/>
        <rect x="60" y="0" width="200" height="240" rx="12" fill="#ffffff"/>
        <rect x="90" y="40" width="140" height="10" rx="2" fill="#4a90e2"/>
        <rect x="90" y="70" width="120" height="10" rx="2" fill="#4a90e2"/>
        <rect x="90" y="100" width="140" height="10" rx="2" fill="#4a90e2"/>
    </g>
</svg>'''

    # Convert SVG to PNG using cairosvg
    png_data = svg2png(bytestring=svg_content.encode('utf-8'), 
                      output_width=512, 
                      output_height=512)
    
    # Create QIcon from the PNG data
    img = Image.open(io.BytesIO(png_data))
    
    # Save temporary icon file
    icon_path = os.path.join(os.path.dirname(__file__), 'temp_icon.png')
    img.save(icon_path)
    
    # Create QIcon
    icon = QIcon(icon_path)
    
    # Clean up temporary file
    try:
        os.remove(icon_path)
    except:
        pass
        
    return icon