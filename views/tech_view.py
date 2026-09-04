
                                                                                        

from __future__ import annotations
import customtkinter as ctk
from views.base_dashboard import BaseDashboard
from typing import TYPE_CHECKING
from views.tech_tabs import IntakePoolTab, MyTicketsTab, InProgressTab

if TYPE_CHECKING:
    from main import RepairERP

class TechView(BaseDashboard):

    def __init__(self, parent, app: "RepairERP"):
        super().__init__(parent, app, title="Technician Dashboard", role="technician")
        self._build()

    def on_show(self):
        if hasattr(self, 'intake_pool_ui'):
            self.intake_pool_ui._refresh_intake()
        if hasattr(self, 'my_tickets_ui'):
            self.my_tickets_ui._refresh_my_tickets()
        if hasattr(self, 'in_progress_ui'):
            self.in_progress_ui._refresh_inprogress()

    def reset_state(self):
        if hasattr(self, 'in_progress_ui'):
            self.in_progress_ui.reset_state()

                                                                        
    def _build(self):
        self.add_nav_item("\U0001f4e5  Intake Pool",  self._build_intake_tab)
        self.add_nav_item("\U0001f4cb  My Tickets",   self._build_my_tickets_tab)
        self.add_nav_item("\u2699\ufe0f  In-Progress", self._build_inprogress_tab)

                                                                        
                             
                                                                        
    def _build_intake_tab(self, tab: ctk.CTkFrame):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.intake_pool_ui = IntakePoolTab(
            master=tab, 
            app=self.app, 
            dashboard=self, 
            on_ticket_accepted=self._handle_ticket_accepted
        )
        self.intake_pool_ui.grid(row=0, column=0, sticky="nsew")

    def _handle_ticket_accepted(self):
        if hasattr(self, 'intake_pool_ui'):
            self.intake_pool_ui._refresh_intake()
        if hasattr(self, 'my_tickets_ui'):
            self.my_tickets_ui._refresh_my_tickets()

                                                                        
                            
                                                                        
    def _build_my_tickets_tab(self, tab: ctk.CTkFrame):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.my_tickets_ui = MyTicketsTab(
            master=tab,
            app=self.app,
            dashboard=self,
            on_manage_parts=self._handle_manage_parts
        )
        self.my_tickets_ui.grid(row=0, column=0, sticky="nsew")

    def _handle_manage_parts(self, ticket: dict):
        if hasattr(self, 'in_progress_ui'):
            self.in_progress_ui.set_ticket(ticket)
        self._show_nav("\u2699\ufe0f  In-Progress")

                                                                        
                             
                                                                        
    def _build_inprogress_tab(self, tab: ctk.CTkFrame):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.in_progress_ui = InProgressTab(
            master=tab,
            app=self.app,
            dashboard=self,
            on_ticket_completed=self._handle_ticket_completed
        )
        self.in_progress_ui.grid(row=0, column=0, sticky="nsew")

    def _handle_ticket_completed(self):
        if hasattr(self, 'intake_pool_ui'):
            self.intake_pool_ui._refresh_intake()
        if hasattr(self, 'my_tickets_ui'):
            self.my_tickets_ui._refresh_my_tickets()
