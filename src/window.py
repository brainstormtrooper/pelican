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
from gi.repository import Adw
from gi.repository import Gtk, GLib, GdkPixbuf, GObject
# from PIL import Image

from . import cdata

@Gtk.Template(resource_path='/com/github/brainstormtrooper/cphotos/window.ui')
class CphotosWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CphotosWindow'

    scroll = Gtk.Template.Child()
    scrollpage = Gtk.Template.Child()
    scrolld = 0
    pages = []
    topdatetime = None
    bottomdatetime = None
    
    

        
    def doindex(self):
        self.work_thread = threading.Thread(target=self.update)
        self.work_thread.start()
        # GObject.timeout_add(1, 200, )


    """
    If 2/3 up or down, trigger query for next pagelaod of pics in right direction
    """
    def scroll_notify_event(w, e, self):
        dvs = e.props.upper - e.props.page_size
        if dvs == 0:
            dvs = 0.1
        prct = (e.props.value / (dvs)) * 100
        if e.props.value > self.scrolld:
            if prct >= 75 and len(self.pages) < 3 and not cdata.proclock:
                thispage = CphotosPage()
                thispage.fillbox('down', 5)
                self.scrollpage.append(thispage)
                self.pages.append('bob')
                if len(self.pages) == 3:
                    self.scrollpage.remove(self.scrollpage.get_first_child())
                    del self.pages[0]
                
        if e.props.value < self.scrolld:
            if prct <= 25 and len(self.pages) < 3 and not cdata.proclock:
                thispage = CphotosPage()
                thispage.fillbox('up', 5)
                self.scrollpage.prepend(thispage)
                self.pages.insert(0, 'bob')
                if len(self.pages) == 3:
                    self.scrollpage.remove(self.scrollpage.get_last_child())
                    del self.pages[-1]
                
        self.scrolld = e.props.value
        
    def pageblock(self):
        

        pass

    def isdate(self, datetime):
        return 'T'.split(datetime)[0] in self.dates


    def update(self):
        # https://docs.gtk.org/gtk3/method.Box.reorder_child.html
        cdata.updatecache()
        GObject.idle_add(self.updatedone)

    def updatedone(self):
        self.work_thread.join()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        cdata.initdb()
        self.scroll.get_child().get_vadjustment().connect('value_changed', self.scroll_notify_event, self)
        # self.scroll.connect('scroll-event', self.scroll_notify_event)
        self.doindex()
        thispage = CphotosPage()
        thispage.fillbox('down', 5)
        self.scrollpage.append(thispage)
        
        
