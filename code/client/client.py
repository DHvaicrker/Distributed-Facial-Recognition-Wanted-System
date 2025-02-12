from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivymd.app import MDApp
import socket
import ssl
import pickle
from geopy.geocoders import Nominatim
import threading
import face_recognition
import cv2
import numpy as np
import time
import os
from captcha.image import ImageCaptcha
import sqlite3
import string
import random

SERVER_HOST = '192.168.1.90'
SERVER_PORT = 60000
Window.size = (800, 600)
# disable the fullscreen button
Window.borderless = '1'

# disable the close button
Window.borderless = '0'


def face_recogintion(client):
    """reciving the client socket and detecet all of the wanted faces that will appear on the camera video. if a
    wanted is detected sending a msg to the server """
    while True:

        if len(known_face_encodings) > 0 and len(known_face_names) > 0:

            face_locations = []
            Detected_names = []
            process_this_frame = True
            # video_capture = cv2.VideoCapture(1)
            while True:
                try:
                    scale = 10
                    # Grab a single frame of video

                    ret, frame = video_capture.read()
                    if not ret:
                        break
                    height, width, channels = frame.shape
                    # the zoom part:
                    centerX, centerY = int(height / 2), int(width / 2)  # coordinates of the center of the frame.
                    radiusX, radiusY = int(scale * height / 100), int(
                        scale * width / 100)  # the desired scale of the zoom - how many rows and columns to take from the center of the frame
                    # the boundaries of the cropped image based on the center and radius:
                    minX, maxX = centerX - radiusX, centerX + radiusX
                    minY, maxY = centerY - radiusY, centerY + radiusY
                    # the  original frame within the boundaries - (minX:maxX, minY:maxY)
                    #  i tell it from what x to what x the new frame will be and the same for the y:
                    cropped = frame[minX:maxX, minY:maxY]  # crop the image - shrink it
                    frame = cv2.resize(cropped, (width,
                                                 height))  # here the zoom affect happen - make the crop img on the orignile frame size - we stretch the image.
                    frame = cv2.flip(frame, 1)  # mirorr the frame not neccesary for face recognition
                    # Only process every other frame of video to save time
                    if process_this_frame:
                        # resize frame of video to 1/4 size for faster face recognition processing
                        # the smalller the frame is the faster face recognition processing will be.
                        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                        # convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                        rgb_small_frame = small_frame[:, :, ::-1]#the code uses NumPy array slicing. The [:, :, ::-1] slice operation is applied to reverse the order of the color channels, swapping the blue and red channels.

                        # Find all the faces in the current frame of video
                        face_locations = face_recognition.face_locations(
                            rgb_small_frame)  # Returns an 2d array of bounding boxes of human faces in a image using the CNN face detector
                        # cnn detector - CNN face detector works by taking an input image and running it through a deep
                        # neural network specifically designed for detecting faces. The network is trained on a large
                        # dataset of labeled face images to learn patterns and features that are indicative of a face.
                        # The network outputs a set of bounding boxes that indicate the location and size of the detected
                        # faces in the input image.
                        face_encodings = face_recognition.face_encodings(rgb_small_frame,
                                                                         face_locations)  # return a list of 128-dimension face encoding for each face in the image.

                        Detected_names = []

                        if not (len(known_face_encodings) > 0 and len(known_face_names) > 0):

                            break
                        with lock:
                            for face_encoding in face_encodings:
                                # See if the face is a match for the known face(s)
                                matches = face_recognition.compare_faces(known_face_encodings,
                                                                         face_encoding,
                                                                         tolerance=0.6)  # Compare a list of face encodings against a candidate encoding to see if they match.
                                # returns a list of true and false - true there is a face that match, false no match
                                if True in matches:  # if a match was found between the current face and the other faces:
                                    # now what we will do is find the closest match the face that is the most similar

                                    # Given a list of face encodings, compare them to a known face encoding and get a
                                    # euclidean distance(the distance between two points) for each comparison face. The
                                    # distance tells you how similar the faces are.return a numpy ndarray(it is similar
                                    # to a list or a Python array, but unlike them, NumPy ndarrays can hold data of
                                    # different types, including numbers, characters, and even other Python objects.)
                                    # with the distance for each face in the same order as the 'known_face_encodings' list:
                                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                                    best_match_index = np.argmin(
                                        face_distances)  # return the index of the min distace so the similarity are the closes.
                                    # It is used to find the index of the minimum element in a NumPy array
                                    # so best_match_index is give me the most similaar face but it might be that the  the minunimu - the closet face is not a match at all is not similar at all thats why i checked if there are True in matches

                                    if matches[best_match_index]:

                                        name = known_face_names[best_match_index]  # get the name
                                        Detected_names.append(name)

                    process_this_frame = not process_this_frame

                    # Display the results
                    for (top, right, bottom, left), name in zip(face_locations, Detected_names):
                        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4

                        # Draw a box around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 0), 2)
                        # (image, start_point, end_point, color, thickness)
                        # Draw a label with a name below the face
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 0), cv2.FILLED)

                        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 1)
                        #(image, text, the coordinates of the bottom-left corner of the text string in the image, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
                        send_data_by_protocol(client, ["DETECTED",name])

                    # Display the resulting image
                    cv2.imshow('face recognition video', frame)

                    cv2.waitKey(1) # adding a delay of a 0.001 seconds
                except ConnectionRefusedError:
                    print("closing connection- the server is closed")
                    cv2.destroyAllWindows()
                    client.close()
                    os._exit(0)
                    return
                except:
                    print("closing connection")
                    cv2.destroyAllWindows()
                    client.close()
                    os._exit(0)




        else:

            cv2.destroyAllWindows()
            time.sleep(2)


def print_crt(c):
    """reciving the TLS certificate and printing it"""
    print(f"Certificat Name : {c['subject'][5][0][1]}")
    print(f"Issuer name : {c['issuer'][0][0][1]}")

    a = len(c['subjectAltName'])
    for i in range(a):
        print(f"Server Domain / IP : {c['subjectAltName'][i]}")

    print(f"Expairy Date : {c['notAfter']}")
    print(f"Serial Number : {c['serialNumber']}")


def send_data_by_protocol(client, data):
    """reciving the client socket and the data to transfer and create message by the protocol - data size with max len
    of 10 digits and then data himself """
    try:
        HEADERSIZE = 10

        data = pickle.dumps(data)
        msg = bytes(f"{len(data):<{HEADERSIZE}}", 'utf-8') + data
        print(msg)
        client.send(msg)
    except Exception as error:
        print(error)
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)


def recive_by_protocol(client):
    """reciving the client socket and return the msg"""
    try:
        HEADERSIZE = 10
        full_msg = b''
        new_msg = True
        while True:
            msg = client.recv(2048)
            if new_msg:
                print("new msg len:", msg[:HEADERSIZE])
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg

            if len(full_msg) - HEADERSIZE == msglen:
                print("full msg recvd")
                finale_msg = pickle.loads(full_msg[HEADERSIZE:])
                break

        return finale_msg
    except ConnectionRefusedError:
        print("closing connection- the server is closed")
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)
    except Exception as error:
        print(error)

        os._exit(0)


def delete_wanted(name):
    with lock:
        conn = sqlite3.connect(r'database/client_db.db')

        # Create a cursor object

        c = conn.cursor()
        c.execute(f"DELETE FROM wanted_info WHERE name = '{name}'")
        c.execute("COMMIT")
        conn.close()


        inddex = known_face_names.index(name)

        known_face_names.remove(name)

        known_face_encodings.pop(inddex)


    print(f"The Wanted {name} was deleted from the list")
def add_wanted(server_req):

    with lock:
        # the name                     #the picture
        conn = sqlite3.connect(r'database/client_db.db')
        # Create a cursor object
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO wanted_info VALUES (?,?)",
                       (server_req[1], server_req[2]))
        cursor.execute("COMMIT")
        conn.close()

        img_numpy_arr = cv2.imdecode(np.frombuffer(server_req[2], np.uint8),
                                     1)  # Load the img file into a numpy array
        # Get the face encodings for each face in each image file
        # But since I know each image only has one face, I only care about the first encoding in each image, so I grab index 0.
        not_add =True
        while not_add:# somtimes it scan the frame and it doesnt find a face but since i know there must be a face because the server checked it.
            try:
                face_encoding = face_recognition.face_encodings(img_numpy_arr)[0]
                known_face_encodings.append(face_encoding)
                not_add = False
            except:
                pass
        known_face_names.append(server_req[1])

    print(f"The Wanted {server_req[1]} was added to the list")
def handle_server_req(client):
    """reciving the client socket and doing the server requests"""

    try:
        while True:
            server_req = recive_by_protocol(client)

            if server_req:
                print(server_req[0])
                if server_req[0] == "DELETE":

                    name = ' '.join(str(e) for e in server_req[1::])
                    t = threading.Thread(target=delete_wanted,args=(name,))
                    t.start()

                elif server_req[0] == "ADD":
                    t = threading.Thread(target=add_wanted, args=(server_req,))
                    t.start()
                    pass
                elif server_req == "EXIT":
                    client.close()
                    Window.close()
                    os._exit(0)
                    pass
    except Exception as error:
        print(error)
        os._exit(0)
    except ConnectionRefusedError:
        print("closing connection- the server is closed")
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)


def main():
    """starting the threads"""


    try:

        handle_thread = threading.Thread(name='handle_thread', target=handle_server_req, args=(client,), daemon=True)
        face_recogintion_thread = threading.Thread(name='face_recogintion_thread', target=face_recogintion,
                                                   args=(client,),
                                                   daemon=True)

        handle_thread.start()
        face_recogintion_thread.start()

        handle_thread.join()
        face_recogintion_thread.join()
    except Exception as error:
        print(error)
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)


class LoginScreen(Screen):
    pass


class Client(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_attemps = 4
        self.current_attemp = 1

    def get_cam_loc(self):
        """reciving the camera location from the ui """
        try:
            global camera_loc
            # Initialize Nominatim API
            geolocator = Nominatim(user_agent="Global_Watch")

            cam_location_name = self.root.ids.login.ids.loc.text
            cam_location = geolocator.geocode(cam_location_name)
            if cam_location:
                # entering the location name

                print(cam_location.address)

                # printing latitude and longitude
                print(f"Latitude =  {cam_location.latitude} ")
                print(f"Longitude =  {cam_location.longitude}")
                camera_loc = [cam_location.latitude, cam_location.longitude]
                return True

            else:
                self.root.ids.login.ids.loc.helper_text = "Enter a real place"
                self.root.ids.login.ids.loc.error = True
                print("Enter a real place")
        except Exception as error:
            print(error)
            cv2.destroyAllWindows()
            client.close()
            os._exit(0)

    def not_a_bot_check(self):
        """captcha check"""
        try:
            if not self.current_attemp > self.max_attemps:

                user_input_str = self.root.ids.login.ids.captcha.text

                if user_input_str == captcha_text:
                    print("great - in a few seconds you will connect to the system")
                    return True
                self.root.ids.login.ids.captcha.helper_text = f"wrong -  you have {self.max_attemps - self.current_attemp} attemps"
                print(f"wrong -  you have {self.max_attemps - self.current_attemp} attemps")
                self.current_attemp += 1
                self.root.ids.login.ids.captcha.error = True

                return False
            Client().stop()
            Window.close()
            os._exit(0)
        except Exception as error:
            print(error)
            cv2.destroyAllWindows()
            client.close()
            os._exit(0)

    def on_start(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.accent_palette = "Red"

    def get_font_size(self, screen):
        if screen == "login":
            return Window.size[0] / 35
        elif screen == "wanted":
            return Window.size[0] / 8
        elif screen == "wanted_label":
            return Window.size[0] / 35

    def login(self):
        """checking if all of the login detail are correct"""
        try:
            IS_NOT_BOT = self.not_a_bot_check()
            IS_REAL_PLACE = self.get_cam_loc()
            if IS_NOT_BOT and IS_REAL_PLACE:
                Client().stop()
                Window.close()
        except Exception as error:
            print(error)
            cv2.destroyAllWindows()
            client.close()
            os._exit(0)

    def close(self):
        try:
            Client().stop()
            Window.close()
            os._exit(0)
        except Exception as error:
            print(error)
            cv2.destroyAllWindows()
            client.close()
            os._exit(0)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    """create a unique string for the captcha"""
    return ''.join(random.choice(chars) for _ in range(size))


def delete_previus_run_database():
    """delete the previous database of the watneds"""
    try:
        Data_base_Folder_path = r"database/client_db.db"
        if os.path.exists(Data_base_Folder_path):
            os.remove(Data_base_Folder_path)
            print("Deleted '%s' file successfully" % Data_base_Folder_path)
    except Exception as error:
        print(error)
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)


def check_if_camera_avaiable():
    """check if there are any available cameras on the machine the code is running"""
    try:
        for i in range(5):
            video_capture = cv2.VideoCapture(i)
            ret, frame = video_capture.read()
            if ret:
                #video_capture.set(cv2.CAP_PROP_FPS, 5)
                return video_capture
            print(i)
        # if we are here it means that there is no camera aviable
        print("no camera aviable")
        os._exit(0)
    except Exception as error:
        print(error)
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)


def connect_to_server():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client = ssl.wrap_socket(
            client,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            do_handshake_on_connect=True,
            cert_reqs=ssl.CERT_REQUIRED,
            ca_certs=r'certificate\rootCA.crt',
        )

        print(client.context.protocol)

        try:
            client.connect((SERVER_HOST, SERVER_PORT))
            print(f' SSL passed : {ssl.SSLError}')
            crt = client.getpeercert()
            print_crt(crt)
        except ConnectionRefusedError:
            print("closing connection- the server is closed")
            cv2.destroyAllWindows()
            client.close()
            os._exit(0)




        print(f'[CLIENT CONNECTED TO {SERVER_HOST}:{SERVER_PORT}...')
        return client
    except:
        print("error connecting to the server")
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)


def create_database():
    """create the images database of all the wanteds"""
    try:
        with open('database/client_db.db', 'wb') as f:
            f.write(database_of_wanteds)

        conn = sqlite3.connect("database/client_db.db")
        cursor = conn.cursor()
        # execute a query to select data from the database
        cursor.execute('SELECT * FROM wanted_info')
        cursor.row_factory = sqlite3.Row
        # iterate over the rows of the result set
        for row in cursor:
            # convert row to a list
            row_list = list(row)
            img_numpy_arr = cv2.imdecode(np.frombuffer(row_list[1], np.uint8), 1)
            face_encoding = face_recognition.face_encodings(img_numpy_arr)[0]
            known_face_encodings.append(face_encoding)
            known_face_names.append(row_list[0])
        print(f"Recived the database with - {len(known_face_names)} wanteds")
        print("face recognition lists are set!")
        conn.close()
    except Exception as error:
        print(error)
        cv2.destroyAllWindows()
        client.close()
        os._exit(0)


if __name__ == "__main__":

    try:
        lock = threading.Lock()
        delete_previus_run_database()
        image = ImageCaptcha(width=280, height=90)
        camera_loc = []
        # Image captcha text
        captcha_text = id_generator()
        print(captcha_text)
        # generate the image of the given text
        data = image.generate(captcha_text)

        image.write(captcha_text, 'CAPTCHA.png')
        Client().run()# run the gui

        video_capture = check_if_camera_avaiable()
        client = connect_to_server()

        send_data_by_protocol(client, camera_loc)  # sending the camrea location
        database_of_wanteds = recive_by_protocol(client)
        print("database was received!")
        known_face_encodings = []
        known_face_names = []
        create_database()
    except Exception as error:
        print(error)



    main()
