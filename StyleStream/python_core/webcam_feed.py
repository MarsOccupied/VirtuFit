import cv2
import numpy as np
from style_transfer import apply_style_to_frame # This will be the slow, placeholder version initially

def start_webcam_feed():
    cap = cv2.VideoCapture(0) # 0 for default webcam

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Webcam feed started. Press 'q' to quit.")

    # Placeholder for a loaded style model. In a real scenario, this would be a pre-trained feed-forward net.
    # For now, `apply_style_to_frame` will just pass through the original frame.
    trained_style_model = None # This will be replaced with an actual model later

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Failed to grab frame.")
            break

        # Convert the frame from BGR (OpenCV default) to RGB (for PIL/Torch if needed)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Apply style transfer (currently a placeholder, just returns original frame)
        styled_frame_rgb = apply_style_to_frame(frame_rgb, trained_style_model)

        # Convert back to BGR for OpenCV display
        styled_frame_bgr = cv2.cvtColor(styled_frame_rgb, cv2.COLOR_RGB2BGR)

        cv2.imshow('StyleStream Webcam Feed', styled_frame_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    start_webcam_feed()

