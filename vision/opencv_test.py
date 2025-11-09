import cv2

esp32_ip = "172.18.200.82"

endpoints = [
    f"http://{esp32_ip}/",
    f"http://{esp32_ip}:80/",
]

cap = None
for url in endpoints:
    print(f"Trying: {url}")
    cap = cv2.VideoCapture(url)
    if cap.isOpened():
        print(f"✓ Works! Connected to {url}")
        break
    cap.release()

if not cap or not cap.isOpened():
    print("Failed")
    exit()

print("Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow("Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()