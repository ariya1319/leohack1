import subprocess
import cv2
import numpy as np
import struct

from qr_code_detector import detect_qr_codes, draw_qr_codes_on_frame


def capture_browser_stream_wsl():
    """Capture video frames from Windows browser using PowerShell"""
    
    print("Starting screen capture from Windows browser window...")
    print("Press 'q' to quit\n")
    
    # PowerShell script to capture screenshot
    ps_script = r'''
    [void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
    
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen
    $bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($screen.Bounds.Location, [System.Drawing.Point]::Empty, $screen.Bounds.Size)
    
    $memStream = New-Object System.IO.MemoryStream
    $bitmap.Save($memStream, [System.Drawing.Imaging.ImageFormat]::Jpeg)
    [System.Console]::Out.Flush()
    [System.Console]::OpenStandardOutput().Write($memStream.ToArray(), 0, $memStream.Length)
    
    $graphics.Dispose()
    $bitmap.Dispose()
    '''
    
    frame_count = 0
    
    try:
        while True:
            try:
                # Call PowerShell to capture screenshot
                result = subprocess.run(
                    ['powershell.exe', '-NoProfile', '-Command', ps_script],
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode == 0 and len(result.stdout) > 0:
                    # Decode JPEG from PowerShell output
                    nparr = np.frombuffer(result.stdout, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        frame_count += 1
                        
                        # Add frame counter
                        cv2.putText(frame, f"Frames: {frame_count}", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        qr_codes = detect_qr_codes(frame)
                        print("Number of QR Codes detected:", len(qr_codes))

                        # frame = draw_qr_codes_on_frame(frame, qr_codes) # this doesn't work, doesn't matter.

                        # Display
                        cv2.imshow("Browser Stream Capture (WSL)", frame)
                        
                        if frame_count % 30 == 0:
                            print(f"✓ Captured {frame_count} frames")
                        
                        # Press 'q' to quit
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            print("Quitting...")
                            break
            
            except subprocess.TimeoutExpired:
                print("Screenshot timeout")
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    except KeyboardInterrupt:
        print("Interrupted")
    
    cv2.destroyAllWindows()
    print(f"Done! Total frames: {frame_count}")

if __name__ == '__main__':
    capture_browser_stream_wsl()