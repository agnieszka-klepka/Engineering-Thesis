import customtkinter
from tkinter import ttk
from tests.thirty_second_test import ThirtySecondsTest
from tests.squat_test import SquadTest
from functions import date_from_db, test_name_from_db, test_result_from_db
from PIL import Image
import os
from database import Database


class MainWindow(customtkinter.CTk):
    def __init__(self, user, **kwargs):
        super().__init__(**kwargs)

        self.title("Keep Your Balance - Aplikacja do badania równowagi")
        self.geometry(f"{1400}x{900}")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.user = user

        """
            ELEMENT create_sidebar => PASEK BOCZNY
            Wywoływana jest funkcja automatycznie po utworzeniu okna głównego aplikacji, zawiera 
            przyciski, dzięki którym można przejśc do poszczególnych elementów aplikacji, czyli 
            Strona główna, Badanie, O aplikajci.
        """
        self.create_sidebar()
        self.top_romberg_window = None
        self.top_berg_window = None
        self.top_squad_window = None

    def create_sidebar(self):
        self.sidebar_frame = customtkinter.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="KEEP YOUR BALANCE",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="STRONA GŁÓWNA",
                                                        command=self.main_page_button_event, corner_radius=0, width=170,
                                                        height=35)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="TEST ROMBERGA",
                                                        command=self.romberg_test_page_button_event, corner_radius=0,
                                                        width=170, height=35)
        self.sidebar_button_3.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, text="TEST BERG",
                                                        command=self.berg_test_page_button_event, corner_radius=0,
                                                        width=170, height=35)
        self.sidebar_button_5.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="WYNIKI",
                                                        command=self.results_page_button_event, corner_radius=0,
                                                        width=170, height=35)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_6 = customtkinter.CTkButton(self.sidebar_frame, text="KONIEC",
                                                        command=self.end_page_button_event, corner_radius=0,
                                                        width=170, height=35)
        self.sidebar_button_6.grid(row=8, column=0, padx=20, pady=10)

    def clear_current_view(self):
        for widget in self.grid_slaves(row=0, column=1):
            widget.destroy()

        self.sidebar_button_1.configure(fg_color="#4C7DBA", text_color="#FFFFFF")
        self.sidebar_button_3.configure(fg_color="#4C7DBA", text_color="#FFFFFF")
        self.sidebar_button_5.configure(fg_color="#4C7DBA", text_color="#FFFFFF")
        self.sidebar_button_4.configure(fg_color="#4C7DBA", text_color="#FFFFFF")

    # STRONA GŁÓWNA
    def main_page_button_event(self):
        self.clear_current_view()  # funkcja czyszcząca wigdety z głównego okna przed wgraniem następnej zakładki aplikacji
        self.sidebar_button_1.configure(fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)

        with open("assets/main_page.txt", "r") as file:
            main_page_content = file.read()

        textbox = customtkinter.CTkTextbox(self, width=250)
        textbox.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
        textbox.insert("0.0", main_page_content)

    # TEST ROMBERGA
    def romberg_test_page_button_event(self):
        self.clear_current_view()  # funkcja czyszcząca wigdety z głównego okna przed wgraniem następnej zakładki aplikacji
        self.sidebar_button_3.configure(fg_color="#FFFFFF", text_color="#4C7DBA",
                                        border_color="#4C7DBA", border_width=2)

        romberg_frame = customtkinter.CTkFrame(self, width=1800, corner_radius=0, fg_color="#F2F2F2")
        romberg_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        romberg_frame.grid_rowconfigure(0, weight=0, minsize=50)
        romberg_frame.grid_rowconfigure(1, weight=1, minsize=50)
        romberg_frame.grid_rowconfigure(2, weight=1, minsize=50)

        romberg_frame.grid_columnconfigure(0, weight=1, minsize=50)
        romberg_frame.grid_columnconfigure(1, weight=1, minsize=50)

        # rozmiar assetów
        IMAGE_WIDTH = 160
        IMAGE_HEIGHT = 200

        # BUTTON WYNIKI
        result_button = customtkinter.CTkButton(romberg_frame, text="WYNIKI",
                                                command=self.results_page_button_event, corner_radius=0,
                                                width=100, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                                border_color="#4C7DBA", border_width=2)
        result_button.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        # TEST 1
        frame1 = customtkinter.CTkFrame(romberg_frame, width=int(romberg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_rowconfigure(1, weight=1)
        frame1.grid_rowconfigure(2, weight=1)
        frame1.grid_rowconfigure(3, weight=1)
        frame1.grid_rowconfigure(4, weight=1)

        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(1, weight=1)

        IMAGE_PATH = 'assets/romberg_test/both-legs.png'

        image1 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i1 = customtkinter.CTkLabel(frame1, image=image1, text='')
        i1.grid(row=0, column=0, rowspan=5)

        label1 = customtkinter.CTkLabel(frame1, text="TEST 1",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label1.grid(row=0, column=1, pady=10, padx=10)

        text1 = customtkinter.CTkLabel(frame1,
                                       text="Test dotyczy stania na dwóch nogach. \n"
                                            "Czas trwania testu wynosi 30 sekund.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.\n",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text1.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button1 = customtkinter.CTkButton(frame1, text="OTWÓRZ",
                                          command=lambda: self.start_romeberg_test("both-legs_standing"),
                                          corner_radius=0,
                                          width=75, height=15, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button1.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        # TEST 2
        frame2 = customtkinter.CTkFrame(romberg_frame, width=int(romberg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_rowconfigure(1, weight=1)
        frame2.grid_rowconfigure(2, weight=1)
        frame2.grid_rowconfigure(3, weight=1)
        frame2.grid_rowconfigure(4, weight=1)

        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_columnconfigure(1, weight=1)

        IMAGE_PATH_2 = 'assets/romberg_test/hands-up.png'

        image2 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH_2)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i2 = customtkinter.CTkLabel(frame2, image=image2, text='')
        i2.grid(row=0, column=0, rowspan=5)

        label2 = customtkinter.CTkLabel(frame2, text="TEST 2",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label2.grid(row=0, column=1, pady=10, padx=10)

        text2 = customtkinter.CTkLabel(frame2,
                                       text="Test dotyczy stania z rękami w górze. \n"
                                            "Czas trwania testu wynosi 30 sekund.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.\n",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text2.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button2 = customtkinter.CTkButton(frame2, text="OTWÓRZ",
                                          command=lambda: self.start_romeberg_test("hands-up_standing"),
                                          corner_radius=0,
                                          width=75, height=15, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button2.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        # TEST 3
        frame3 = customtkinter.CTkFrame(romberg_frame, width=int(romberg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame3.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_rowconfigure(1, weight=1)
        frame3.grid_rowconfigure(2, weight=1)
        frame3.grid_rowconfigure(3, weight=1)
        frame3.grid_rowconfigure(4, weight=1)

        frame3.grid_columnconfigure(0, weight=1)
        frame3.grid_columnconfigure(1, weight=1)

        IMAGE_PATH_3 = 'assets/romberg_test/one-leg.png'

        image3 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH_3)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i3 = customtkinter.CTkLabel(frame3, image=image3, text='')
        i3.grid(row=0, column=0, rowspan=5)

        label3 = customtkinter.CTkLabel(frame3, text="TEST 3",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label3.grid(row=0, column=1, pady=10, padx=10)

        text3 = customtkinter.CTkLabel(frame3,
                                       text="Test dotyczy stania na jednej nodze. \n"
                                            "Czas trwania testu wynosi 30 sekund.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.\n",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text3.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button3 = customtkinter.CTkButton(frame3, text="OTWÓRZ",
                                          command=lambda: self.start_romeberg_test("one-leg_standing"),
                                          corner_radius=0,
                                          width=75, height=15, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button3.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        # TEST 4
        frame4 = customtkinter.CTkFrame(romberg_frame, width=int(romberg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame4.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        frame4.grid_rowconfigure(0, weight=1)
        frame4.grid_rowconfigure(1, weight=1)
        frame4.grid_rowconfigure(2, weight=1)
        frame4.grid_rowconfigure(3, weight=1)
        frame4.grid_rowconfigure(4, weight=1)

        frame4.grid_columnconfigure(0, weight=1)
        frame4.grid_columnconfigure(1, weight=1)

        IMAGE_PATH_4 = 'assets/romberg_test/one-leg_hands-up.png'

        image4 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH_4)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i4 = customtkinter.CTkLabel(frame4, image=image4, text='')
        i4.grid(row=0, column=0, rowspan=5)

        label4 = customtkinter.CTkLabel(frame4, text="TEST 4",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label4.grid(row=0, column=1, pady=10, padx=10)

        text4 = customtkinter.CTkLabel(frame4,
                                       text="Test dotyczy stania na dwóch nogach. \n"
                                            "z rękami w górze.\n"
                                            "Czas trwania testu wynosi 30 sekund.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text4.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button4 = customtkinter.CTkButton(frame4, text="OTWÓRZ",
                                          command=lambda: self.start_romeberg_test("hands-up-one-leg_standing"),
                                          corner_radius=0,
                                          width=75, height=15, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button4.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

    # TEST BERG
    def berg_test_page_button_event(self):
        self.clear_current_view()  # funkcja czyszcząca wigdety z głównego okna przed wgraniem następnej zakładki aplikacji
        self.sidebar_button_5.configure(fg_color="#FFFFFF", text_color="#4C7DBA",
                                        border_color="#4C7DBA", border_width=2)

        berg_frame = customtkinter.CTkFrame(self, width=1800, corner_radius=0, fg_color="#F2F2F2")
        berg_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        berg_frame.grid_rowconfigure(0, weight=0, minsize=50)
        berg_frame.grid_rowconfigure(1, weight=1, minsize=50)
        berg_frame.grid_rowconfigure(2, weight=1, minsize=50)

        berg_frame.grid_columnconfigure(0, weight=1, minsize=50)
        berg_frame.grid_columnconfigure(1, weight=1, minsize=50)

        # rozmiar assetów
        IMAGE_WIDTH = 160
        IMAGE_HEIGHT = 200

        # BUTTON WYNIKI
        result_button = customtkinter.CTkButton(berg_frame, text="WYNIKI",
                                                command=self.results_page_button_event, corner_radius=0,
                                                width=100, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                                border_color="#4C7DBA", border_width=2)
        result_button.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        # TEST 1
        frame1 = customtkinter.CTkFrame(berg_frame, width=int(berg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_rowconfigure(1, weight=1)
        frame1.grid_rowconfigure(2, weight=1)
        frame1.grid_rowconfigure(3, weight=1)
        frame1.grid_rowconfigure(4, weight=1)

        frame1.grid_columnconfigure(0, weight=1)
        frame1.grid_columnconfigure(1, weight=1)

        IMAGE_PATH = 'assets/berg_test/both-legs.png'

        image1 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i1 = customtkinter.CTkLabel(frame1, image=image1, text='')
        i1.grid(row=0, column=0, rowspan=5)

        label1 = customtkinter.CTkLabel(frame1, text="TEST 1",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label1.grid(row=0, column=1, pady=10, padx=10)

        text1 = customtkinter.CTkLabel(frame1,
                                       text="Test dotyczy stania na dwóch nogach. \n"
                                            "Czas trwania testu wynosi 30 sekund.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.\n\n",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text1.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button1 = customtkinter.CTkButton(frame1, text="OTWÓRZ",
                                          command=lambda: self.start_berg_test("both-legs_standing"), corner_radius=0,
                                          width=75, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button1.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        # TEST 2
        frame2 = customtkinter.CTkFrame(berg_frame, width=int(berg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_rowconfigure(1, weight=1)
        frame2.grid_rowconfigure(2, weight=1)
        frame2.grid_rowconfigure(3, weight=1)
        frame2.grid_rowconfigure(4, weight=1)

        frame2.grid_columnconfigure(0, weight=1)
        frame2.grid_columnconfigure(1, weight=1)

        IMAGE_PATH_2 = 'assets/berg_test/both-legs-soft.png'

        image2 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH_2)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i2 = customtkinter.CTkLabel(frame2, image=image2, text='')
        i2.grid(row=0, column=0, rowspan=5)

        label2 = customtkinter.CTkLabel(frame2, text="TEST 2",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label2.grid(row=0, column=1, pady=10, padx=10)

        text2 = customtkinter.CTkLabel(frame2,
                                       text="Test dotyczy stania na dwóch nogach \n"
                                            "na miękkim podłożu. Przygotuj miękkie\n"
                                            "podłoże przed przystąpieniem do testu\n"
                                            "Czas trwania testu wynosi 30 sekund.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text2.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button2 = customtkinter.CTkButton(frame2, text="OTWÓRZ",
                                          command=lambda: self.start_berg_test("both-legs_standing"),
                                          corner_radius=0,
                                          width=75, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button2.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        # TEST 3
        frame3 = customtkinter.CTkFrame(berg_frame, width=int(berg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame3.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_rowconfigure(1, weight=1)
        frame3.grid_rowconfigure(2, weight=1)
        frame3.grid_rowconfigure(3, weight=1)
        frame3.grid_rowconfigure(4, weight=1)

        frame3.grid_columnconfigure(0, weight=1)
        frame3.grid_columnconfigure(1, weight=1)

        IMAGE_PATH_3 = 'assets/berg_test/one-leg.png'

        image3 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH_3)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i3 = customtkinter.CTkLabel(frame3, image=image3, text='')
        i3.grid(row=0, column=0, rowspan=5)

        label3 = customtkinter.CTkLabel(frame3, text="TEST 3",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label3.grid(row=0, column=1, pady=10, padx=10)

        text3 = customtkinter.CTkLabel(frame3,
                                       text="Test dotyczy stania na jednej nodze. \n"
                                            "Czas trwania testu wynosi 30 sekund.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.\n\n",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text3.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button3 = customtkinter.CTkButton(frame3, text="OTWÓRZ",
                                          command=lambda: self.start_berg_test("one-leg_standing"),
                                          corner_radius=0,
                                          width=75, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button3.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

        # TEST 4
        frame4 = customtkinter.CTkFrame(berg_frame, width=int(berg_frame.winfo_reqwidth() / 2), height=350, corner_radius=0, fg_color="#FFFFFF")
        frame4.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        frame4.grid_rowconfigure(0, weight=1)
        frame4.grid_rowconfigure(1, weight=1)
        frame4.grid_rowconfigure(2, weight=1)
        frame4.grid_rowconfigure(3, weight=1)
        frame4.grid_rowconfigure(4, weight=1)

        frame4.grid_columnconfigure(0, weight=1)
        frame4.grid_columnconfigure(1, weight=1)

        IMAGE_PATH_4 = 'assets/berg_test/squad.png'

        image4 = customtkinter.CTkImage(light_image=Image.open(os.path.join(IMAGE_PATH_4)),
                                        size=(IMAGE_WIDTH, IMAGE_HEIGHT))
        i4 = customtkinter.CTkLabel(frame4, image=image4, text='')
        i4.grid(row=0, column=0, rowspan=5)

        label4 = customtkinter.CTkLabel(frame4, text="TEST 4",
                                        font=customtkinter.CTkFont("Times New Roman", size=20))
        label4.grid(row=0, column=1, pady=10, padx=10)

        text4 = customtkinter.CTkLabel(frame4,
                                       text="Test dotyczy zmianę z pozycji stojącej na siedzącą\n"
                                            "i z powrotem. Można do ćwiczenia użyć krzesła.\n"
                                            "Wykonaj ćwiczenie ze spokojem, ale sprawnie.\n"
                                            "Zadbaj o dobre oświetlenie pomieszczenia. \n"
                                            "W wypadku przerwania testu i wyniku\n"
                                            "negatywnego, możesz podejść do testu \n"
                                            "jeszcze raz. Pamiętaj, że test nie zastępuje\n"
                                            "badania u specjalisty.\n",
                                       font=customtkinter.CTkFont("Times New Roman", size=16))
        text4.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        button4 = customtkinter.CTkButton(frame4, text="OTWÓRZ",
                                          command=lambda: self.start_squad_test(),
                                          corner_radius=0,
                                          width=75, height=35, fg_color="#FFFFFF", text_color="#4C7DBA",
                                          border_color="#4C7DBA", border_width=2)
        button4.grid(row=3, column=1, pady=10, padx=10, sticky="nsew")

    # WYNIKI
    def results_page_button_event(self):
        self.clear_current_view()  # funkcja czyszcząca wigdety z głównego okna przed wgraniem następnej zakładki aplikacji
        self.sidebar_button_4.configure(fg_color="#FFFFFF", text_color="#4C7DBA",
                                        border_color="#4C7DBA", border_width=2)

        # Wygląd tabeli wyników
        result_frame = customtkinter.CTkFrame(self, width=1000, corner_radius=0, fg_color="#F2F2F2")
        result_frame.grid(row=0, column=1, sticky="nsew")
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.pack(side="right", fill="y")

        treeview = ttk.Treeview(
            result_frame,
            selectmode="browse",
            yscrollcommand=scrollbar.set,
            columns=(1, 2),
            height=10,
        )
        treeview.pack(expand=True, fill="both")
        scrollbar.config(command=treeview.yview)

        treeview.column("#0", anchor="w", width=120)
        treeview.column(1, anchor="w", width=120)
        treeview.column(2, anchor="w", width=120)

        treeview.heading("#0", text="TEST", anchor="center")
        treeview.heading(1, text="DATA", anchor="center")
        treeview.heading(2, text="WYNIK", anchor="center")

        # Pobieranie danych z bazy
        db_handler = Database()

        results = db_handler.get_test_results(self.user)
        # [(1, 1, 'romberg', 'both-legs_standing', '2024-01-07 14:52:28.534830', '0'),
        # (2, 1, 'romberg', 'hands-up_standing', '2024-01-07 16:04:18.190734', '1'),
        # (3, 1, 'romberg', 'hands-up_standing', '2024-01-07 16:04:31.856750', '0'),
        # (4, 1, 'romberg', 'one-leg_standing', '2024-01-07 16:05:29.907864', '0'),
        # (5, 1, 'romberg', 'hands-up-one-leg_standing', '2024-01-07 16:05:50.963718', '0')]
        romberg = []
        berg = []
        all_tests = []
        treeview_data = []
        parents = ["Test Romberga", "Test Berg"]

        for result in results:
            if result[2] == "romberg":
                romberg.append(result)
            elif result[2] == "berg":
                berg.append(result)

        all_tests.append(romberg)
        all_tests.append(berg)

        j = 0
        for x in range(len(all_tests)):
            j += 1
            i = j
            treeview_data.append(("", j, f"{parents[x]}", ("", "")))
            for y in range(len(all_tests[x])):
                j += 1
                treeview_data.append(
                    (i, j, test_name_from_db(all_tests[x][y][3]), (date_from_db(all_tests[x][y][4]), test_result_from_db(all_tests[x][y][5]))))

        for item in treeview_data:
            treeview.insert(
                parent=item[0], index="end", iid=item[1], text=item[2], values=item[3]
            )
            if item[0] == "" or item[1] in {8, 21}:
                treeview.item(item[1], open=True)  # Open parents

    # KONIEC
    def end_page_button_event(self):
        self.destroy()

    # TEST 30 SEKUND ROMBERG
    def start_romeberg_test(self, pose):
        path = '../poseestimationmodel/weights/weights.h5'

        if self.top_romberg_window is None or not self.top_romberg_window.winfo_exists():
            self.top_romberg_window = ThirtySecondsTest(self, pose=pose, path=path)
        else:
            self.top_romberg_window.focus()

        db_handler = Database()
        for result in self.top_romberg_window.ended_tests:
            db_handler.add_test_result(self.user, "romberg", pose, result[0], result[1])

    # TEST BERG 30 seconds
    def start_berg_test(self, pose):
        path = '../poseestimationmodel/weights/weights.h5'

        if self.top_berg_window is None or not self.top_berg_window.winfo_exists():
            self.top_berg_window = ThirtySecondsTest(self, pose=pose, path=path)
        else:
            self.top_berg_window.focus()

        db_handler = Database()
        for result in self.top_berg_window.ended_tests:
            db_handler.add_test_result(self.user, "berg", pose, result[0], result[1])

    def start_squad_test(self):

        if self.top_squad_window is None or not self.top_squad_window.winfo_exists():
            self.top_squad_window = SquadTest(self)
        else:
            self.top_squad_window.focus()

        print(self.top_squad_window.ended_tests)

        db_handler = Database()
        for result in self.top_squad_window.ended_tests:
            db_handler.add_test_result(self.user, "berg", "squad", result[0], result[1])
