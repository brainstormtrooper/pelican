import os
import hashlib
from PIL import Image, ExifTags, TiffImagePlugin
from datetime import datetime, timezone


class local:

    def __init__(self, photospath, filename):
        self.exists = False
        self.filepath = None
        self.filehash = None
        self.exif = None
        self.lat = None
        self.lon = None
        self.alt = None
        self.dir = None
        self.createdDate = None
        self.model = None

        self.doExists(photospath, filename)
        if self.exists:
            self.doHash()
            self.doExtractExif()
            self.doExtractCoords()
            self.doCreatedDate()



    def doExists(self, photospath, filename):
        res = False
        filepath = None
        fpath = os.path.join(photospath, filename)
        if os.path.isfile(fpath):
            res = True
            filepath = fpath
        self.exists = res
        self.filepath = filepath

    def doHash(self):
        fileHash = ''
        with open(self.filepath, 'rb') as toHash:
            hash_md5 = hashlib.md5()
            for chunk in iter(lambda: toHash.read(4096), b""):
                hash_md5.update(chunk)
            fileHash = hash_md5.hexdigest()
        self.filehash = fileHash
    
    def doExtractExif(self):
        img = Image.open(self.filepath)
        exifitems = img._getexif()
        if exifitems:
            self.exif = { ExifTags.TAGS[k]: self.safeType(v) for k, v in exifitems.items() if k in ExifTags.TAGS }
            gpsinfo = {}
            if 'GPSInfo' in self.exif:
                for key in self.exif['GPSInfo'].keys():
                    decode = ExifTags.GPSTAGS.get(key,key)
                    v = self.safeType(self.exif['GPSInfo'][key])
                    gpsinfo[decode] = v
                self.exif['GPSInfo'] = gpsinfo

    def doCreatedDate(self):
        if self.exists:
            dt = datetime.fromtimestamp(os.path.getmtime(self.filepath), timezone.utc)
            
            if self.exif and 'DateTime' in self.exif:
                sub = self.exif['SubsecTime'] if 'SubsecTime' in self.exif else '000000'
                if len(sub) == 3:
                    sub = sub + '000'
                offset = self.exif['OffsetTime'].replace(':', '') if 'OffsetTime' in self.exif else '+0000'
                dt = datetime.strptime(f"{self.exif['DateTime']}.{sub}{offset}", '%Y:%m:%d %H:%M:%S.%f%z')

            self.createdDate = dt.isoformat(timespec='microseconds')

    def doExtractCoords(self):
        if self.exif and 'GPSInfo' in self.exif:
            gpsinfo = self.exif['GPSInfo']
            lat = None
            lon = None
            alt = None
            direction = None
            try:
                alt = gpsinfo['GPSAltitude']
                direction = gpsinfo['GPSImgDirection']
                lat = float(gpsinfo['GPSLatitude'][0] + (gpsinfo['GPSLatitude'][1]/60) + (gpsinfo['GPSLatitude'][2]/3600))
                lon = float(gpsinfo['GPSLongitude'][0] + (gpsinfo['GPSLongitude'][1]/60) + (gpsinfo['GPSLongitude'][2]/3600))
                if gpsinfo['GPSLatitudeRef'] != 'N':
                    lat = -lat
                if gpsinfo['GPSLongitudeRef'] != 'E':
                    lon = -lon
            except Exception as e:
                print(e)
            self.alt = alt
            self.dir = direction
            self.lat = lat
            self.lon = lon

    def doExtractModel(self):
        pass 

    def getThumbnail(self):
        res = None
        if self.exists:
            img = Image.open(self.filepath)
            img.thumbnail((250, 250))
            res = img
        return res
    
    def getCreatedDate(self):
        return self.createdDate

    def getFileHash(self):
        return self.filehash

    def getModel(self):
        return 'test model'
    
    def getCoordinates(self):
        return self.lat, self.lon, self.alt, self.dir
    
    def getExists(self):
        return self.exists

    def getIsHash(self, myhash):
        return myhash == self.filehash

    def safeType(self, v):
        try:
            v = v.decode()
        except (UnicodeDecodeError, AttributeError):
            if type(v) is TiffImagePlugin.IFDRational:
                v = int(v)
        if type(v) is tuple:
            v = [float(i) for i in v]
        return v