import cv2
from ultralytics import YOLO

model = YOLO('iotsmart_gym.pt')
cap = cv2.VideoCapture("ex1.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    results = model(frame, verbose=False)
    annotated = results[0].plot()
    cv2.line(annotated, (600, 0), (600, 1920), (0, 255, 0), 3)
    annotated = cv2.resize(annotated, (360, 640))

    cv2.imshow("YOLO 모니터", annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()