import os
import io
from datetime import datetime, timezone
from PIL import Image
import gi

# gi.require_version('WebKit2', '5.0')
from gi.repository import Gtk, GLib, Gio, GdkPixbuf

class preview:

    def __init__(self, id, filename, filepath, takendate, name, town):
        # id, filename, filepath, takendate, cachepath
        
        self.id = id
        # self.thumbnailbytes = thumbnail
        self.filepath = filepath
        # self.previewpath = os.path.join(cachepath, 'previews', id)
        
        self.filename = filename
        self.exists = os.path.isfile(os.path.join(self.filepath, self.filename))
        self.takendate = takendate
        self.timestamp = datetime.strptime(self.takendate, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()
        self.placename = name
        self.town = town

    
    def getwidget(self):
        res = None
        thumbbytes = self.getThumbnail()
        if thumbbytes:
            file = Gio.MemoryInputStream.new_from_data(thumbbytes)
            # file = Gio.MemoryInputStream.new_from_file(os.path.join(self.filepath, self.filename))
            # gdata = GdkPixbuf.Pixbuf.new_from_stream_at_scale(file, 250, 250, True)
            gdata = GdkPixbuf.Pixbuf.new_from_stream(file)
            picBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, hexpand=False)
            picBox.set_size_request(250, 250)
            picBox.set_name(self.id)
            # webview = WebKit2.WebView()
            gtk_image = Gtk.Image.new_from_pixbuf(gdata)
            gtk_image.set_size_request(250, 250)
            # webview.set_size_request(250, 250)
            # webview.load_bytes(GLib.Bytes.new(self.thumbnailbytes), 'image/webp', None, None)
            picBox.append(gtk_image)
            res = picBox

        return res

    def getThumbnail(self):
        res = None
        if self.exists:
            try:
                img = Image.open(os.path.join(self.filepath, self.filename))
                img.thumbnail((250, 250))
                imgba = io.BytesIO()
                img.save(imgba, format='jpeg')
                res = imgba.getvalue()
            except Exception as e:
                print(e)
        return res