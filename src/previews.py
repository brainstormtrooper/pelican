import os
import io
from datetime import datetime, timezone
import gi

gi.require_version('WebKit2', '5.0')
from gi.repository import Gtk, GLib, Gio, WebKit2

class preview:

    def __init__(self, id, filename, filepath, takendate, thumbnail, name, town):
        # id, filename, filepath, takendate, cachepath
        
        self.id = id
        self.thumbnailbytes = thumbnail
        # self.previewpath = os.path.join(cachepath, 'previews', id)
        # self.exists = os.path.isfile(self.previewpath)
        self.filename = filename
        self.takendate = takendate
        self.timestamp = datetime.strptime(self.takendate, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp()
        self.placename = name
        self.town = town

    
    def getwidget(self):
        res = None
        # file = Gio.MemoryInputStream.new_from_data(self.thumbnailbytes, None)
        # gdata = GdkPixbuf.Pixbuf.new_from_stream_at_scale(file, 250, 250, True)
        picBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, hexpand=False)
        picBox.set_size_request(250, 250)
        picBox.set_name(self.id)
        webview = WebKit2.WebView()
        # gtk_image = Gtk.Image.new_from_pixbuf(gdata)
        webview.set_size_request(250, 250)
        webview.load_bytes(GLib.Bytes.new(self.thumbnailbytes), 'image/webp', None, None)
        picBox.append(webview)
        res = picBox

        return res