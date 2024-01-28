import os
from datetime import datetime, timezone
from gi.repository import Gtk, GLib, GdkPixbuf

class preview:

    def __init__(self, id, filename, filepath, takendate, cachepath):
        # id, filename, filepath, takendate, cachepath
        
        self.id = id
        self.previewpath = os.path.join(cachepath, 'previews', id)
        self.exists = os.path.isfile(self.previewpath)
        self.filename = filename
        self.takendate = takendate
        self.timestamp = datetime.strptime(self.takendate, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()

    
    def getwidget(self):
        res = None
        if self.exists:
            gdata = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.previewpath, 250, 250, True)
            picBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            picBox.set_size_request(250, 250)
            picBox.set_name(self.id)
            gtk_image = Gtk.Image.new_from_pixbuf(gdata)
            gtk_image.set_size_request(250, 250)
            picBox.append(gtk_image)
            res = picBox

        return res