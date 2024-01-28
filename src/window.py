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
from gi.repository import Adw
from gi.repository import Gtk, GLib, GdkPixbuf, GObject
# from PIL import Image

from .cdata import *

@Gtk.Template(resource_path='/com/github/brainstormtrooper/cphotos/window.ui')
class CphotosWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CphotosWindow'

    scroll = Gtk.Template.Child()
    flow = Gtk.Template.Child()
    scrolld = 0
    dates = []
    page = []
    topdatetime = None
    bottomdatetime = None

    def fillbox(self, direction = 'down', datelimit = None, qty = 100):
        print('fillbox?')
        if not self.page:
            print('yes')
            self.picsthread = threading.Thread(target=self.getpics, args=[self.page, direction, datelimit, qty])
            self.picsthread.start()

        
    def doindex(self):
        self.work_thread = threading.Thread(target=self.update)
        self.work_thread.start()
        # GObject.timeout_add(1, 200, )


    def getpics(self, pagelist, direction = 'down', datelimit = None, qty = 100):
        get100pics(pagelist, direction, datelimit, qty)
        GObject.idle_add(self.fetchdone, direction)


    """
    Adds found thumb widgets to page.
    Should avoid duplicates
    """
    def fetchdone(self, direction):
        if self.page:
            self.bottomdatetime = self.page[-1].takendate
            self.topdatetime = self.page[0].takendate
            if direction == 'down':
                for tn in self.page[:]:
                    # fpath = getcacheloc(tn)
                    self.flow.append(tn.getwidget())
                    self.page.remove(tn)
            else:
                for tn in self.page[:]:
                    # fpath = getcacheloc(tn)
                    self.flow.prepend(tn.getwidget())
                    self.page.remove(tn)
        print(self.page)

    """
    If 2/3 up or down, trigger query for next pagelaod of pics in right direction
    """
    def scroll_notify_event(w, e, self):
        prct = (e.props.value / (e.props.upper - e.props.page_size)) * 100
        
        if e.props.value > self.scrolld:
            d = 'down'
            if prct >= 75:
                self.fillbox(d, self.bottomdatetime, 5)
        else:
            d = 'up'
            if prct <= 25:
                self.fillbox(d, self.topdatetime, 5)
        self.scrolld = e.props.value
        


    def isdate(self, datetime):
        return 'T'.split(datetime)[0] in self.dates

    def dodatepage(self):
        pass


    def update(self):
        # https://docs.gtk.org/gtk3/method.Box.reorder_child.html
        updatecache()
        GObject.idle_add(self.updatedone)

    def updatedone(self):
        self.work_thread.join()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        initdb()
        self.scroll.get_child().get_vadjustment().connect('value_changed', self.scroll_notify_event, self)
        # self.scroll.connect('scroll-event', self.scroll_notify_event)
        self.doindex()
        self.fillbox()
        
