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
    ignorescrolldown = False
    ignorescrollup = False
    
    

        
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
            dvs = 1
        prct = (e.props.value / (dvs)) * 100
        if e.props.value > self.scrolld:
            self.ignorescrollup = False
            if prct >= 90 and len(cdata.pages) < 3 and not self.ignorescrolldown:
                thispage = CphotosPage()
                ct = thispage.fillbox('down', 50)
                if ct:
                    self.scrollpage.append(thispage)
                    cdata.pages.append(cdata.datetimerange)
                    if len(cdata.pages) == 3:
                        print('>>> removing a top page')
                        # self.scrollpage.remove(self.scrollpage.get_first_child())
                        # vadj = self.scroll.get_child().get_vadjustment()
                        # vadj.set_value(0.5*(vadj.get_upper() - vadj.get_page_size()))
                        del cdata.pages[0]
                else:
                    self.ignorescrolldown = True
                    
                    
                
        if e.props.value < self.scrolld:
            self.ignorescrolldown = False
            if prct <= 10 and len(cdata.pages) < 3 and not self.ignorescrollup:
                thispage = CphotosPage()
                ct = thispage.fillbox('up', 50)
                if ct:
                    self.scrollpage.prepend(thispage)
                    cdata.pages.insert(0, cdata.datetimerange)
                    if len(cdata.pages) == 3:
                        print('>>> removing a bottom page')
                        # self.scrollpage.remove(self.scrollpage.get_last_child())
                        # vadj = self.scroll.get_child().get_vadjustment()
                        # vadj.set_value(0.5*(vadj.get_upper() - vadj.get_page_size()))
                        del cdata.pages[-1]
                else:
                    self.ignorescrollup = True
                
        self.scrolld = e.props.value
        


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
        thispage.fillbox('down', 50)
        self.scrollpage.append(thispage)
        cdata.pages.append(cdata.datetimerange)
        
        
