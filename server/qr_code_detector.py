import cv2
import pyzbar.pyzbar as pyzbar
from typing import List, Dict, Tuple

def detect_qr_codes(frame) -> List[Dict]:
    """
    Detect QR codes in a frame and return their positions and data.
    
    Args:
        frame: OpenCV image frame (BGR format)
    
    Returns:
        List of dictionaries containing QR code information:
        [
            {
                'data': 'QR code content',
                'type': 'QRCODE',
                'position': {'x': int, 'y': int, 'width': int, 'height': int},
                'category': 'URL/EMAIL/PHONE/TEXT/WIFI/VCARD/UNKNOWN',
                'display_data': 'Truncated data for display'
            },
            ...
        ]
    """
    
    qr_codes = []
    
    # Detect QR codes
    decoded_objects = pyzbar.decode(frame)
    
    for obj in decoded_objects:
        # Extract QR code data
        qr_data = obj.data.decode('utf-8')
        qr_type = obj.type
        
        # Get bounding box
        x, y, w, h = obj.rect.left, obj.rect.top, obj.rect.width, obj.rect.height
        
        # Categorize the QR code
        category = categorize_qr_data(qr_data)
        
        # Truncate data for display
        display_data = qr_data[:30] + "..." if len(qr_data) > 30 else qr_data
        
        # Add to results
        qr_codes.append({
            'data': qr_data,
            'type': qr_type,
            'position': {
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'x_end': x + w,
                'y_end': y + h
            },
            'category': category,
            'display_data': display_data
        })
    
    return qr_codes


def categorize_qr_data(data: str) -> str:
    """Categorize QR code based on its content"""
    
    # Check for URL
    if data.startswith('http://') or data.startswith('https://') or data.startswith('www.'):
        return 'URL'
    
    # Check for email
    elif '@' in data and '.' in data and ' ' not in data:
        return 'EMAIL'
    
    # Check for phone number
    elif data.startswith('tel:') or (data.isdigit() and len(data) >= 10):
        return 'PHONE'
    
    # Check for WiFi
    elif data.startswith('WIFI:'):
        return 'WIFI'
    
    # Check for vCard
    elif data.startswith('BEGIN:VCARD'):
        return 'VCARD'
    
    # Default to TEXT
    else:
        return 'TEXT'


def draw_qr_codes_on_frame(frame, qr_codes: List[Dict]) -> None:
    """
    Draw detected QR codes on the frame.
    
    Args:
        frame: OpenCV image frame to draw on
        qr_codes: List of QR code dictionaries from detect_qr_codes()
    """
    
    for qr in qr_codes:
        pos = qr['position']
        x, y, w, h = pos['x'], pos['y'], pos['width'], pos['height']
        print(x, y, w, h)
        category = qr['category']
        display_data = qr['display_data']
        
        # Draw rectangle around QR code (GREEN)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Put category label
        cv2.putText(frame, f"QR-{category}", (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Put truncated data
        cv2.putText(frame, display_data, (x, y + h + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
        
        return frame


# Example usage:
if __name__ == '__main__':
    # Read a test image or frame
    frame = cv2.imread('images/PXL_20251108_142820159.jpg')
    
    if frame is None:
        print("Error reading image")
        exit()
    
    # Detect QR codes
    qr_codes = detect_qr_codes(frame)
    
    # Print results
    print(f"Found {len(qr_codes)} QR codes:")
    for i, qr in enumerate(qr_codes):
        print(f"\n{i+1}. Data: {qr['data']}")
        print(f"   Category: {qr['category']}")
        print(f"   Position: ({qr['position']['x']}, {qr['position']['y']}) - {qr['position']['width']}x{qr['position']['height']}")
    
    # Draw and display
    frame = draw_qr_codes_on_frame(frame, qr_codes)
    cv2.imshow('QR Codes Detected', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()