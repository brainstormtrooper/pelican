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
        print('fillbox?')
        if not self.page:
            print('yes')
            cdata.proclock = True
            self.picsthread = threading.Thread(target=self.getpics, args=[self.page, direction, qty])
            self.picsthread.start()

    def getpics(self, pagelist, direction = 'down', qty = 100):
        datelimit = cdata.datetimerange[1] if direction == 'down' else cdata.datetimerange[0]
        cdata.get100pics(pagelist, direction, datelimit, qty)
        GObject.idle_add(self.fetchdone, direction)

    """
    Adds found thumb widgets to page.
    Should avoid duplicates
    """
    def fetchdone(self, direction):
        if self.page:
            cdata.datetimerange = [self.page[0].takendate, self.page[-1].takendate]
            self.bottomdatetime = self.page[-1].takendate
            self.topdatetime = self.page[0].takendate
            if direction == 'down':
                for tn in self.page[:]:
                    # fpath = getcacheloc(tn)
                    self.pageBox.append(tn.getwidget())
                    self.page.remove(tn)
            else:
                for tn in self.page[:]:
                    # fpath = getcacheloc(tn)
                    self.pageBox.prepend(tn.getwidget())
                    self.page.remove(tn)
        cdata.proclock = False
        print(self.page)
        print('range in fetchdone: ', cdata.datetimerange)