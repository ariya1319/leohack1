import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import ZBarSymbol
import json
from datetime import datetime
import os
import glob
from pupil_apriltags import Detector

class VideoMarkerDetector:
    def __init__(self):
        # Define QR code categories based on content
        self.categories = {
            'URL': [],
            'EMAIL': [],
            'PHONE': [],
            'TEXT': [],
            'WIFI': [],
            'VCARD': [],
            'UNKNOWN': []
        }
        self.detected_codes = set()  # To avoid duplicate QR code detections

        # AprilTag detector
        self.apriltag_detector = Detector(
            families='tag36h11',
            nthreads=1,
            quad_decimate=1.0,
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0
        )
        self.detected_apriltags = {}  # Store detected AprilTags by ID

    def categorize_qr_data(self, data):
        """Categorize QR code based on its content"""
        data_lower = data.lower()

        # Check for URL
        if data.startswith('http://') or data.startswith('https://') or data.startswith('www.'):
            return 'URL', data

        # Check for email
        elif '@' in data and '.' in data and ' ' not in data:
            return 'EMAIL', data

        # Check for phone number
        elif data.startswith('tel:') or (data.isdigit() and len(data) >= 10):
            return 'PHONE', data

        # Check for WiFi
        elif data.startswith('WIFI:'):
            return 'WIFI', data

        # Check for vCard
        elif data.startswith('BEGIN:VCARD'):
            return 'VCARD', data

        # Default to TEXT
        else:
            return 'TEXT', data

    def detect_and_display_video(self):
        """Main function: Detect QR codes and AprilTags from video stream URL"""
        # URL stream configuration
        video_url = "http://172.18.200.82/"

        # # OLD CODE: Get all video files from video/ directory
        # video_dir = "video/"
        #
        # if not os.path.exists(video_dir):
        #     print(f"Error: Directory '{video_dir}/' does not exist")
        #     print(f"Please create the directory and add video files to it")
        #     return
        #
        # # Support common video formats
        # video_patterns = [
        #     os.path.join(video_dir, "*.mp4"),
        #     os.path.join(video_dir, "*.avi"),
        #     os.path.join(video_dir, "*.mov"),
        #     os.path.join(video_dir, "*.mkv"),
        #     os.path.join(video_dir, "*.wmv"),
        #     os.path.join(video_dir, "*.flv")
        # ]
        #
        # video_files = []
        # for pattern in video_patterns:
        #     video_files.extend(glob.glob(pattern))
        #
        # if not video_files:
        #     print(f"Error: No video files found in '{video_dir}/' directory")
        #     print(f"Supported formats: mp4, avi, mov, mkv, wmv, flv")
        #     return
        #
        # print(f"Found {len(video_files)} video(s) in '{video_dir}/' directory")
        # print("Press 'q' to quit current video, 's' to save results, 'n' for next video, SPACE to pause/resume\n")
        #
        # for video_idx, video_path in enumerate(video_files):
        #     video_name = os.path.basename(video_path)
        #     print(f"\n[{video_idx + 1}/{len(video_files)}] Processing: {video_name}")
        #
        #     cap = cv2.VideoCapture(video_path)

        print(f"Connecting to video stream: {video_url}")
        print("Press 'q' to quit, 's' to save results, SPACE to pause/resume\n")

        video_name = "Stream: " + video_url
        cap = cv2.VideoCapture(video_url)

        if not cap.isOpened():
            print(f"Error: Failed to open stream {video_url}")
            return

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        # total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Not available for streams
        # duration = total_frames / fps if fps > 0 else 0

        print(f"  Connected! FPS: {fps:.2f}")
        print(f"  Stream source: {video_url}\n")

        frame_count = 0
        paused = False

        while True:
            if not paused:
                ret, frame = cap.read()

                if not ret:
                    print(f"  Lost connection to stream")
                    break

                frame_count += 1

                # Process every frame (can be optimized to skip frames if needed)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect QR codes
                decoded_objects = pyzbar.decode(frame)

                # Draw rectangles and decode QR codes
                for obj in decoded_objects:
                    # Extract QR code data
                    qr_data = obj.data.decode('utf-8')
                    qr_type = obj.type

                    # Get bounding box
                    x, y, w, h = obj.rect.left, obj.rect.top, obj.rect.width, obj.rect.height

                    # Categorize the QR code
                    category, display_data = self.categorize_qr_data(qr_data)

                    # Only process if we haven't seen this exact code recently
                    if qr_data not in self.detected_codes:
                        self.detected_codes.add(qr_data)
                        self.categories[category].append({
                            'data': qr_data,
                            'type': qr_type,
                            'video': video_name,
                            'frame': frame_count,
                            'timestamp': datetime.now().isoformat()
                        })

                        print(f"  ✓ Frame {frame_count}: Detected QR {category}: {display_data[:50]}")

                    # Draw rectangle around QR code (GREEN)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Put category label
                    cv2.putText(frame, f"QR-{category}", (x, y - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    # Put truncated data
                    display_text = display_data[:30] + "..." if len(display_data) > 30 else display_data
                    cv2.putText(frame, display_text, (x, y + h + 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)

                # Detect AprilTags
                apriltags = self.apriltag_detector.detect(gray)

                # Draw rectangles and decode AprilTags
                for tag in apriltags:
                    # Get corner points
                    corners = tag.corners.astype(int)

                    # Draw polygon around AprilTag (BLUE)
                    cv2.polylines(frame, [corners], True, (255, 0, 0), 2)

                    # Get center point
                    center = tag.center.astype(int)

                    # Draw center dot
                    cv2.circle(frame, tuple(center), 5, (0, 0, 255), -1)

                    # Track AprilTag
                    tag_id = tag.tag_id
                    if tag_id not in self.detected_apriltags:
                        self.detected_apriltags[tag_id] = {
                            'tag_id': tag_id,
                            'family': tag.tag_family.decode('utf-8'),
                            'hamming': tag.hamming,
                            'decision_margin': tag.decision_margin,
                            'first_seen_video': video_name,
                            'first_seen_frame': frame_count,
                            'timestamp': datetime.now().isoformat()
                        }
                        print(f"  ✓ Frame {frame_count}: Detected AprilTag ID: {tag_id} (family: {tag.tag_family.decode('utf-8')})")

                    # Put AprilTag ID label
                    cv2.putText(frame, f"AprilTag ID: {tag_id}", (corners[0][0], corners[0][1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

                    # Put additional info
                    cv2.putText(frame, f"Family: {tag.tag_family.decode('utf-8')}",
                               (corners[0][0], corners[0][1] - 35),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 0), 1)

                # Display video info and instructions
                # current_time = frame_count / fps if fps > 0 else 0  # OLD: Used for file playback
                # cv2.putText(frame, f"Video: [{video_idx + 1}/{len(video_files)}] {video_name}",  # OLD
                #            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                # cv2.putText(frame, f"Frame: {frame_count}/{total_frames} | Time: {current_time:.2f}/{duration:.2f}s",  # OLD
                #            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                cv2.putText(frame, f"Stream: {video_url}",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Frame: {frame_count} | FPS: {fps:.2f}",
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, f"QR Codes: {len(self.detected_codes)} | AprilTags: {len(self.detected_apriltags)}",
                           (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                status = "PAUSED" if paused else "LIVE"
                cv2.putText(frame, status, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                cv2.putText(frame, "SPACE: Pause/Resume | 's': Save | 'q': Quit",
                           (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Show current categories count
                status_text = " | ".join([f"{cat}: {len(self.categories[cat])}"
                                         for cat in self.categories if len(self.categories[cat]) > 0])
                if status_text:
                    cv2.putText(frame, status_text, (10, frame.shape[0] - 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 255, 100), 1)

            # Display the frame
            cv2.imshow('QR Code & AprilTag Detector - Video Stream', frame)

            # Keyboard input
            key = cv2.waitKey(1 if not paused else 0) & 0xFF
            if key == ord('q'):
                print(f"  Quitting stream...")
                break
            elif key == ord('s'):
                self.save_results()
            # elif key == ord('n'):  # OLD: Next video option
            #     print(f"  Moving to next video...")
            #     break
            elif key == ord(' '):
                paused = not paused
                print(f"  {'Paused' if paused else 'Resumed'}")

        cap.release()

        cv2.destroyAllWindows()
        self.print_summary()

    def save_results(self):
        """Save detected QR codes and AprilTags to JSON file"""
        filename = f"video_markers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        results = {
            'qr_codes': self.categories,
            'apriltags': list(self.detected_apriltags.values())
        }

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to {filename}")

    def print_summary(self):
        """Print summary of detected QR codes and AprilTags"""
        print("\n" + "="*60)
        print("VIDEO MARKER DETECTION SUMMARY")
        print("="*60)

        # QR Code Summary
        total_qr = sum(len(codes) for codes in self.categories.values())
        print(f"\nQR CODES: {total_qr} detected")
        print("-" * 60)

        for category, codes in self.categories.items():
            if codes:
                print(f"\n{category} ({len(codes)}):")
                for i, code in enumerate(codes, 1):
                    data_preview = code['data'][:50] + "..." if len(code['data']) > 50 else code['data']
                    print(f"  {i}. {data_preview}")
                    print(f"     Type: {code['type']}")
                    print(f"     Video: {code.get('video', 'N/A')} (Frame: {code.get('frame', 'N/A')})")
                    print(f"     Time: {code['timestamp']}")

        # AprilTag Summary
        print(f"\nAPRILTAGS: {len(self.detected_apriltags)} detected")
        print("-" * 60)

        if self.detected_apriltags:
            for tag_id, tag_info in sorted(self.detected_apriltags.items()):
                print(f"\n  Tag ID: {tag_id}")
                print(f"     Family: {tag_info['family']}")
                print(f"     Hamming: {tag_info['hamming']}")
                print(f"     Decision Margin: {tag_info['decision_margin']:.2f}")
                print(f"     First seen in: {tag_info['first_seen_video']} (Frame: {tag_info['first_seen_frame']})")
                print(f"     Time: {tag_info['timestamp']}")
        else:
            print("  No AprilTags detected")

        print("\n" + "="*60)

if __name__ == '__main__':
    detector = VideoMarkerDetector()
    detector.detect_and_display_video()
