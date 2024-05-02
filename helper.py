from ultralytics import YOLO
import time
import streamlit as st
import cv2
from pytube import YouTube
import os
import shutil
import settings
import glob



def load_model(model_path):
    """
    Loads a YOLO object detection model from the specified model_path.

    Parameters:
        model_path (str): The path to the YOLO model file.

    Returns:
        A YOLO object detection model.
    """
    model = YOLO(model_path)
    return model


def display_tracker_options():
    display_tracker = st.radio("Display Tracker", ('Yes', 'No'))
    is_display_tracker = True if display_tracker == 'Yes' else False
    if is_display_tracker:
        tracker_type = st.radio("Tracker", ("bytetrack.yaml", "botsort.yaml"))
        return is_display_tracker, tracker_type
    return is_display_tracker, None


def _display_detected_frames(conf, model, st_frame, image, is_display_tracking=None, tracker=None):
    """
    Display the detected objects on a video frame using the YOLOv8 model.

    Args:
    - conf (float): Confidence threshold for object detection.
    - model (YoloV8): A YOLOv8 object detection model.
    - st_frame (Streamlit object): A Streamlit object to display the detected video.
    - image (numpy array): A numpy array representing the video frame.
    - is_display_tracking (bool): A flag indicating whether to display object tracking (default=None).

    Returns:
    None
    """
    # Specify the directory from which to delete subdirectories
    directory = "runs/detect"

    # Iterate over all entries in the directory
    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        
        # Check if the entry is a directory
        if os.path.isdir(path):
            # Remove the subdirectory
            shutil.rmtree(path)
    # Resize the image to a standard size
    image = cv2.resize(image, (720, int(720*(9/16))))

    # Display object tracking, if specified
    if is_display_tracking:
        res = model.track(image, conf=conf, persist=True, tracker=tracker, save=True, name='predict')
    else:
        # Predict the objects in the image using the YOLOv8 model
        res = model.predict(image, conf=conf, save=True, name='predict')

    # # Plot the detected objects on the video frame
    res_plotted = res[0].plot()
    st_frame.image(res_plotted,
                   caption='Detected Video',
                   channels="BGR",
                   use_column_width=True
                   )
    return res[0].boxes.cls

def play_youtube_video(conf, model):
    """
    Plays a webcam stream. Detects Objects in real-time using the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    st.sidebar.write("example link 1: https://youtu.be/3F6GsMESbDc")
    # st.sidebar.write("example link 1: https://youtu.be/3F6GsMESbDc")
    source_youtube = st.sidebar.text_input("YouTube Video url")
    
    is_display_tracker, tracker = display_tracker_options()

    if st.sidebar.button('Detect Drowing'):
        try:
            dcls = []
            s = time.time() 
            yt = YouTube(source_youtube)
            stream = yt.streams.filter(file_extension="mp4", res=720).first()
            vid_cap = cv2.VideoCapture(stream.url)

            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    n = time.time()
                    detectCls = _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                    try: 
                        if n-s > settings.timeout:
                            s = n
                            from collections import Counter
                            element_counts = Counter(dcls)
                            if max(element_counts, key=element_counts.get) == 0:
                                st.write("Drowning, sending distress signal!")
                                # audio_file = open(settings.AUDIO_PATH, 'rb')
                                # audio_bytes = audio_file.read()
                                # st.audio(audio_bytes, format='audio/mp4a')
                                autoplay_audio(settings.AUDIO_PATH)
                                send_message()
                            dcls.clear()
                            
                        dcls.append(int(detectCls))
                        # print(dcls)
                    except:
                        print(detectCls)
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))


def play_rtsp_stream(conf, model):
    """
    Plays an rtsp stream. Detects Objects in real-time using the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    source_rtsp = st.sidebar.text_input("rtsp stream url:")
    st.sidebar.caption('Example URL: rtsp://admin:12345@192.168.1.210:554/Streaming/Channels/101')
    is_display_tracker, tracker = display_tracker_options()
    if st.sidebar.button('Detect Drowing'):
        s = time.time()
        dcls = []
        try:
            vid_cap = cv2.VideoCapture(source_rtsp)
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    n = time.time()
                    detectCls = _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                    try: 
                        if n-s > settings.timeout:
                            s = n
                            from collections import Counter
                            element_counts = Counter(dcls)
                            if max(element_counts, key=element_counts.get) == 0:
                                st.write("Drowning, sending distress signal!")
                                # audio_file = open(settings.AUDIO_PATH, 'rb')
                                # audio_bytes = audio_file.read()
                                # st.audio(audio_bytes, format='audio/mp4a')
                                autoplay_audio(settings.AUDIO_PATH)
                                send_message()
                            dcls.clear()
                            
                        dcls.append(int(detectCls))
                        # print(dcls)
                    except:
                        print(detectCls)
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video from RTSP: " + str(e))


def play_webcam(conf, model):
    """
    Plays a webcam stream. Detects Objects in real-time using the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    source_webcam = settings.WEBCAM_PATH
    is_display_tracker, tracker = display_tracker_options()
    if st.sidebar.button('Detect Drowing'):
        s = time.time()
        dcls = []
        try:
            vid_cap = cv2.VideoCapture(source_webcam)
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    n = time.time()
                    detectCls = _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                    try: 
                        if n-s > settings.timeout:
                            s = n
                            from collections import Counter
                            element_counts = Counter(dcls)
                            if max(element_counts, key=element_counts.get) == 0:
                                st.write("Drowning, sending distress signal!")
                                # audio_file = open(settings.AUDIO_PATH, 'rb')
                                # audio_bytes = audio_file.read()
                                # st.audio(audio_bytes, format='audio/mp4a')
                                autoplay_audio(settings.AUDIO_PATH)
                                send_message()
                                
                            dcls.clear()
                            
                        dcls.append(int(detectCls))
                        # print(dcls)
                    except:
                        print(detectCls)
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))


def play_stored_video(conf, model):
    """
    Plays a stored video file. Tracks and detects objects in real-time using the YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """
    source_vid = st.sidebar.selectbox(
        "Choose a video...", settings.VIDEOS_DICT.keys())

    is_display_tracker, tracker = display_tracker_options()

    with open(settings.VIDEOS_DICT.get(source_vid), 'rb') as video_file:
        video_bytes = video_file.read()
    if video_bytes:
        st.video(video_bytes)

    if st.sidebar.button('Detect Drowing'):
        s = time.time()
        dcls = []
        try:
            vid_cap = cv2.VideoCapture(
                str(settings.VIDEOS_DICT.get(source_vid)))
            st_frame = st.empty()
            while (vid_cap.isOpened()):
                success, image = vid_cap.read()
                if success:
                    n = time.time()
                    detectCls = _display_detected_frames(conf,
                                             model,
                                             st_frame,
                                             image,
                                             is_display_tracker,
                                             tracker
                                             )
                    try: 
                        if n-s > settings.timeout:
                            s = n
                            from collections import Counter
                            element_counts = Counter(dcls)
                            if max(element_counts, key=element_counts.get) == 0:
                                st.write("Drowning, sending distress signal!")
                                # audio_file = open(settings.AUDIO_PATH, 'rb')
                                # audio_bytes = audio_file.read()
                                # st.audio(audio_bytes, format='audio/mp4a')
                                autoplay_audio(settings.AUDIO_PATH)
                                send_message()
                                
                            dcls.clear()
                            
                        dcls.append(int(detectCls))
                        # print(dcls)
                    except:
                        print(detectCls)
                else:
                    vid_cap.release()
                    break
        except Exception as e:
            st.sidebar.error("Error loading video: " + str(e))
            
import base64
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )


from twilio.rest import Client
import requests
def send_message():
    print("\nsending distress signal")
    directory = "runs/detect/predict"
    img_path = glob.glob(os.path.join(directory, "*.jpg"))[0]
    print(img_path)
    api_key = settings.imgbb_api
    image_path = img_path

    with open(image_path, 'rb') as image_file:
        response = requests.post(
            'https://api.imgbb.com/1/upload',
            params={'key': api_key},
            files={'image': image_file}
        )

    if response.status_code == 200:
        media_path = response.json()['data']['url']
        try:
            account_sid = settings.account_sid
            auth_token = settings.auth_token
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                media_url=media_path,
                from_=f'whatsapp:{settings.from_}',
                body=f'{settings.alertmsg}',
                to=f'whatsapp:{settings.to_}'
            )
            print(message.sid)
        except Exception as e:
            print(f"error with Twilio {e}")
    else:
        print("Failed to upload image")