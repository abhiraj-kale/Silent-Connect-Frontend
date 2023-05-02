import cv2
import mediapipe
import time
from utils.dataset_utils import load_dataset, load_reference_signs
from utils.mediapipe_utils import *
from sign_recorder import SignRecorder
from webcam_manager import WebcamManager



if __name__ == "__main__":
    # Create dataset of the videos where landmarks have not been extracted yet
    videos = load_dataset()

    # Create a DataFrame of reference signs (name: str, model: SignModel, distance: int)
    reference_signs = load_reference_signs(videos)

    # Object that stores mediapipe results and computes sign similarities
    sign_recorder = SignRecorder(reference_signs)

    # Object that draws keypoints & displays results
    webcam_manager = WebcamManager()

    # Turn on the webcam
    cap = cv2.VideoCapture(0)
    # Set up the Mediapipe environment
    with mediapipe.solutions.holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        # set a flag to keep track of whether the sign is currently being recorded
        is_recording = False
        is_paused = False

        # set the start time for the timer
        start_time = time.time()

        while cap.isOpened():

            # Read feed
            ret, frame = cap.read()
            #cv2.waitKey(50)
            #print(frame)
            # Make detections
            image, results = mediapipe_detection(frame, holistic)

            # Process results
            sign_detected, is_recording = sign_recorder.process_results(results)

            # Update the frame (draw landmarks & display result)
            webcam_manager.update(frame, results, sign_detected, is_recording)

            # Check for user input
            pressedKey = cv2.waitKey(1) & 0xFF
            if pressedKey == ord("r"):
                sign_recorder.record()
                start_time = time.time()
            elif pressedKey == ord("q"):
                break
            elif pressedKey == ord("p"):
                is_paused = not is_paused

            # Check if recording should continue
            if (
                sign_detected
                and not is_recording
                and not is_paused
                and time.time() - start_time >= 5
            ):
                sign_recorder.record()
                start_time = time.time()
        cap.release()
        cv2.destroyAllWindows()
