from __future__ import annotations
import customtkinter as ctk
from views.base_dashboard import BaseDashboard
from typing import TYPE_CHECKING

from views.helpdesk_tabs.all_tickets_tab import AllTicketsTab
from views.helpdesk_tabs.create_ticket_tab import CreateTicketTab
from views.helpdesk_tabs.search_tickets_tab import SearchTicketsTab
from views.helpdesk_tabs.customers_tab import CustomersTab
from views.helpdesk_tabs.customer_pickup_tab import CustomerPickupTab

if TYPE_CHECKING:
    from main import RepairERP

class HelpdeskView(BaseDashboard):

    def __init__(self, parent, app: "RepairERP"):
        super().__init__(parent, app, title="Help Desk", role="helpdesk")
        self._all_ticket_cache: list[dict] = []
        self._customer_cache:   list[dict] = []
        self._build()

    def on_show(self):
        self._all_ticket_cache = []
        if hasattr(self, "all_tickets_tab"):
            self.all_tickets_tab.refresh()
        if hasattr(self, "search_tickets_tab"):
            self.search_tickets_tab.refresh()
        if hasattr(self, "customers_tab"):
            self.customers_tab.refresh()
        if hasattr(self, "customer_pickup_tab"):
            self.customer_pickup_tab.refresh()

    def reset_state(self):
        if hasattr(self, "create_ticket_tab"):
            self.create_ticket_tab.reset_state()
        if hasattr(self, "search_tickets_tab"):
            self.search_tickets_tab.reset_state()
        if hasattr(self, "customers_tab"):
            self.customers_tab.reset_state()

    def _build(self):

        def build_create_ticket(tab):
            self.create_ticket_tab = CreateTicketTab(tab, self.app, self)
            self.create_ticket_tab.pack(expand=True, fill="both")

        def build_search_tickets(tab):
            self.search_tickets_tab = SearchTicketsTab(tab, self.app, self)
            self.search_tickets_tab.pack(expand=True, fill="both")

        def build_customers(tab):
            self.customers_tab = CustomersTab(tab, self.app, self)
            self.customers_tab.pack(expand=True, fill="both")

        def build_notify(tab):
            self.customer_pickup_tab = CustomerPickupTab(tab, self.app, self)
            self.customer_pickup_tab.pack(expand=True, fill="both")

        
        self.add_nav_item("➕  Create Ticket",      build_create_ticket)
        self.add_nav_item("🔍  Search Tickets", build_search_tickets)
        self.add_nav_item("👥  Customers",       build_customers)
        self.add_nav_item("🔔  Notify Customer", build_notify)
