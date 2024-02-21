import customtkinter
from database import Database


class RegisterWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x400")
        self.title("Keep Your Balance - Zarejestruj się")

        self.label = customtkinter.CTkLabel(self, text="Rejestracja", font=("Roboto", 16))
        self.label.pack(padx=20, pady=20)

        self.username = customtkinter.CTkEntry(self, placeholder_text="Login", corner_radius=0)
        self.username.pack(pady=12, padx=10)
        self.password = customtkinter.CTkEntry(self, placeholder_text="Hasło", show="*", corner_radius=0)
        self.password.pack(pady=12, padx=10)
        self.passwordConfirmation = customtkinter.CTkEntry(self, placeholder_text="Potwierdź hasło", show="*", corner_radius=0)
        self.passwordConfirmation.pack(pady=12, padx=10)

        self.button_reg = customtkinter.CTkButton(self, text="Zarejestruj", command=self.sign_in, corner_radius=0)
        self.button_reg.pack(pady=12, padx=10)

    def sign_in(self):
        username = self.username.get()
        password = self.password.get()
        password2 = self.passwordConfirmation.get()

        db_handler = Database()

        is_username_free = db_handler.check_username(username)
        if is_username_free and len(username) > 0:
            if len(password) > 0 and password == password2:
                db_handler.register_user(username, password)
                self.destroy()
            else:
                print("Hasła się nie zgadzają")
                self.password.delete(0, len(password))
                self.passwordConfirmation.delete(0, len(password2))
        else:
            print("Username jest zajęty")
            self.username.delete(0, len(username))
            self.password.delete(0, len(password))
            self.passwordConfirmation.delete(0, len(password2))
