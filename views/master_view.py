from __future__ import annotations
import customtkinter as ctk
from views.base_dashboard import BaseDashboard
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import RepairERP

                                                                       
ALL_ROLES = ["master", "admin", "technician", "helpdesk"]

class MasterView(BaseDashboard):

    def __init__(self, parent, app: "RepairERP"):
        super().__init__(parent, app, title="Master Dashboard", role="master")
        self._build()

    def reset_state(self):
        if hasattr(self, "_cu_entries"):
            for widget in self._cu_entries.values():
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
        if hasattr(self, "_cu_status"):
            self._cu_status.configure(text="")

    def _build(self):
        self.add_nav_item("\U0001f464  Create User", self._build_create_user_tab)

                                                                        
    def _build_create_user_tab(self, tab: ctk.CTkFrame):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=2)
        scroll.grid_columnconfigure(1, weight=3)
        scroll.grid_columnconfigure(2, weight=2)

        card = ctk.CTkFrame(scroll, corner_radius=16, border_width=1)
        card.grid(row=0, column=1, sticky="ew", pady=40)
        card.grid_columnconfigure(0, weight=1)

                     
        chdr = ctk.CTkFrame(
            card, height=60, corner_radius=0,
            fg_color=("gray86", "gray19"),
        )
        chdr.grid(row=0, column=0, sticky="ew")
        chdr.grid_propagate(False)
        chdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            chdr, text="Create New User Account",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=24, sticky="w")

                   
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=1, column=0, sticky="ew", padx=28, pady=24)
        body.grid_columnconfigure(0, weight=1)

        labels = ["Full Name", "Username", "Password"]
        self._cu_entries: dict[str, ctk.CTkEntry | ctk.CTkOptionMenu] = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(
                body, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                anchor="w",
            ).grid(row=i * 2, column=0, sticky="w", pady=(16 if i else 0, 0))

            e = ctk.CTkEntry(
                body, height=50,
                font=ctk.CTkFont(family="Segoe UI", size=16),
                corner_radius=10,
                show="\u2022" if label == "Password" else "",
            )
            e.grid(row=i * 2 + 1, column=0, sticky="ew", pady=(6, 0))
            self._cu_entries[label] = e

                       
        ctk.CTkLabel(
            body, text="Role",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
        ).grid(row=6, column=0, sticky="w", pady=(16, 0))

        role_menu = ctk.CTkOptionMenu(
            body, values=ALL_ROLES,
            height=50, font=ctk.CTkFont(family="Segoe UI", size=16),
            corner_radius=10,
        )
        role_menu.set("technician")
        role_menu.grid(row=7, column=0, sticky="ew", pady=(6, 0))
        self._cu_entries["Role"] = role_menu

        self._cu_status = ctk.CTkLabel(
            body, text="",
            font=ctk.CTkFont(family="Segoe UI", size=15),
        )
        self._cu_status.grid(row=8, column=0, sticky="w", pady=(14, 0))

        ctk.CTkButton(
            body, text="Create User", height=54,
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            corner_radius=10,
            command=self._do_create_user,
        ).grid(row=9, column=0, sticky="ew", pady=(12, 0))

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
        else:
            self._cu_status.configure(
                text=result.get("message", "Failed to create user."),
                text_color="#e05c5c",
            )
