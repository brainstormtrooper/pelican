# import threading
from gi.repository import Gtk, GLib, GdkPixbuf, GObject
from .dates import *
from . import cdata

@Gtk.Template(resource_path='/com/github/brainstormtrooper/cphotos/page.ui')
class CphotosPage(Gtk.Box):
    __gtype_name__ = 'CphotosPage'

    pageBox = Gtk.Template.Child()

    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #
        # List of pics returned from database
        # pics are removed from here and added to dates list
        #
        self.page = []
        #
        # Pics sorted into dated groups
        #
        self.dates = {}

    def fillbox(self, direction = 'down', qty = 100):
        found = 0
        # datelimit = cdata.datetimerange[1] if direction == 'down' else cdata.datetimerange[0]
        datelimit = None
        if cdata.pages:
            datelimit = cdata.pages[-1][1] if direction == 'down' else cdata.pages[0][0]
        cdata.get100pics(self.page, direction, datelimit, qty)
        found = len(self.page)
        if found:
            if direction == 'up':
                self.page.reverse()

            cdata.datetimerange = [self.page[0][3], self.page[-1][3]]
            for tn in self.page[:]:
                # fpath = getcacheloc(tn)
                self.todate(tn)
                # self.pageBox.append(tn.getwidget())
                self.page.remove(tn)
            for datestr in self.dates:
                mydate = dateBlock(datestr)
                myYear = datestr.split('-')[0]
                if cdata.curyear != myYear:
                    mydate.yearLabel.set_text(myYear)
                mydate.additems(self.dates[datestr])
                self.pageBox.append(mydate)
                cdata.curyear = myYear

        return found    
    
    def todate(self, tn):
        datestr = tn[3].split('T')[0]
        if datestr not in self.dates.keys():
            print('creating new date', datestr)
            self.dates[datestr] = [ tn ]
        else:
            self.dates[datestr].append(tn)

