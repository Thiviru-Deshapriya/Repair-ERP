from __future__ import annotations
import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import RepairERP
    from views.admin_view import AdminView

ADMIN_ROLES = ["technician", "helpdesk"]

class UsersTab(ctk.CTkFrame):
    _ROLE_BADGE_COLORS: dict[str, str] = {
        "admin": "#3498db", "helpdesk": "#27ae60", "technician": "#e67e22",
    }

    def __init__(self, parent, app: "RepairERP", admin_view: "AdminView"):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.admin_view = admin_view
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)               
        self.grid_columnconfigure(1, weight=1)                

                                                                        
                                       
                                                                        
        left = ctk.CTkScrollableFrame(self, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left.grid_columnconfigure(0, weight=1)

                        
        card = ctk.CTkFrame(left, corner_radius=16, border_width=1)
        card.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 24))
        card.grid_columnconfigure(0, weight=1)

                           
        chdr = ctk.CTkFrame(
            card, height=56, corner_radius=0,
            fg_color=("gray86", "gray19"),
        )
        chdr.grid(row=0, column=0, sticky="ew")
        chdr.grid_propagate(False)
        chdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            chdr, text="➕  Create New User Account",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=22, sticky="w")

                   
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=1, column=0, sticky="ew", padx=24, pady=20)
        body.grid_columnconfigure(0, weight=1)

        labels = ["Full Name", "Username", "Password"]
        self._cu_entries: dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(
                body, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                anchor="w",
            ).grid(row=i * 2, column=0, sticky="w", pady=(12 if i else 0, 0))

            e = ctk.CTkEntry(
                body, height=44,
                font=ctk.CTkFont(family="Segoe UI", size=15),
                corner_radius=10,
                show="\u2022" if label == "Password" else "",
            )
            e.grid(row=i * 2 + 1, column=0, sticky="ew", pady=(4, 0))
            self._cu_entries[label] = e

                       
        ctk.CTkLabel(
            body, text="Role",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            anchor="w",
        ).grid(row=6, column=0, sticky="w", pady=(12, 0))

        role_menu = ctk.CTkOptionMenu(
            body, values=ADMIN_ROLES,
            height=44, font=ctk.CTkFont(family="Segoe UI", size=15),
            corner_radius=10,
        )
        role_menu.set("technician")
        role_menu.grid(row=7, column=0, sticky="ew", pady=(4, 0))
        self._cu_entries["Role"] = role_menu

                                      
        self._cu_status = ctk.CTkLabel(
            body, text="",
            font=ctk.CTkFont(family="Segoe UI", size=14),
        )
        self._cu_status.grid(row=8, column=0, sticky="w", pady=(10, 0))

        ctk.CTkButton(
            body, text="Create User", height=48,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            corner_radius=10,
            command=self._do_create_user,
        ).grid(row=9, column=0, sticky="ew", pady=(10, 0))

                                                                        
                                          
                                                                        
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

                       
        ctk.CTkLabel(
            right, text="👥  Current Users",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=20, pady=(24, 2), sticky="w")

        ctk.CTkLabel(
            right, text="Manage user accounts - deactivate to revoke login access",
            font=ctk.CTkFont(family="Segoe UI", size=13), text_color="gray",
            anchor="w",
        ).grid(row=1, column=0, padx=20, pady=(0, 8), sticky="w")

                              
        self._user_scroll = ctk.CTkScrollableFrame(right, corner_radius=10)
        self._user_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 24))
        self._user_scroll.grid_columnconfigure(0, weight=1)

                      
        self.refresh_user_list()

    def refresh_user_list(self):
        frame = self._user_scroll
        for w in frame.winfo_children():
            w.destroy()

        res = self.app.api.get_all_users()
        if res["status"] != "success":
            self.admin_view.empty_label(frame, f"Error loading users: {res.get('message')}")
            return

        users = res["data"]
        if not users:
            self.admin_view.empty_label(frame, "No user accounts found.")
            return

        for idx, u in enumerate(users):
            is_active = u["is_active"]
            bg = ("gray93", "gray19") if idx % 2 == 0 else ("gray88", "gray23")

            row = ctk.CTkFrame(frame, fg_color=bg, corner_radius=8, height=56)
            row.grid(row=idx, column=0, sticky="ew", pady=3)
            row.grid_propagate(False)
            row.grid_columnconfigure(1, weight=1)

                        
            role_color = self._ROLE_BADGE_COLORS.get(u["role"], "#888")
            ctk.CTkLabel(
                row, text=f"  {u['role'].upper()}  ",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color=role_color, corner_radius=6, text_color="white",
                width=90,
            ).grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")

                      
            ctk.CTkLabel(
                row, text=u["username"],
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                anchor="w",
            ).grid(row=0, column=1, padx=(0, 8), sticky="w")

                                            
            if is_active:
                status_text  = "● Active"
                status_color = "#27ae60"
            else:
                status_text  = "● Inactive"
                status_color = "#e05c5c"

            ctk.CTkLabel(
                row, text=status_text,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=status_color, width=90, anchor="w",
            ).grid(row=0, column=2, padx=(0, 8), sticky="e")

                           
            if is_active:
                btn_text   = "Deactivate"
                btn_fg     = ("#e05c5c", "#a93226")
                btn_hover  = ("#c0392b", "#922b21")
            else:
                btn_text   = "Activate"
                btn_fg     = ("#27ae60", "#1e8449")
                btn_hover  = ("#229954", "#1a7640")

            ctk.CTkButton(
                row, text=btn_text, width=100, height=34,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                corner_radius=8,
                fg_color=btn_fg, hover_color=btn_hover,
                command=lambda uid=u["user_id"], uname=u["username"],
                               active=is_active: self._confirm_toggle_user(uid, uname, active),
            ).grid(row=0, column=3, padx=(0, 12), pady=10, sticky="e")

    def _confirm_toggle_user(self, user_id: int, username: str, currently_active: bool):
        if currently_active:
            action_word = "deactivate"
            msg = (f"Are you sure you want to deactivate \"{username}\"?\n\n"
                   f"They will be immediately blocked from logging in.")
        else:
            action_word = "activate"
            msg = (f"Are you sure you want to re-activate \"{username}\"?\n\n"
                   f"They will be able to log in again.")

        confirmed = messagebox.askyesno(
            f"Confirm {action_word.title()}",
            msg,
            icon="warning",
        )
        if not confirmed:
            return

        new_state = not currently_active
        result = self.app.api.toggle_user_active(
            admin_id=self.app.session.get("id"),
            target_user_id=user_id,
            new_state=new_state,
        )

        if result["status"] == "success":
            messagebox.showinfo(
                "Success",
                f"User \"{username}\" has been {action_word}d successfully.",
            )
            self.refresh_user_list()
        else:
            messagebox.showerror(
                "Error",
                result.get("message", f"Failed to {action_word} user."),
            )

    def _do_create_user(self):
        name     = self._cu_entries["Full Name"].get().strip()
        username = self._cu_entries["Username"].get().strip()
        password = self._cu_entries["Password"].get()
        role     = self._cu_entries["Role"].get()

        if not all([name, username, password]):
            self._cu_status.configure(text="All fields are required.", text_color="#e05c5c")
            return

        result = self.app.api.create_user(
            creator_id=self.app.session.get("id"),
            name=name, role=role, username=username, password=password,
        )

        if result["status"] == "success":
            self._cu_status.configure(
                text=f"\u2713  User '{username}' ({role}) created.",
                text_color="#27ae60",
            )
            for widget in self._cu_entries.values():
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
            self.refresh_user_list()
        else:
            self._cu_status.configure(
                text=result.get("message", "Failed to create user."),
                text_color="#e05c5c",
            )
