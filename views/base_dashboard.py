
                                                                               
                                                                               
                                                                               
                                                                               
                                                                               
                                                                               
                                                                               

from __future__ import annotations
import customtkinter as ctk
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from main import RepairERP

ROLE_COLORS: dict[str, str] = {
    "master":     "#9b59b6",
    "admin":      "#3498db",
    "helpdesk":   "#27ae60",
    "technician": "#e67e22",
}

ROLE_ICONS: dict[str, str] = {
    "master":     "👑",   
    "admin":      "🛡",   
    "helpdesk":   "🎧",   
    "technician": "🔧",  }

                   
_ACCENT_L  = "#1a73e8"                                              
_ACCENT_D  = "#1254b5"                                             
_TOPBAR_H  = 64                                     
_SIDEBAR_W = 248                                   
_NAV_H     = 52                                              

class BaseDashboard(ctk.CTkFrame):

    def __init__(self, parent, app: "RepairERP", title: str, role: str):
        super().__init__(parent, corner_radius=0)
        self.app   = app
        self._title = title
        self._role  = role

        self._nav_frames:  dict[str, ctk.CTkFrame]  = {}
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._nav_badges:  dict[str, ctk.CTkLabel]  = {}                              
        self._sidebar_nav_row = 2                                    

                                                                
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_topbar()
        self._build_sidebar()

        host = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        host.grid(row=1, column=1, sticky="nsew")
        host.grid_rowconfigure(0, weight=1)
        host.grid_columnconfigure(0, weight=1)
        self._host = host
        self._content_frame = host                          

                                                                            
    def _build_topbar(self):
        bar = ctk.CTkFrame(
            self, height=_TOPBAR_H, corner_radius=0,
            fg_color=("gray92", "gray13"),
        )
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bar,
            text=f"  RepairERP  |  {self._title}",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(12, 0), sticky="w") 

                                                                
        ctk.CTkButton(
            bar, text="🔄️", width=2, height=38,
            font=ctk.CTkFont(size=20),
            fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30"),
            command=self._refresh_dashboard,
        ).grid(row=0, column=1, padx=(0, 4), pady=(12, 0), sticky="e")

        role_color = ROLE_COLORS.get(self._role, "#555")
        ctk.CTkLabel(
            bar,
            text=f"  {self._role.upper()}  ",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=role_color, corner_radius=6, text_color="white", height=37
        ).grid(row=0, column=2, padx=8, pady=(12, 0), sticky="e") 

        ctk.CTkButton(
            bar, text="Toggle Theme", width=140, height=38,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="transparent", border_width=1,
            command=self._toggle_theme,
        ).grid(row=0, column=3, padx=4, pady=(12, 0)) 

        ctk.CTkButton(
            bar, text="Logout", width=100, height=38,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=("#e05c5c", "#a93226"),
            hover_color=("#c0392b", "#922b21"),
            command=self.app.on_logout,
        ).grid(row=0, column=4, padx=(4, 20), pady=(12, 0)) 

    def _refresh_dashboard(self):
        if hasattr(self, "reset_state"):
            self.reset_state()
        if hasattr(self, "on_show"):
            self.on_show()
                                                                        
        if self.app.session:
            self.app.on_login(self.app.session)

                                                                                
    def _build_sidebar(self):
        role_color = ROLE_COLORS.get(self._role, "#555")
        icon       = ROLE_ICONS.get(self._role, "●")

        sb = ctk.CTkFrame(
            self, width=_SIDEBAR_W, corner_radius=0,
            fg_color=("gray88", "gray14"),
        )
        sb.grid(row=1, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_columnconfigure(0, weight=1)
        sb.grid_rowconfigure(99, weight=1)                     
        self._sidebar = sb

                                               
        banner = ctk.CTkFrame(
            sb, height=88, corner_radius=0,
            fg_color=(role_color, role_color),
        )
        banner.grid(row=0, column=0, sticky="ew")
        banner.grid_propagate(False)
        banner.grid_columnconfigure(0, weight=1)
        banner.grid_rowconfigure(0, weight=1)
        banner.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            banner, text=f"{icon}  {self._role.title()}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="white", anchor="w",
        ).grid(row=0, column=0, padx=20, sticky="sw")

        ctk.CTkLabel(
            banner, text="Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#d0e8ff", anchor="w",
        ).grid(row=1, column=0, padx=20, sticky="nw")

                              
        ctk.CTkLabel(
            sb, text="   MENU",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=("gray50", "gray55"), anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(14, 2))

                                                                                
    def add_nav_item(self, label: str, builder_fn, has_badge: bool = False) -> ctk.CTkFrame:
                                                                    
        frame = ctk.CTkFrame(self._host, corner_radius=0, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew")
        self._nav_frames[label] = frame

                                                      
        nav_row_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent", height=_NAV_H)
        nav_row_frame.grid(row=self._sidebar_nav_row, column=0, sticky="ew")
        nav_row_frame.grid_propagate(False)
        nav_row_frame.grid_columnconfigure(0, weight=1)

                        
        btn = ctk.CTkButton(
            nav_row_frame,
            text=f"   {label}",
            anchor="w",
            height=_NAV_H,
            font=ctk.CTkFont(family="Segoe UI", size=15),
            fg_color="transparent",
            text_color=("gray25", "gray72"),
            hover_color=("gray80", "gray22"),
            corner_radius=0,
            command=lambda n=label: self._show_nav(n),
        )
        btn.grid(row=0, column=0, sticky="ew")
        self._nav_buttons[label] = btn

        if has_badge:
                                                                         
            badge = ctk.CTkLabel(
                nav_row_frame,
                text="",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color="#e74c3c", text_color="white",
                corner_radius=8, width=28, height=22,
            )
                                                                        
            badge.grid(row=0, column=1, padx=(0, 12), sticky="e")
            badge.grid_remove()                          
            self._nav_badges[label] = badge

        self._sidebar_nav_row += 1

                               
        builder_fn(frame)

                                    
        if len(self._nav_frames) == 1:
            self._show_nav(label)

        return frame

    def _show_nav(self, name: str):
        for frame in self._nav_frames.values():
            frame.grid_remove()                                  
        self._nav_frames[name].grid()                                 

        for n, btn in self._nav_buttons.items():
            if n == name:
                btn.configure(
                    fg_color=(_ACCENT_L, _ACCENT_D),
                    text_color="white",
                    font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray25", "gray72"),
                    font=ctk.CTkFont(family="Segoe UI", size=15),
                )

                                                                                
    def update_nav_badge(self, label: str, count: int):
        badge = self._nav_badges.get(label)
        if not badge:
            return
        if count > 0:
            badge.configure(text=f" {count} ")
            badge.grid()                
        else:
            badge.grid_remove()                       

                                                                                
    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if current == "Dark" else "dark")

                                                                                
    @staticmethod
    def page_header(parent: ctk.CTkFrame, title: str) -> ctk.CTkFrame:
        hdr = ctk.CTkFrame(parent, fg_color="transparent", height=68)
        hdr.grid(row=0, column=0, columnspan=99, sticky="ew", padx=0)
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr, text=title,
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=28, sticky="w")

                 
        ctk.CTkFrame(
            hdr, height=2, corner_radius=1,
            fg_color=("gray78", "gray30"),
        ).grid(row=1, column=0, columnspan=99, sticky="ew", padx=28)

        return hdr

    @staticmethod
    def table_header_row(parent, headers: list[str], widths: list[int]) -> None:
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                parent, text=h,
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                width=w, anchor="w",
            ).grid(row=0, column=i, padx=(14 if i == 0 else 6, 6), sticky="w")

    @staticmethod
    def empty_label(parent, text: str) -> None:
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="gray",
        ).grid(row=0, column=0, padx=20, pady=32)
