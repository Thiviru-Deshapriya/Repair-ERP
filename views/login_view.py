from __future__ import annotations
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import RepairERP

                                                          
                                                                         
_ACCENT_LIGHT = "#1a73e8"
_ACCENT_DARK  = "#1558b0"

class LoginView(ctk.CTkFrame):

    def __init__(self, parent, app: "RepairERP"):
        super().__init__(parent, corner_radius=0)
        self.app = app                                                             
        self._build()

                                                                               
    def _build(self):
                                                          
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_left_panel()
        self._build_right_panel()

                                                                               
    def _build_left_panel(self):
        left = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=(_ACCENT_LIGHT, _ACCENT_DARK),
        )
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure(0, weight=1)
        left.grid_columnconfigure(0, weight=1)

        box = ctk.CTkFrame(left, fg_color="transparent")
        box.grid(row=0, column=0, padx=48)

                                 
        ctk.CTkLabel(
            box,
            text="\U0001f527",                               
            font=ctk.CTkFont(size=80),
            text_color="white",
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            box,
            text="RepairERP",
            font=ctk.CTkFont(family="Segoe UI", size=52, weight="bold"),
            text_color="white",
        ).pack()

        ctk.CTkLabel(
            box,
            text="Mobile Repair Shop\nManagement System",
            font=ctk.CTkFont(family="Segoe UI", size=20),
            text_color="#c8dcf8",
            justify="center",
        ).pack(pady=(14, 40))

                            
        for feat in (
            "\u2714\ufe0f  Job Cards & Ticketing",
            "\u2714\ufe0f  Role-Based Access Control",
            "\u2714\ufe0f  Reports & Analytics",
            "\u2714\ufe0f  Inventory Tracking",
        ):
            ctk.CTkLabel(
                box,
                text=feat,
                font=ctk.CTkFont(family="Segoe UI", size=16),
                text_color="#c8dcf8",
                anchor="w",
            ).pack(anchor="w", pady=5)

                                                                               
    def _build_right_panel(self):
        right = ctk.CTkFrame(self, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=0)
        right.grid_columnconfigure(0, weight=1)

                                            
        form = ctk.CTkFrame(right, fg_color="transparent")
        form.grid(row=0, column=0, padx=72)
        form.grid_columnconfigure(0, weight=1)

                      
        ctk.CTkLabel(
            form,
            text="Welcome back",
            font=ctk.CTkFont(family="Segoe UI", size=40, weight="bold"),
        ).grid(row=0, column=0, pady=(0, 8))

        ctk.CTkLabel(
            form,
            text="Sign in to your account to continue",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="gray",
        ).grid(row=1, column=0, pady=(0, 40))

                        
        ctk.CTkLabel(
            form,
            text="Username",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
        ).grid(row=2, column=0, sticky="w")

        self._username = ctk.CTkEntry(
            form,
            placeholder_text="Enter your username",
            width=380,
            height=54,
            font=ctk.CTkFont(family="Segoe UI", size=17),
            corner_radius=10,
        )
        self._username.grid(row=3, column=0, pady=(8, 22), sticky="ew")

                        
        ctk.CTkLabel(
            form,
            text="Password",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
        ).grid(row=4, column=0, sticky="w")

        self._password = ctk.CTkEntry(
            form,
            placeholder_text="Enter your password",
            show="\u2022",
            width=380,
            height=54,
            font=ctk.CTkFont(family="Segoe UI", size=17),
            corner_radius=10,
        )
        self._password.grid(row=5, column=0, pady=(8, 12), sticky="ew")

                           
        self._error_label = ctk.CTkLabel(
            form,
            text="",
            text_color="#e05c5c",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            anchor="w",
        )
        self._error_label.grid(row=6, column=0, sticky="w", pady=(0, 4))

                              
        self._login_btn = ctk.CTkButton(
            form,
            text="Sign In",
            height=58,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            corner_radius=10,
            command=self._do_login,
        )
        self._login_btn.grid(row=7, column=0, pady=(14, 0), sticky="ew")

                                  
        self._username.bind("<Return>", lambda e: self._password.focus())
        self._password.bind("<Return>", lambda e: self._do_login())

                                                          
        ctk.CTkButton(
            right,
            text="Toggle Theme",
            width=140,
            height=34,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="transparent",
            border_width=1,
            command=self._toggle_theme,
        ).grid(row=1, column=0, sticky="se", padx=24, pady=18)

                                                                               
    def _do_login(self):
        username = self._username.get().strip()
        password = self._password.get()

        if not username or not password:
            self._show_error("Please enter both username and password.")
            return

                                                                      
        self._login_btn.configure(state="disabled", text="Signing in\u2026")
        self.update_idletasks()                                                

        result = self.app.api.login(username, password)

        self._login_btn.configure(state="normal", text="Sign In")

        if result["status"] == "success":
            self._show_error("")                                     
            self._username.delete(0, "end")                                  
            self._password.delete(0, "end")
            self.app.on_login(result["user"])                                           
        else:
            self._show_error(result.get("message", "Login failed."))

    def _show_error(self, msg: str):
        self._error_label.configure(text=msg)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if current == "Dark" else "dark")
