# window.py
#
# Copyright 2022 Rick Opper
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import threading
from .pager import CphotosPage
from .mapview import Mapview
from gi.repository import Adw
from gi.repository import Gtk, GLib, GdkPixbuf, GObject
# from PIL import Image

from . import cdata

@Gtk.Template(resource_path='/com/github/brainstormtrooper/cphotos/window.ui')
class CphotosWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CphotosWindow'

    scroll = Gtk.Template.Child()
    scrollpage = Gtk.Template.Child()
    previewreveal = Gtk.Template.Child()
    mapbox = Gtk.Template.Child()
    search_button = Gtk.Template.Child()
    scrolld = 0
    ignorescrolldown = False
    ignorescrollup = False
    
    

        
    def doindex(self):
        self.work_thread = threading.Thread(target=self.update)
        self.work_thread.start()
        # GObject.timeout_add(1, 200, )


    """
    If 2/3 up or down, trigger query for next pageload of pics in right direction
    """
    def scroll_notify_event(w, e, self):
        """
        Callback for scroll event

        Args:
            w (widget): Not used
            e (event): The event and properties that triggered the function
        """
        dvs = e.props.upper - e.props.page_size
        if dvs == 0:
            dvs = 1
        prct = (e.props.value / (dvs)) * 100

        if e.props.value > self.scrolld:
            self.ignorescrollup = False
            if prct >= 90 and len(cdata.pages) < 3 and not self.ignorescrolldown and not cdata.proclock:
                #
                # thread for new page
                # mythread = threading.Thread(target=self.update, args=listofargs)
                #
                print('here')
                self.mythread = threading.Thread(target=self.dopage, args=['down', 50])
                self.mythread.start()
                
                    
                    
                
        if e.props.value < self.scrolld:
            self.ignorescrolldown = False
            if prct <= 10 and len(cdata.pages) < 3 and not self.ignorescrollup and not cdata.proclock:
                self.mythread = threading.Thread(target=self.dopage, args=['up', 50])
                self.mythread.start()
                
        self.scrolld = e.props.value
        


    def isdate(self, datetime):
        return 'T'.split(datetime)[0] in self.dates

    def dopage(self, direction, count):
        """
        Builds a page of photos.

        Args:
            count (int): how many photos to return
            direction (string): whether we are scrolling up or down - impacts sql and sorting
        """
        print('>>>>>>>>>> dopage')

        cdata.proclock = True
        
        sp_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        spinner = Gtk.Spinner()
        sp_box.append(spinner)
        spinner.start()

        if direction == 'down':
            self.scrollpage.append(sp_box)
        else:
            self.scrollpage.prepend(sp_box)

        thispage = CphotosPage()
        ct = thispage.fillbox(direction, count)

        if direction == 'down':
            self.scrollpage.remove(self.scrollpage.get_last_child())
        else:
            self.scrollpage.remove(self.scrollpage.get_first_child())

        if ct:

            if direction == 'down':
                self.scrollpage.append(thispage)
                cdata.pages.append(cdata.datetimerange)
            else:
                self.scrollpage.prepend(thispage)
                cdata.pages.insert(0, cdata.datetimerange)
            if len(cdata.pages) == 3:
                print('>>> removing a page')
                if direction == 'down':
                    cva = self.scroll.get_child().get_vadjustment().get_value()
                    nva = cva - self.scrollpage.get_first_child().get_height()
                    self.scrollpage.remove(self.scrollpage.get_first_child())
                    self.scroll.get_child().get_vadjustment().set_value(nva)
                    del cdata.pages[0]
                else:
                    cva = self.scroll.get_child().get_vadjustment().get_value()
                    nva = cva + self.scrollpage.get_last_child().get_height()
                    self.scrollpage.remove(self.scrollpage.get_last_child())
                    self.scroll.get_child().get_vadjustment().set_value(nva)
                    del cdata.pages[-1]
                    
            # vadj = self.scroll.get_child().get_vadjustment()
            # vadj.set_value(0.5*(vadj.get_upper() - vadj.get_page_size()))
                
        else:
            if direction == 'down':
                self.ignorescrolldown = True
            else:
                self.ignorescrollup = True

        GObject.idle_add(self.pagedone)

    def pagedone(self):
        cdata.proclock = False
        self.mythread.join()

    def update(self):
        # https://docs.gtk.org/gtk3/method.Box.reorder_child.html
        cdata.updatecache()
        GObject.idle_add(self.updatedone)

    def updatedone(self):
        self.work_thread.join()

    def on_search_clicked(self, widget):
        # https://mail.gnome.org/archives/gtk-app-devel-list/2008-May/msg00056.html
        if widget.get_active():
            print("serachin' ;-)")
        else:
            print("not searchin' :-D")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cdata.initdb()
        self.scroll.get_child().get_vadjustment().connect('value_changed', self.scroll_notify_event, self)
        # self.scroll.connect('scroll-event', self.scroll_notify_event)
        # self.doindex()
        self.search_button.connect('toggled', self.on_search_clicked)
        thismap = Mapview()
        thismap.getPicsWithLocs()
        thismap.center_map()
        self.mapbox.append(thismap)
        thispage = CphotosPage()
        thispage.fillbox('down', 50)
        self.scrollpage.append(thispage)
        cdata.pages.append(cdata.datetimerange)
        
        
