import io
from flask import Flask, jsonify, render_template, Response, request
import cv2
import mediapipe as mp
import numpy as np
import time
from utils.dataset_utils import load_dataset, load_reference_signs
from utils.mediapipe_utils import *
from sign_recorder import SignRecorder
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, abort
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant, ChatGrant
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from flask_cors import CORS
import pyttsx3

engine = pyttsx3.init()

load_dotenv()
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_api_key_sid = os.environ.get('TWILIO_API_KEY_SID')
twilio_api_key_secret = os.environ.get('TWILIO_API_KEY_SECRET')
twilio_client = Client(twilio_api_key_sid, twilio_api_key_secret,
                       twilio_account_sid)

app = Flask(__name__,template_folder='template')
CORS(app)

socketio = SocketIO(app)

# load the dataset and create a DataFrame of reference signs
videos = load_dataset()
reference_signs = load_reference_signs(videos)

# create an object that stores Mediapipe results and computes sign similarities
sign_recorder = SignRecorder(reference_signs)


camera_on = True

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 25)  # Set frame rate to 10 FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 375)  # Set input resolution to 320x240
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 375)

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

def draw_landmarks(image, results):
    # Draw hand landmarks
    mp_drawing.draw_landmarks(
        image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS
    )
    mp_drawing.draw_landmarks(
        image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS
    )
    return image



# def recognize_sign(results):
#     #results = sign_recorder.process(image)
    
#     # Get the recognized sign
#     sign = sign_recorder.process_results(results)
    
#     # Return the recognized sign as a response
#     return sign


def get_chatroom(name):
    for conversation in twilio_client.conversations.conversations.stream():
        if conversation.friendly_name == name:
            return conversation


    # a conversation with the given name does not exist ==> create a new one
    return twilio_client.conversations.conversations.create(
        friendly_name=name)


@app.route('/login', methods=['POST'])
def login():
    username = request.get_json(force=True).get('username')
    if not username:
        abort(401)

    conversation = get_chatroom('My Room')
    try:
        conversation.participants.create(identity=username)
    except TwilioRestException as exc:
        # do not error if the user is already in the conversation
        if exc.status != 409:
            raise

    token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=username)
    token.add_grant(VideoGrant(room='My Room'))
    token.add_grant(ChatGrant(service_sid=conversation.chat_service_sid))

    return {'token': token.to_jwt(),
            'conversation_sid': conversation.sid}


def gen_frames():
    with mp_holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        is_recording = False
        is_paused = False
        start_time = time.time()
        
        while True:
            
            # Capture frame from camera
            success, frame = cap.read()
            if not success:
                break

            # Convert the image from BGR to RGB
            image, results = mediapipe_detection(frame, holistic)

            # Draw the landmarks on the image
            image = draw_landmarks(frame, results)

            # Recognize the sign from the image
            sign_detected = sign_recorder.process_results(results)

            # Convert sign_label to string
            sign_detected_str = str(sign_detected)

            # Inside the while loop
            

            # Speak the sign_detected string
            engine.say(sign_detected_str)
            engine.runAndWait()

            

            # Draw the sign label on the image
            font = cv2.FONT_HERSHEY_SIMPLEX
            bottom_left_corner = (10, 30)
            font_scale = 1
            font_color = (0, 0, 255)
            line_type = 2
            cv2.putText(
                image,
                sign_detected_str,
                bottom_left_corner,
                font,
                font_scale,
                font_color,
                line_type,
            )

            # Encode the image as JPEG
            ret, jpeg = cv2.imencode(".jpg", image)

            # Convert the JPEG data to bytes
            frame = jpeg.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
            if (
                
                not is_recording
                and time.time() - start_time >= 5
            ):
                sign_recorder.record()
                start_time = time.time()

            elapsed_time = time.time() - start_time
            if elapsed_time < 0.1:
                time.sleep(0.1 - elapsed_time) 



@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected with a socket on server.')
    emit('connect')

# Socket event to join a chat room
@socketio.on('join_room', namespace='/test')
def handle_join_room(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('join_room_response', {'username': username, 'room': room}, room=room)

@socketio.on('leave_room', namespace='/test')
def handle_leave_room(data):
    room = data['room']
    leave_room(room)

@app.route('/')
def home():
    return render_template("frontend.html")

@app.route('/room/<uuid>')
def index(uuid):
    return render_template("video.html")



@app.route('/frontend')
def frontend():
    return render_template("frontend.html")

@app.route('/videocall')
def videocall():
    return render_template("videocall.html")


@app.after_request
def after_request(response):
    # Make the request object available globally
    global request
    return response
import base64

# @app.route('/video_feed', methods=['POST'])
# def video_feed():
#     image_data = request.json['imageData']
#     print(image_data)
#     # Process the image data with OpenCV here
#     return 'success'
    # if frame_data is not None:
    #     # Decode the base64-encoded JPEG data
    #     data = frame_data.split(',')[1].encode('utf-8')
    #     jpeg_bytes = base64.b64decode(data)

    #     # Convert the JPEG data to a numpy array
    #     frame = cv2.imdecode(np.frombuffer(jpeg_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)

    #     # Process the frame using OpenCV
    #     # ...
    #     return frame
    # # Return an empty HTTP response
    # return ('', 204)

@app.route('/video_feed')
def video_feed():
    response = Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  
    return response

# @app.route('/video_feed', methods=['POST'])
# def video_feed():
#     with mp_holistic.Holistic(
#         min_detection_confidence=0.5, min_tracking_confidence=0.5
#     ) as holistic:
#         is_recording = True
#         is_paused = False
#         start_time = time.time()

#         while True:
#             # Get the frame from the frontend
#             frame = request.json['imageData']
#             print(frame)

#             # Convert the image from JPEG bytes to numpy array
#             frame = np.frombuffer(frame.encode('utf-8'), np.uint8)
#             frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

#             # Convert the image from BGR to RGB
#             image, results = mediapipe_detection(frame, holistic)

#             # Draw the landmarks on the image
#             image = draw_landmarks(frame, results)

#             # Recognize the sign from the image
#             sign_detected = sign_recorder.process_results(results)

#             # Convert sign_label to string
#             sign_detected_str = str(sign_detected)

#             # Draw the sign label on the image
#             font = cv2.FONT_HERSHEY_SIMPLEX
#             bottom_left_corner = (10, 30)
#             font_scale = 1
#             font_color = (0, 0, 255)
#             line_type = 2
#             cv2.putText(
#                 image,
#                 sign_detected_str,
#                 bottom_left_corner,
#                 font,
#                 font_scale,
#                 font_color,
#                 line_type,
#             )

#             # Encode the image as JPEG
#             ret, jpeg = cv2.imencode(".jpg", image)

#             # Convert the JPEG data to bytes
#             frame = jpeg.tobytes()

#             yield Response(
#                 b"--frame\r\n"
#                 b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n",
#                 mimetype='multipart/x-mixed-replace; boundary=frame'
#             )

#             elapsed_time = time.time() - start_time
#             if elapsed_time < 10:
#                 continue
#             else:
#                 break


@app.route('/video_feed2')
def video_feed2():
    response = Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  
    # room = input['room']
    # for video_frame in gen_frames(): 
        # emit('out-image-event', {'image_data': video_frame},  namespace='/test', include_self=False)
    return response

# @app.route('/start_recording')
# def start_recording():
#     global is_recording
#     is_recording = True
#     return "Sign recording started"

# @app.route('/stop_recording')
# def stop_recording():
#     global is_recording
#     is_recording = False
#     return "Sign recording stopped"


@app.route('/camera_on')
def camera_on_route():
    global camera_on
    camera_on = True
    return "Camera On"

@app.route('/camera_off')
def camera_off_route():
    global camera_on
    camera_on = False
    return "Camera Off"

if __name__ == "__main__":
    app.run(debug=True)
