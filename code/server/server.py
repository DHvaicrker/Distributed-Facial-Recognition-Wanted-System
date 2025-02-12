from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from pygame import mixer
from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty
from kivy_garden.mapview import MapMarkerPopup
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
import sqlite3
import time
import random
import threading
import pickle
import os
import hashlib
import cv2
import ssl
import socket
import face_recognition
import pyttsx3

print(Window.size)
Window.size = (800, 600)
# disable the fullscreen button
Window.borderless = '1'

# disable the close button
Window.borderless = '0'


class CreateAccount(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.Data_base_path = r"databases/login.db"
        self.security_code = "123" # the secret security code

    def clear(self):
        """clear the screen"""
        self.ids.security_code.text = ""
        self.ids.psw_confirm.text = ""
        self.ids.psw.text = ""
        self.ids.generated_id.text = ""

    def Add_account(self):
        """check the user input and create the account and add it to the database"""
        data_status = True
        if self.security_code != self.ids.security_code.text:
            self.ids.security_code.error = True
            data_status = False
        if self.ids.psw.text != self.ids.psw_confirm.text:
            self.ids.psw.error = True
            data_status = False
            self.ids.psw_confirm.error = True
            self.ids.psw.helper_text = "you entered different passwords"
            self.ids.psw_confirm.helper_text = "you entered different passwords"
        if not (7 < len(self.ids.psw.text) < 13):
            data_status = False
            self.ids.psw.error = True
            self.ids.psw_confirm.error = True
            self.ids.psw.helper_text = "password length is not valid"
            self.ids.psw_confirm.helper_text = "password length is not valid"

        if data_status:
            # creating the id:
            try:
                id = random.randint(10000000, 100000001)# id = a uniuqe number in that range of numbers
                conn = sqlite3.connect(self.Data_base_path)
                c = conn.cursor()
                while True:
                    c.execute(f"SELECT id FROM agent_info WHERE id =  {id} ")
                    if not c.fetchone():  # empty result evaluates to False the id is not on the database which mean it is a new one.
                        print(f"created an a id{id} ")
                        break
                    else:
                        id = random.randint(10000000, 100000001)
                hash_id = hashlib.md5(str(id).encode()).hexdigest()
                hash_pass = hashlib.md5(str(self.ids.psw.text).encode()).hexdigest()
                c.execute(f"INSERT INTO agent_info VALUES (?,?)", (hash_id, hash_pass))
                c.execute("COMMIT")
                self.ids.generated_id.text = str(id)
                conn.close()
            except:
                os._exit(0)
        pass

    pass


class Map(Screen):

    def getTime(self, interval):
        """update the time label on the main screen"""
        self.ids.top_bar.title = time.asctime() + "      Map of Wanteds"

    def conn_secure(self):
        """creating a small box with text with the message -Connection secure"""


        toast("The connection is securely protected by TLS  and encryption")
    def __init__(self, **kwargs):
        self.play_song_bool = False
        super().__init__(**kwargs)

        Clock.schedule_interval(self.getTime, 1)

    def play_song(self):
        """play the song"""
        self.play_song_bool = not (self.play_song_bool)

        if self.play_song_bool:
            mixer.init()
            mixer.music.load(r'gui\songs\The_good_the_bad_and_the_ugly.mp3')
            mixer.music.play()
        else:

            mixer.music.stop()


class LoginScreen(Screen):

    def getTime(self, interval):
        """update the time label on the login screen"""
        self.ids.time.text = time.asctime()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Data_base_path = r"databases/login.db"
        Clock.schedule_interval(self.getTime, 1)

    def login(self):
        """check if the user is a subscriber and if he does let him in"""

        # 'or '1'='1 here is an example of a simple sql injection input_id = 'or '1'='1 id='{input_id}' => id= ''or
        # '1'='1' always true statement = f"SELECT id FROM agent_info WHERE id='{input_id}' AND Password = '{
        # input_psw}';"  statment that doesnt block sql injection
        input_id = self.ids.usrn.text
        input_psw = self.ids.psw.text
        input_id_hash = hashlib.md5(str(input_id).encode()).hexdigest()
        input_pass_hash = hashlib.md5(str(input_psw).encode()).hexdigest()
        try:
            conn = sqlite3.connect(self.Data_base_path)
            c = conn.cursor()

            c.execute(f"SELECT id FROM agent_info WHERE id=  ? AND Password = ?",
                      (input_id_hash, input_pass_hash))  # checking if the hash values are in the database

            if not c.fetchone():  # An empty result evaluates to False.
                print("Login failed")
                self.ids.usrn.error = True
                self.ids.psw.error = True

            else:
                print("Welcome")
                print(self.ids.usrn.text + "\n" + self.ids.psw.text)
                # fixing the bug with the MDFloatingActionButtonSpeedDial that WAS opening to the left and by changing the
                # screen dimension it will get back to the right side
                # you can delete it and see what happens
                self.manager.transition.direction = 'up'
                self.manager.transition.duration = 1
                self.manager.current = "Map"
                size = Window.size
                Window.size = (350, 650)
                Window.size = size
                # Window.maximize()
        except Exception as error:
            print(error)
            os._exit(0)


class HelpScreen(Screen):
    pass


class TakePicture(Screen):

    def __init__(self, **kwargs):
        super(TakePicture, self).__init__(**kwargs)

        # create camera object and start capture
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FPS, 30)

        # create kivy image object to display camera feed
        self.image = Image()

        # create kivy button object for capture
        self.capture_button = Button(text='Capture', size_hint=(1, 0.1), pos_hint={"center_x": 0.5})
        self.capture_button.bind(on_press=self.capture_image)

        self.return_button = Button(text='return', size_hint=(1, 0.1), pos_hint={"center_x": 0.5})
        self.return_button.bind(on_press=self.return_wanted_screen)
        # create a horizontal box layout for the image and capture button
        self.layout = BoxLayout(orientation='vertical')
        self.layout.add_widget(self.image)
        self.layout.add_widget(self.capture_button)
        self.layout.add_widget(self.return_button)

        # add layout to main layout
        self.add_widget(self.layout)

        # schedule update of camera frames 30 fps
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def return_wanted_screen(self, *args):
        """change the screen to the add wanted screen"""
        self.manager.transition.direction = 'up'
        self.manager.transition.duration = 1.1
        self.manager.current = 'AddWantedScreen'

    def update(self, *args):
        """update the frame in order to create a video"""
        # get the latest frame from the camera and convert to texture for display
        ret, frame = self.capture.read()

        if ret:
            frame = cv2.flip(frame, 0)  # flip the image verticaly
            frame = cv2.flip(frame, 1)  # flip it horizontaly
            buf = frame.tobytes()  # Convert the image to a byte format
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')  # copies the pixel data from the buf variable
            # into the texture's buffer, using the 'bgr' color format for both the input pixel data and the texture's
            # buffer format
            self.image.texture = texture

    def capture_image(self, *args):
        """save the captured image"""
        # get the latest frame from the camera and save as image
        try:
            ret, frame = self.capture.read()
            if ret:
                #resized_frame = resized_image = cv2.resize(frame, (0, 0), fx=0.25,fy=0.25)

                cv2.imwrite('captured_image.png', frame)
                MDApp.get_running_app().root.ids.AddWantedScreen.ids.picture_name.text = f"picture: {'captured_image.png'}"  # changing the image text at he wanted sceen
        except Exception as error:
            print(error)
            os._exit(0)

class AddWantedScreen(Screen):
    def __init__(self, **kwargs):
        self.path = ''
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path)

    def clear_picture_field(self):
        self.ids.picture_error.text = ""

    def open_file_manger(self):
        """opening the file manager ui"""
        self.file_manager.show(r'c:/')  # output manager to the screen at c: folder
        self.manager_open = True

    def select_path(self, path):
        '''it will be called when you click on the file name
        or the catalog selection button.
        path - the selected file path
        '''
        self.path = path
        self.exit_manager()
        toast(path)
        self.ids.picture_name.text = "picture: " + path

    def exit_manager(self, *args):
        '''called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()


class DeleteWanted(Screen):
    pass


class WantedsList(Screen):
    pass


class server(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.play_name = False
        self.engine = pyttsx3.init()
        self.dict_of_layouts = {}
        self.all_wanteds_info_dict = {}
        self.wanted_database_path = "databases/wanteds_pic_and_name.db"
        # Dictionary to keep track of SYN and ACK counts for each client
        self.syn_counts = {}
        self.ack_counts = {}
        self.detectd_dict = {}
        self.list_of_client_sockets = []
        self.tool_bar = DictProperty()
        self.path = ""
        self.tool_bar = {

            'Add  wanted': [
                'account-cowboy-hat',
                "on_press", lambda x: self.Add_wanted(),
            ],

            'Delete Wanted': [
                'account-remove',
                "on_press", lambda x: self.delete_wanted(),

            ],

            'wanted list': [
                'account-group',
                "on_press", lambda x: self.wanted_list(),

            ],
            'help': [
                'help-circle',
                "on_press", lambda x: self.Help(),

            ],
            'exit': [
                'application-export',
                "on_press", lambda x: self.closing_app(),

            ],

        }

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = ssl.wrap_socket(
            server,
            server_side=True,
            keyfile="certificate\server.key",
            certfile="certificate\server.crt",
            ssl_version=ssl.PROTOCOL_TLSv1_2
        )



    def check_if_human(self, file_path):

        """recive the image file path and return True or false according to the image
        check if a person face appear on the image(in order to the the face recognition the software need
        face. )"""
        image = face_recognition.load_image_file(file_path)

        if len(face_recognition.face_encodings(image)) == 1:  # only one face in the image
            return True
        return False

    def send_bounty(self):
        """check if the user input for the wanted are valid if they are add him to the databasae of wanteds and send to
        client """

        found_error = False

        if not self.root.ids.AddWantedScreen.ids.full_name.text:
            self.root.ids.AddWantedScreen.ids.full_name.helper_text = "you didn't entered a name"
            self.root.ids.AddWantedScreen.ids.full_name.error = True
            found_error = True
        if self.root.ids.AddWantedScreen.ids.full_name.text in self.all_wanteds_info_dict:
            self.root.ids.AddWantedScreen.ids.full_name.helper_text = "there is already someone with that name"
            self.root.ids.AddWantedScreen.ids.full_name.error = True
            found_error = True
        if not self.root.ids.AddWantedScreen.ids.crimes.text:
            self.root.ids.AddWantedScreen.ids.crimes.error = True
            self.root.ids.AddWantedScreen.ids.crimes.helper_text = "you didn't entered the crimes"
            found_error = True
        if not self.root.ids.AddWantedScreen.ids.bounty.text:
            self.root.ids.AddWantedScreen.ids.bounty.error = True
            self.root.ids.AddWantedScreen.ids.bounty.helper_text = "you didn't entered the bounty"
            found_error = True

        if not self.root.ids.AddWantedScreen.ids.danger_level.text:
            self.root.ids.AddWantedScreen.ids.danger_level.error = True
            self.root.ids.AddWantedScreen.ids.danger_level.helper_text = "you didn't entered the danger level"
            found_error = True

        if not self.root.ids.AddWantedScreen.ids.bounty.text.isdigit():
            self.root.ids.AddWantedScreen.ids.bounty.error = True
            self.root.ids.AddWantedScreen.ids.bounty.helper_text = "enter only numbers"
            found_error = True

        if not self.root.ids.AddWantedScreen.ids.danger_level.text.isdigit():
            self.root.ids.AddWantedScreen.ids.danger_level.error = True
            self.root.ids.AddWantedScreen.ids.danger_level.helper_text = "enter only numbers"
            return

        elif not 0 < int(self.root.ids.AddWantedScreen.ids.danger_level.text) <= 10:
            self.root.ids.AddWantedScreen.ids.danger_level.error = True
            self.root.ids.AddWantedScreen.ids.danger_level.helper_text = "the danger level is between 1-10"
            return

        if self.root.ids.AddWantedScreen.ids.picture_name.text == "picture:":
            self.root.ids.AddWantedScreen.ids.picture_error.text = "you didn't entered a picture"
            return

        try:
            from PIL import Image
            Image.open(str(self.root.ids.AddWantedScreen.ids.picture_name.text).split(": ")[1])


        except:
            self.root.ids.AddWantedScreen.ids.picture_error.text = "Wrong type of file"
            return
        image = cv2.imread(str(self.root.ids.AddWantedScreen.ids.picture_name.text).split(": ")[1])

        resized_image = cv2.resize(image, (0, 0), fx=0.25,
                                   fy=0.25)  # Resize the image to 1/4 of it size in order to reduce memory usage
        cv2.imwrite('captured_image.png', resized_image)


        if not self.check_if_human('captured_image.png'):
            self.root.ids.AddWantedScreen.ids.picture_error.text = "no face in the picture you chose or more than 2 face detected"
            self.root.ids.AddWantedScreen.ids.picture_name.text = "picture:"
            found_error = True


        if not found_error:
            bounty_req = self.root.ids.AddWantedScreen.ids.full_name.text + "\n" + self.root.ids.AddWantedScreen.ids.crimes.text + "\n" + self.root.ids.AddWantedScreen.ids.bounty.text + "\n" + self.root.ids.AddWantedScreen.ids.danger_level.text + "\n" + self.path
            print(bounty_req)
            try:
                new_path = f'wanted_images/{self.root.ids.AddWantedScreen.ids.full_name.text}_image.png'
                cv2.imwrite(new_path, image)
                self.all_wanteds_info_dict[self.root.ids.AddWantedScreen.ids.full_name.text] = [
                    new_path, self.root.ids.AddWantedScreen.ids.crimes.text,
                    self.root.ids.AddWantedScreen.ids.danger_level.text, self.root.ids.AddWantedScreen.ids.bounty.text]

                f = open("captured_image.png", 'rb')
                image_bytes = f.read()
                conn = sqlite3.connect(self.wanted_database_path)
                c = conn.cursor()

                c.execute(f"INSERT INTO wanted_info VALUES (?,?)",
                          (self.root.ids.AddWantedScreen.ids.full_name.text, image_bytes))
                c.execute("COMMIT")

                self.add_criminal(self.root.ids.AddWantedScreen.ids.full_name.text, image_bytes)

                self.add_wanted_to_screen_list(self.root.ids.AddWantedScreen.ids.full_name.text,
                                               new_path)
                self.root.transition.direction = 'down'
                self.root.transition.duration = 1
                self.root.current = 'Map'
                self.clear()
            except Exception as error:
                print(error)
                self.root.ids.AddWantedScreen.ids.picture_error.text = "Error occur! There is a problem with the data you provided, please try again."


    def add_wanted_to_screen_list(self, name, path):
        """get the name of the wanted and the image path
        and add the wanted to the list screen"""
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        layout = MDBoxLayout(id=name, orientation="horizontal")

        image = Image()

        # create texture from image file
        image_path = path
        image_data = cv2.imread(image_path)
        image_data = cv2.flip(image_data, 0)  # flip the image verticaly
        image_data = cv2.flip(image_data, 1)  # flip it horizontaly
        texture = Texture.create(size=(image_data.shape[1], image_data.shape[0]), colorfmt='bgr')
        texture.blit_buffer(image_data.tobytes(), colorfmt='bgr')

        # assign texture to image widget
        image.texture = texture

        name_label = MDLabel(text=name,
                             pos_hint={"x": 0, "center_y": 0.5},
                             size_hint=[1, 1], )
        dash_label = MDLabel(text=" - ",
                             pos_hint={"center_y": 0.5},
                             size_hint=[1, 1], )

        name_label.font_name = r"gui/fonts/WANTED2.ttf"
        dash_label.font_name = r"gui/fonts/WANTED2.ttf"
        name_label.font_size = self.get_font_size("wanted_list")
        dash_label.font_size = self.get_font_size("wanted_list")
        layout.add_widget(name_label)
        layout.add_widget(dash_label)
        layout.add_widget(image)

        layout_size = 300

        self.dict_of_layouts[name] = layout
        self.root.ids.WantedsList.ids.layout.add_widget(layout)
        self.root.ids.WantedsList.ids.layout.height = layout_size * len(self.dict_of_layouts)

    def clear(self):
        """clearing all the labels of the wanted page"""
        self.root.ids.AddWantedScreen.ids.full_name.text = ""
        self.root.ids.AddWantedScreen.ids.crimes.text = ""
        self.root.ids.AddWantedScreen.ids.bounty.text = ""

        self.root.ids.AddWantedScreen.ids.danger_level.text = ""
        self.root.ids.AddWantedScreen.ids.picture_name.text = "picture:"
        self.root.ids.AddWantedScreen.ids.picture_error.text = ""

        self.root.ids.AddWantedScreen.ids.full_name.error = False
        self.root.ids.AddWantedScreen.ids.crimes.error = False
        self.root.ids.AddWantedScreen.ids.bounty.error = False
        self.root.ids.AddWantedScreen.ids.danger_level.error = False

        self.path = ''

    def add_criminal(self, name, picture):

        """get the name of the wanted and his picture anf sending to the client a ADD message the add a wanted to his
        database """
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        print("sending picture to clients")
        for client in self.list_of_client_sockets:
            try:

                self.send_data_by_protocol(client, ['ADD', name, picture])

            except:
                try:
                    client.close()
                except:# the connection is already closed
                       pass
                finally:
                    self.list_of_client_sockets.remove(client)

    def remove_criminal(self, name):
        """get the name of the wanted remove a criminal from the database and sending a msg to the client to delete
        him """
        if name in self.all_wanteds_info_dict:
            self.all_wanteds_info_dict.pop(name)
            conn = sqlite3.connect(self.wanted_database_path)
            c = conn.cursor()
            c.execute(f"DELETE FROM wanted_info WHERE name = '{name}'")
            c.execute("COMMIT")
            conn.close()
            os.remove(rf"wanted_images/{name}_image.png")
            self.remove_wanted_from_screen_list(name)
            if name in self.detectd_dict:
                self.root.ids.map.ids.map_view.remove_widget(self.detectd_dict[name][0])
                self.detectd_dict.pop(name)
            self.root.ids.DeleteWanted.ids.status_label.text = "The wanted deleted successfully"
            for client in self.list_of_client_sockets:
                try:
                    self.send_data_by_protocol(client, ['DELETE', name])
                except:
                    try:
                        client.close()
                    except:  # the connection is already closed
                        pass
                    finally:
                        self.list_of_client_sockets.remove(client)

        else:
            self.root.ids.DeleteWanted.ids.status_label.text = "There is no wanted with that name"

    def remove_wanted_from_screen_list(self, name):
        """get the name of the wanted and remove the wanted's name from the list screen"""
        layout_size = 300
        layout = self.dict_of_layouts[name]
        self.root.ids.WantedsList.ids.layout.remove_widget(layout)
        self.dict_of_layouts.pop(name)
        self.root.ids.WantedsList.ids.layout.height = layout_size * len(self.dict_of_layouts)

    def send_data_by_protocol(self, connection, data_to_tranfer):
        """recive the sockect and the data.
        the protocol of communication between the server and the client"""
        HEADERSIZE = 10

        data = pickle.dumps(data_to_tranfer)
        # the msg according to the protocol - the length of the data is in the header and the maximum len is  number
        # with 10 digits and after the header comes the data itself
        msg = bytes(f"{len(data):<{HEADERSIZE}}", 'utf-8') + data
        connection.send(msg)

    def recv_by_protocol(self, client, addr):
        """recive the client socket and his addres and receiving msg by the protocol while defending against syn
        flood """
        HEADERSIZE = 10
        full_msg = b''
        new_msg = True
        while True:
            msg = client.recv(4096)
            if not msg:
                break

            if msg.startswith(b"\x16\x03"):
                # If this is a TLS handshake message, reset SYN and ACK counts for this client
                self.syn_counts[addr] = 0
                self.ack_counts[addr] = 0

            if msg[13] & 0x02:  # Check if packet is a SYN packet (SYN flag is set in 14th byte of TCP header)
                # If this is a SYN packet, increment SYN count for this client
                self.syn_counts[addr] = self.syn_counts.get(addr, 0) + 1
                print(f"SYN packet received from {addr} and this is count {self.syn_counts[addr]}")

            if msg[13] & 0x10:  # Check if packet is an ACK packet (ACK flag is set in 14th byte of TCP header)
                # AND between the binary number in msg[13] and 00010000
                # If this is an ACK packet, increment ACK count for this client
                self.ack_counts[addr] = self.ack_counts.get(addr, 0) + 1
                print(f"ACK packet received from {addr} and this is count {self.ack_counts[addr]}")

            if self.syn_counts.get(addr, 0) > 10 and self.ack_counts.get(addr, 0) < 2:
                # If SYN flood is detected for this client, terminate connection
                print(f"SYN flood detected from {addr}. Terminating connection.")
                # Remove SYN and ACK counts for this client
                del self.syn_counts[addr]
                del self.ack_counts[addr]
                self.list_of_client_sockets.remove(client)
                # Close the connection
                client.shutdown(socket.SHUT_RDWR)
                client.close()
                print(f"Connection with {addr} closed")
                return "CLOSE"

            if new_msg:
                print("new msg len:", msg[:HEADERSIZE])
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            print(f"full message length: {msglen}")

            full_msg += msg

            print(len(full_msg))

            if len(full_msg) - HEADERSIZE == msglen:
                print("full msg recvd")
                finale_msg = pickle.loads(full_msg[HEADERSIZE:])
                break
        return finale_msg

    def handle_client(self, connection, addr):
        """receive the client socket and his adders and wait for his messages and response accordingly"""
        camera_loc = ()
        self.syn_counts[addr] = 0
        self.ack_counts[addr] = 0
        recv_camera_loc = False
        # Receive data from the client and detect SYN flood
        while True:
            data = self.recv_by_protocol(connection, addr)
            if data == "CLOSE":
                return
            if not recv_camera_loc and isinstance(data, list):
                camera_loc = data

                with open('databases/wanteds_pic_and_name.db', 'rb') as f:
                    file_data = f.read()
                self.send_data_by_protocol(connection, file_data)
                recv_camera_loc = True
            else:
                client_req = data
                print(f"Received: {client_req}")
                if client_req[0] == "DETECTED":
                    conn = sqlite3.connect(self.wanted_database_path)
                    c = conn.cursor()

                    value = client_req[1]
                    c.execute('SELECT * FROM wanted_info WHERE name = ?', (value,))
                    # Check if any rows were returned
                    if c.fetchone():
                        wanted_name = value
                        if not self.play_name:
                            speak = threading.Thread(target=self.text_to_speach, args=(wanted_name + "was detected",))
                            speak.start()

                        self.add_wanteds_to_map(wanted_name, camera_loc)
                        print('Value exists in the database')
                    else:
                        print('Value does not exist in the database')

    def text_to_speach(self, text):
        """receive the text to talk and say it"""
        # say the name of the wanted
        self.play_name = True
        self.engine.say(text)
        self.engine.runAndWait()
        self.play_name = False


    def delete_files_in_directory(self,directory):
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
        except Exception as error:
            print(error)
            os._exit(0)


    def start_connection(self):
        """connecting to the clients and start the set up procces between the server and the client"""
        conn = sqlite3.connect(self.wanted_database_path)
        c = conn.cursor()
        c.execute("DELETE FROM wanted_info")  # clearing the database from the last run
        c.execute("COMMIT")
        self.delete_files_in_directory("wanted_images")
        SERVER_HOST = '192.168.1.90'
        SERVER_PORT = 60000
        self.server.bind((SERVER_HOST, SERVER_PORT))

        self.server.listen()
        print(f'[SERVER LISTEN ON {SERVER_HOST}:{SERVER_PORT}...')
        try:
            while True:
                connection, client_address = self.server.accept()
                self.list_of_client_sockets.append(connection)
                print(f'[SERVER CONNECTED TO {client_address}...')

                handle_thread = threading.Thread(name='handel', target=self.handle_client,
                                                 args=(connection, client_address,), daemon=True)
                handle_thread.start()
        except Exception as error:
            print(f"the socket has been closed {error}")
            os._exit(0)

    def build(self):
        """set the main colors for the gui and starting the thread for listening to clients"""
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        try:
            conn_thread = threading.Thread(name='conn_thread', target=self.start_connection, daemon=True)
            conn_thread.start()
        except Exception as error:
            print(error)
            os._exit(0)

    def create_wanted_layout(self, wanted_name):
        """receiving the wanted name and returning a layout of that wanted to put on the map"""
        wanted = self.all_wanteds_info_dict[wanted_name]
        layout = MDBoxLayout(size_hint=[4.6, 4.6], md_bg_color=[226 / 255, 188 / 255, 81 / 255, 0.58],
                             orientation='vertical')

        layout.add_widget(MDLabel(id="wanted",
                                  text="Wanted",
                                  pos_hint={"center_x": 0.6},
                                  theme_text_color="Custom",
                                  text_color=[34 / 255, 28 / 255, 16 / 255, 0.88],
                                  size_hint=[.3, .1]))

        # picture: c:/dvir.png
        layout.add_widget(Image(source=wanted[0], pos_hint={"center_x": .5}, size_hint=[.3, .3]))
        layout.add_widget(MDLabel(text="FULL NAME: " + wanted_name,
                                  id="name",
                                  pos_hint={"x": 0},
                                  theme_text_color="Custom",
                                  text_color=[34 / 255, 28 / 255, 16 / 255, 0.88],
                                  size_hint=[1, .1]))

        layout.add_widget(MDLabel(text="CRIMES: " + wanted[1],
                                  id="crimes",
                                  pos_hint={"x": 0},
                                  theme_text_color="Custom",
                                  text_color=[34 / 255, 28 / 255, 16 / 255, 0.88],
                                  size_hint=[1, .1]))

        layout.add_widget(MDLabel(text="DANGER LEVEL: " + wanted[2],
                                  id="danger",
                                  pos_hint={"x": 0},
                                  theme_text_color="Custom",
                                  text_color=[34 / 255, 28 / 255, 16 / 255, 0.88],
                                  size_hint=[1, .1]))
        layout.add_widget(MDLabel(text="BOUNTY: " + wanted[3],
                                  id="bounty",
                                  pos_hint={"x": 0},
                                  theme_text_color="Custom",
                                  text_color=[34 / 255, 28 / 255, 16 / 255, 0.88],
                                  size_hint=[1, .1]))

        return layout

    @mainthread  # In order to change the graphic you need to do that from the main thread
    def add_wanteds_to_map(self, wanted_name, camera_loc):
        """recive the camera location the wanted name and adding him to the map"""
        if wanted_name in self.detectd_dict:  # check if he already was detected
            if camera_loc == self.detectd_dict[wanted_name][1]:  # same pos
                return
            self.root.ids.map.ids.map_view.remove_widget(self.detectd_dict[wanted_name][0])
            self.detectd_dict.pop(wanted_name)
        wanted_to_delete = None
        for wanted in self.detectd_dict:  # check if there is someone at that place and delete him
            if camera_loc in self.detectd_dict[wanted]:
                self.root.ids.map.ids.map_view.remove_widget(self.detectd_dict[wanted][0])
                wanted_to_delete = wanted
        if wanted_to_delete:
            self.detectd_dict.pop(wanted_to_delete)

        marker = MapMarkerPopup(lat=camera_loc[0], lon=camera_loc[1], source="gui/images/criminal_icon.png")

        layout = self.create_wanted_layout(wanted_name)
        marker.add_widget(layout)
        self.detectd_dict[wanted_name] = (marker, camera_loc)
        self.root.ids.map.ids.map_view.add_widget(marker)

    def delete_wanted(self):
        """transfer to the remove-wanted screen"""
        self.root.transition.direction = 'up'
        self.root.transition.duration = 1.1
        self.root.current = 'DeleteWanted'

        pass

    def wanted_list(self):
        """transfer to the WANTED-LIST screen"""
        self.root.transition.direction = 'up'
        self.root.transition.duration = 1.1
        self.root.current = 'WantedsList'

    def closing_app(self):
        """"close the app and sending the clients a close msg"""
        for client in self.list_of_client_sockets:
            self.send_data_by_protocol(client, "EXIT")
            client.close()

        self.server.close()
        # removing window
        Window.close()
        os._exit(0)

    def Help(self):
        """transfer to the HELP screen"""
        self.root.transition.direction = 'up'
        self.root.transition.duration = 1.1
        self.root.current = 'HelpScreen'

    def Add_wanted(self):
        """transfer to the ADD-WANTED screen"""
        self.root.transition.direction = 'up'
        self.root.transition.duration = 1.1
        self.root.current = 'AddWantedScreen'

    def Take_picture(self):
        print(self.root.ids)
        """transfer to the TAKE-PICTURE screen"""
        self.root.transition.direction = 'up'
        self.root.transition.duration = 1.1
        self.root.current = 'TakePictureScreen'

    def return_main_menu(self):
        """transfer to the MAP screen"""
        self.root.transition.direction = 'down'
        self.root.transition.duration = 1.1
        self.root.current = 'Map'

    def get_resolution(self):
        """return the window resolution"""
        return Window.size

    def get_font_size(self, screen):
        """recive the screen type and returing a font size that match that screen"""
        if screen == "login":
            return Window.size[0] / 35
        elif screen == "wanted":
            return Window.size[0] / 8
        elif screen == "wanted_label":
            return Window.size[0] / 35
        elif screen == "wanted_list":
            return Window.size[0] / 14


if __name__ == "__main__":
    server().run()
