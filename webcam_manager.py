import cv2
import numpy as np
import mediapipe as mp
from gtts import gTTS
from playsound import playsound
import os
audio = 'output/speech.mp3'
language = 'en-IN'


WHITE_COLOR = (245, 242, 226)
RED_COLOR = (25, 35, 240)

HEIGHT = 600


class WebcamManager(object):
    """Object that displays the Webcam output, draws the landmarks detected and
    outputs the sign prediction
    """

    def __init__(self):
        self.sign_detected = ""

    def update(
        self, frame: np.ndarray, results, sign_detected: str, is_recording: bool
    ):
        self.sign_detected = sign_detected
        # if self.sign_detected:
        #     if os.path.exists('output/speech.mp3'):
        #         os.remove('output/speech.mp3')
        #     sp = gTTS(self.sign_detected, lang=language)
        #     sp.save(audio)
        #     playsound(audio)

       
        # Draw landmarks
        self.draw_landmarks(frame, results)

        WIDTH = int(HEIGHT * len(frame[0]) / len(frame))
        # Resize frame
        frame = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)

        # Flip the image vertically for mirror effect
        frame = cv2.flip(frame, 1)

        # Write result if there is
        frame = self.draw_text(frame)

        # Chose circle color
        color = WHITE_COLOR
        if is_recording:
            color = RED_COLOR

        # Update the frame
        cv2.circle(frame, (30, 30), 20, color, -1)
        cv2.imshow("OpenCV Feed", frame)

    def draw_text(
        self,
        frame,
        font=cv2.FONT_HERSHEY_COMPLEX,
        font_scale=1.0,
        font_thickness=2,
        offset=int(HEIGHT * 0.02),
        bg_color=(245, 242, 176, 0.85),
        text_color=(118, 62, 37)
    ):
        # Set window width based on aspect ratio of input frame
        window_w = int(HEIGHT * len(frame[0]) / len(frame))

        # Get size of text
        (text_w, text_h), _ = cv2.getTextSize(
            self.sign_detected, font, font_scale, font_thickness
        )

        # Set text position at center of window
        text_x, text_y = int((window_w - text_w) / 2), HEIGHT - text_h - offset

        # Draw background rectangle
        cv2.rectangle(frame, (0, text_y - offset), (window_w, HEIGHT), bg_color, -1)

        # Draw text
        cv2.putText(
            frame,
            self.sign_detected,
            (text_x, text_y + text_h + int(font_scale) - 1),
            font,
            font_scale,
            text_color,
            font_thickness,
        )


        return frame


    @staticmethod
    def draw_landmarks(image, results):
        mp_holistic = mp.solutions.holistic  # Holistic model
        mp_drawing = mp.solutions.drawing_utils  # Drawing utilities

        # Draw left hand connections
        mp_drawing.draw_landmarks(
            image,
            landmark_list=results.left_hand_landmarks,
            connections=mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=1),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=1),
        )
        
        # Draw right hand connections
        mp_drawing.draw_landmarks(
            image,
            landmark_list=results.right_hand_landmarks,
            connections=mp_holistic.HAND_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=1),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=1),
        )
        
        
        # Draw pose connections
        mp_drawing.draw_landmarks(
            image,
            landmark_list=results.pose_landmarks,
            connections=mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(128,128,128), thickness=2, circle_radius=1),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(128,128,128), thickness=2, circle_radius=1),
        )

       


        
        
    
    #return image

