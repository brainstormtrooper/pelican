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

from gi.repository import Adw
from gi.repository import Gtk, GLib, GdkPixbuf
# from PIL import Image

from .cdata import *

@Gtk.Template(resource_path='/com/github/brainstormtrooper/cphotos/window.ui')
class CphotosWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'CphotosWindow'

    flow = Gtk.Template.Child()

    def fillbox(self):

        tns = get100pics()

        for tn in tns:
            fpath = getcacheloc(tn)
            if os.path.isfile(fpath):
                gdata = GdkPixbuf.Pixbuf.new_from_file_at_scale(fpath, 250, 250, True)
                picBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                picBox.set_size_request(250, 250)

                gtk_image = Gtk.Image.new_from_pixbuf(gdata)
                gtk_image.set_size_request(250, 250)
                picBox.append(gtk_image)
                # label = Gtk.Label(label=text)
                self.flow.append(picBox)

        updatecache()



    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fillbox()
        
