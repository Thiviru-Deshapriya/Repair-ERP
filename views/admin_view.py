from __future__ import annotations
import customtkinter as ctk
from views.base_dashboard import BaseDashboard
from typing import TYPE_CHECKING

from views.admin_tabs.dashboard_tab import DashboardTab
from views.admin_tabs.inventory_tab import InventoryTab, DonorBoardTab
from views.admin_tabs.tickets_tab import TicketsTab
from views.admin_tabs.users_tab import UsersTab
from views.admin_tabs.reports_tab import ReportsTab

if TYPE_CHECKING:
    from main import RepairERP

class AdminView(BaseDashboard):

    def __init__(self, parent, app: "RepairERP"):
        super().__init__(parent, app, title="Admin Dashboard", role="admin")
        self._build()                                                                

                                                                        
    def reset_state(self):
        if hasattr(self, "users_tab") and hasattr(self.users_tab, "_cu_entries"):
            for widget in self.users_tab._cu_entries.values():
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
        if hasattr(self, "users_tab") and hasattr(self.users_tab, "_cu_status"):
            self.users_tab._cu_status.configure(text="")

    def on_show(self):
        if hasattr(self, "dashboard_tab"):
            self.dashboard_tab.refresh_alerts()
        if hasattr(self, "tickets_tab"):
            self.tickets_tab.refresh_all_tickets()
        if hasattr(self, "users_tab"):
            self.users_tab.refresh_user_list()
        if hasattr(self, "inventory_tab"):
            self.inventory_tab.refresh_inventory()

                                                                        
    _ALERTS_NAV_LABEL = "🚨  Action Required"

    def _build(self):
        def build_dashboard(tab):
            self.dashboard_tab = DashboardTab(tab, self.app, self)
            self.dashboard_tab.pack(expand=True, fill="both")
            
        def build_inventory(tab):
            self.inventory_tab = InventoryTab(tab, self.app, self)
            self.inventory_tab.pack(expand=True, fill="both")
            
        def build_donor_boards(tab):
            self.donor_board_tab = DonorBoardTab(tab, self.app, self)
            self.donor_board_tab.pack(expand=True, fill="both")
            
        def build_tickets(tab):
            self.tickets_tab = TicketsTab(tab, self.app, self)
            self.tickets_tab.pack(expand=True, fill="both")
            
        def build_users(tab):
            self.users_tab = UsersTab(tab, self.app, self)
            self.users_tab.pack(expand=True, fill="both")
            
        def build_reports(tab):
            self.reports_tab = ReportsTab(tab, self.app, self)
            self.reports_tab.pack(expand=True, fill="both")

        self.add_nav_item(self._ALERTS_NAV_LABEL, build_dashboard, has_badge=True)
        self.add_nav_item("🎫  All Tickets",       build_tickets)
        self.add_nav_item("🤝  Donor Boards",      build_donor_boards)
        self.add_nav_item("🧾  Inventory",         build_inventory)
        self.add_nav_item("📄  Generate Reports",  build_reports)
        self.add_nav_item("👤  User Management",   build_users)
