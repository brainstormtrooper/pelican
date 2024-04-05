import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Shumate', '1.0')
gi.require_version('Adw', '1')
from gi.repository import Shumate, Graphene
from gi.repository import Gtk, Adw

import os
from .dbase import db

from . import cdata

class Mapview:

    def __init__(self):
        # self.zl = 1
        self.rows = []
        self.squares = []
        self.locs = {}
        map_source = Shumate.MapSourceRegistry.new_with_defaults().get_by_id(Shumate.MAP_SOURCE_OSM_MAPNIK)
        self.widget = Shumate.SimpleMap()
        self.widget.set_map_source(map_source)

        self.viewport = self.widget.get_viewport()
        self.viewport.set_min_zoom_level(1)
        self.viewport.set_zoom_level(2)
        self.zl = int(self.viewport.get_zoom_level())
        self.viewport.connect('notify::zoom-level', self.on_zoom)
        self.marker_layer = Shumate.MarkerLayer.new(self.viewport)
        self.widget.add_overlay_layer(self.marker_layer)
        self.widget.set_vexpand(True)
        self.widget.set_hexpand(True)

    def do_group(self, w):
        print("clicked group")
        print(w.get_name())
        
        w.get_next_sibling().popup()

    def do_clicked(self, w):
        print("clicked")
        print(w.get_name())
        
        w.get_next_sibling().popup()
        
        os.system(f"xdg-open {w.get_name()}")
        
    def on_zoom(self, viewport, zoomlevel):
        if int(viewport.get_property(zoomlevel.name)) != self.zl:
            print("zoomed")
            print(viewport.get_property(zoomlevel.name))
            self.doGroupedPins(self.rows)
            self.zl = int(viewport.get_property(zoomlevel.name))

    def center_map(self):
        xs = []
        ys = []
        points = self.marker_layer.get_markers()
        for m in points:
            xs.append(m.get_latitude())
            ys.append(m.get_longitude())
        center = (sum(xs) / len(points), sum(ys) / len(points))
        self.widget.get_map().center_on(center[0], center[1])

    
    """
    DOESN'T WORK BECAUSE ALL MARKERS EXIST AND NO WAY TO KNOW WHETHER THEY ARE IN VIEW
    """
    def optimum_zoom(self, allvis = None):
        zl = self.viewport.get_zoom_level()
        viscount = 0
        # allvis = False
        widgets = self.marker_layer.get_markers()
        for w in widgets:
            if w.get_mapped():
                viscount += 1

        optimum = (allvis == False and viscount == len(widgets))
        print('optimizing')
        if viscount == len(widgets) and zl < self.viewport.get_max_zoom_level():
            self.viewport.set_zoom_level(zl + 1)
            if not optimum:
                self.optimum_zoom(True)
        if viscount < len(widgets) and zl > self.viewport.get_min_zoom_level():
            
            self.viewport.set_zoom_level(zl - 1)
            if not optimum:
                self.optimum_zoom(False)
        

    def get_square_plot(self, x, y, side):
        return [(x-(side/2), y+(side/2)), (x+(side/2), y+(side/2)), (x-(side/2), y-(side/2)), (x+(side/2), y-(side/2))]

    def is_in_square(self, x, y, square):
        insquare = False
        tl = square[0]
        tr = square[1]
        bl = square[2]
        br = square[3]
        insquare = (x >= tl[0] and x <= tr[0]) and (y >= bl[1] and y <= tl[1])
        return insquare

    def getPicsWithLocs(self):
        db3 = db()
        self.rows = db3.getPicsWithLocs()

        self.doGroupedPins(self.rows)
        """
        for rec in rows:

            if (rec[2], rec[3]) not in self.locs.keys():
                self.locs[(rec[2], rec[3])] = [ os.path.join(rec[1], rec[0]) ]
            else:
                self.locs[(rec[2], rec[3])].append(os.path.join(rec[1], rec[0]))
        """

    def doGroupedPins(self, rows):
        self.marker_layer.remove_all()
        self.squares = []
        side = 24
        for rec in rows:
            mysq = -1
            tmppin = Shumate.Point()
            tmppin.set_location(rec[2], rec[3])
            # tmpimg = Gtk.Image(icon_name = 'view-pin-symbolic')
            # tmppin.set_child(tmpimg)
            tmppos = self.viewport.location_to_widget_coords(tmppin, rec[2], rec[3])
            # print(tmppos)
            tmpsqr = self.get_square_plot(int(tmppos.x), int(tmppos.y), side)
            tmpobj = {
                'lat': rec[2],
                'lon': rec[3],
                'path': os.path.join(rec[1], rec[0])
            }
            for k, sq in enumerate(self.squares):
                if self.is_in_square(tmppos.x, tmppos.y, sq['rect']):
                    sq['obs'].append(tmpobj)
                    mysq = k
                    break
            if mysq == -1:
                myob = {
                    'sloc' : (rec[2], rec[3]),
                    'rect': tmpsqr,
                    'obs' : [ tmpobj ]
                }
                self.squares.append(myob)



        for k, sqob in enumerate(self.squares):
            if len(sqob['obs']) == 1:
                # only one location, so no group
                print('>>> PIN at : ', sqob['obs'][0]['lat'],  sqob['obs'][0]['lon'])
                mypin = Shumate.Point()
                mybtn = Gtk.Button(icon_name = 'view-pin-symbolic')
                mybtn.connect('clicked', self.do_clicked)
                mybtn.set_name(sqob['obs'][0]['path'])
                pop = Gtk.Popover()
                # pop.set_pointing_to(mybtn.compute_bounds(widget))
                pop.set_child(Gtk.Label(label = mybtn.get_name()))
            
                box = Gtk.Box(orientation = 'vertical')
                box.append(mybtn)  
                box.append(pop)
                
                
                mypin.set_child(box)
                
                mypin.set_location(sqob['obs'][0]['lat'],  sqob['obs'][0]['lon'])
                self.marker_layer.add_marker(mypin)
            else:
                # we have a group
                print('>>> GROUP at ', sqob['sloc'])
                mypin = Shumate.Point()
                mybtn = Gtk.Button(label = 'group')
                mybtn.connect('clicked', self.do_group)
                
                mybtn.set_name(str(k))
                listbox = Gtk.Box(orientation = 'vertical')
                for ob in sqob['obs']:
                    l = Gtk.Label(label = ob['path'])
                    listbox.append(l)
                pop = Gtk.Popover()
                pop.set_child(listbox)
                mypin.set_location(sqob['sloc'][0], sqob['sloc'][1])
                box = Gtk.Box(orientation = 'vertical')
                box.append(mybtn)  
                box.append(pop)
                mypin.set_child(box)
                self.marker_layer.add_marker(mypin)

        


         


    
    def doPins(self):
        for coords, pics in self.locs.items():
            if len(pics) == 1:
                mypin = Shumate.Point()
                mybtn = Gtk.Button(icon_name = 'view-pin-symbolic')
                mybtn.connect('clicked', self.do_clicked)
                mybtn.set_name(pics[0])
                pop = Gtk.Popover()
                # pop.set_pointing_to(mybtn.compute_bounds(widget))
                pop.set_child(Gtk.Label(label = mybtn.get_name()))
            
                box = Gtk.Box(orientation = 'vertical')
                box.append(mybtn)  
                box.append(pop)
                
                
                mypin.set_child(box)
                
                mypin.set_location(coords[0], coords[1])
                self.marker_layer.add_marker(mypin)
            else:
                mypin = Shumate.Point()
                mybtn = Gtk.Button(label = 'group')
                mybtn.connect('clicked', self.do_group)
                mypin.set_child(mybtn)
                mybtn.set_name(f"{coords[0]},{coords[1]}")
                mypin.set_location(coords[0], coords[1])
                self.marker_layer.add_marker(mypin)
        
        