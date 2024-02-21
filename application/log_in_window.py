import tkinter
import customtkinter
from database import Database
from sign_in_window import RegisterWindow
from main_window import MainWindow


class LoginWindow(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("dark-blue")
        self.geometry("800x500")
        # "Keep Your Balance - Balance Test Application"
        self.title("Keep Your Balance - Aplikacja do badania równowagi")

        self.frame = customtkinter.CTkFrame(master=self, width=600, height=400, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.label = customtkinter.CTkLabel(self.frame, text="KEEP YOUR BALANCE", font=("Century Gothic", 24))
        self.label.pack(pady=12, padx=10)
        self.login_label = customtkinter.CTkLabel(self.frame, text="Zaloguj się", font=("Century Gothic", 16))
        self.login_label.pack(pady=12, padx=10)

        self.username = customtkinter.CTkEntry(self.frame, width=220, placeholder_text="Login", corner_radius=0, height=35)
        self.username.pack(pady=10, padx=10)
        self.password = customtkinter.CTkEntry(self.frame, width=220, placeholder_text="Hasło", show="*", corner_radius=0, height=35)
        self.password.pack(pady=10, padx=10)

        self.button = customtkinter.CTkButton(self.frame, width=220, text="Zaloguj", command=self.log_in, corner_radius=0, height=35)
        self.button.pack(pady=10, padx=10)

        self.register_label = customtkinter.CTkLabel(self.frame, text="Chcesz się zarejestrować?", font=("Century Gothic", 12))
        self.register_label.pack(pady=5, padx=10)
        self.button2 = customtkinter.CTkButton(self.frame, width=220, text="Zarejestruj",
                                               command=self.open_register, corner_radius=0, height=35)
        self.button2.pack(side="top", padx=20, pady=10)

        self.register_window = None

    def log_in(self):
        username = self.username.get()
        password = self.password.get()

        db_handler = Database()

        is_data_correct = db_handler.verify_user(username, password)
        if is_data_correct[0]:
            self.destroy()
            app = MainWindow(is_data_correct[1])
            app.mainloop()
        else:
            print("takiego użytkownika nie ma")

        self.username.delete(0, len(username))
        self.password.delete(0, len(password))

    def open_register(self):
        if self.register_window is None or not self.register_window.winfo_exists():
            self.register_window = RegisterWindow(self)
            self.register_window.resizable(False, False)
        else:
            self.register_window.focus()
