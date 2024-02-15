import threading
from gi.repository import Gtk, GLib, GdkPixbuf, GObject

from . import cdata

@Gtk.Template(resource_path='/com/github/brainstormtrooper/cphotos/page.ui')
class CphotosPage(Gtk.Box):
    __gtype_name__ = 'CphotosPage'

    pageBox = Gtk.Template.Child()

    page = []
    dates = []
    bottomdatetime = None
    topdatetime = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fillbox(self, direction = 'down', qty = 100):
        found = 0
        # datelimit = cdata.datetimerange[1] if direction == 'down' else cdata.datetimerange[0]
        datelimit = None
        if cdata.pages:
            datelimit = cdata.pages[-1][1] if direction == 'down' else cdata.pages[0][0]
        cdata.get100pics(self.page, direction, datelimit, qty)
        found = len(self.page)
        if self.page:
            
            if direction == 'down':
                cdata.datetimerange = [self.page[0].takendate, self.page[-1].takendate]
                self.bottomdatetime = self.page[-1].takendate
                self.topdatetime = self.page[0].takendate
                for tn in self.page[:]:
                    # fpath = getcacheloc(tn)
                    self.pageBox.append(tn.getwidget())
                    self.page.remove(tn)
            else:
                self.page.reverse()
                cdata.datetimerange = [self.page[0].takendate, self.page[-1].takendate]
                self.bottomdatetime = self.page[-1].takendate
                self.topdatetime = self.page[0].takendate
                for tn in self.page[:]:
                    # fpath = getcacheloc(tn)
                    self.pageBox.append(tn.getwidget())
                    self.page.remove(tn)
        return found    
    

