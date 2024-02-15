from gi.repository import Gtk, GLib, GdkPixbuf
#CphotosDate
@Gtk.Template(resource_path='/com/github/brainstormtrooper/cphotos/dates.ui')
class dateBlock(Gtk.Box):
    __gtype_name__ = 'CphotosDate'

    yearLabel = Gtk.Template.Child()
    monthLabel = Gtk.Template.Child()
    dateLabel = Gtk.Template.Child()
    flow = Gtk.Template.Child()

    def __init__(self, date, **kwargs):
        super().__init__(**kwargs)
        self.date = date

    
    def additem(self, item):
        pass

    
    
    