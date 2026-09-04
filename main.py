import customtkinter as ctk
from app import Api
from views.login_view import LoginView
from views.master_view import MasterView
from views.admin_view import AdminView
from views.helpdesk_view import HelpdeskView
from views.tech_view import TechView

       
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

                                                               
                                                        
ROLE_FRAME_MAP = {
    "master":     "master",
    "admin":      "admin",
    "helpdesk":   "helpdesk",
    "technician": "tech",
}

class RepairERP(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RepairERP — Mobile Repair Shop")
        self.geometry("1280x800")                                     
        self.minsize(1024, 680)                                                           
        self.after(0, lambda: self.state("zoomed"))                             

                                                                          
        self.api = Api()

                                                            
        self.session = {}

                                                                 
        self._frames: dict[str, ctk.CTkFrame] = {}

                                                          
        self._build_frames()
        self.show_frame("login")

                                                                        
                      
                                                                        
    def _build_frames(self):
      
                                              
        container = ctk.CTkFrame(self, corner_radius=0)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self._container = container

                                                                   
        for name, cls in [
            ("login",    LoginView),
            ("master",   MasterView),
            ("admin",    AdminView),
            ("helpdesk", HelpdeskView),
            ("tech",     TechView),
        ]:
            frame = cls(container, self)                                                  
            self._frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")                               

    def show_frame(self, name: str):
        frame = self._frames[name]
        if hasattr(frame, "on_show"):
            frame.on_show()                                                
        frame.tkraise()                                                                

                                                                                                                         
    def on_login(self, user: dict):
   
        self.session = user
        role   = user["role"]
                                                                                          
        target = ROLE_FRAME_MAP.get(role, "login")
        self.show_frame(target)                         

                                 
    def on_logout(self):
        
        for name, frame in self._frames.items():
            if name != "login" and hasattr(frame, "reset_state"):
                frame.reset_state()
        self.session = {}                              
        self.show_frame("login")                               

if __name__ == "__main__":
                                                           
                                          
    app = RepairERP()
    app.mainloop()                                                                 
