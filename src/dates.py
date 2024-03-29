from gi.repository import Gtk, GLib, GdkPixbuf
from . import cdata
from .previews import preview
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
        self.places = []
    
    def additems(self, items):
        for tn in items:
            P = preview(tn)
            self.doPlaces(P)
            widget = P.getwidget()
            if widget:
                self.flow.append(widget)
        placeslabeltext = ', '.join(list(set([w for w in self.places if None != w])))
        dateloc = f"{self.date} at {placeslabeltext}"
        self.dateLabel.set_text(dateloc)
    
    def doPlaces(self, item):
        # list(set(curwords + [w for w in words if None != w]))
        self.places.append(item.placename)
        self.places.append(item.town)
        
    