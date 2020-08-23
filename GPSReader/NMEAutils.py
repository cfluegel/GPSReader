# -*- coding: ascii -*-

import math

############################################################################
# Helper functions
############################################################################
def CreateNMEAChkSum(sentence=None):
  """ Calculates the XOR Checksum of a NMEA sentence, but only
  between the $ and *"""

  if sentence == None:
    return None
  elif (sentence[0] == "$") and (sentence[-3] == "*"):
    t = sentence[1:-3]
    sentence = t
  elif (sentence[0] == "$") and (sentence[-1] == "*"):
    t = sentence[1:-1]
    sentence = t
  elif (sentence[0] == "$"):
    t = sentence[1]
    sentence = t

  i = int(0)
  XOR = int(0)
  ilen = long()
  ilen = len(sentence)

  for i in range(0,len(sentence)):
    XOR = XOR ^ ord(sentence[i])

  if (XOR <= 15):
    return "0"+str(hex(XOR))[-1:]
  else:
    return str(hex(XOR))[-2:]
# CreateNMEAChkSum

def VerifyNMEAChkSum(sentence=None):
  """ Checks the XOR Checksum with the transmitted checksum """
  if sentence == None:
    return None

  Checksum = str(sentence[-2:])
  GenChecksum = CreateNMEAChkSum(sentence)

  if (Checksum.upper() == GenChecksum.upper()):
    return True
  return False
# VerifyNMEAChkSum

def convertKMHToKnots(kmh=0.0):
  if kmh == 0.0:
    return 0.0

  try:
    return kmh * 0.5399568034557235
  except TypeError:
    return 0.0
# convertKMHToKnots

def convertKnotsToKMH(knots=0.0):
  if knots == 0.0:
    return 0.0

  try:
    return knots * 1.852
  except TypeError:
    return 0.0
# convertKnotsToKMH

def parseLatitude(lat, ns):
  """ Convert a latitude with N/S indication to a positive or negative latitude """

  try:
    lat_in = float(lat)
  except:
    lat_in = 0.0

  # copied from another class
  if ns == 'S':
    lat_in = -lat_in

  latitude_degrees = int(lat_in/100)
  latitude_minutes = lat_in - latitude_degrees*100
  latitude = latitude_degrees + (latitude_minutes/60)

  return latitude
# parseLatitude

def parseLongitude(lon, ew):
  """ Convert a longitude with E/W indication to a pos or neg longitude """
  try:
    lon_in = float(lon)
  except:
    lon_in = 0.0

  # copied from another class
  if ew == 'W':
    lon_in = -lon_in

  longitude_degrees = int(lon_in/100)
  longitude_minutes = lon_in - longitude_degrees*100
  longitude = longitude_degrees + (longitude_minutes/60)

  return longitude
# parse Longitude


def estimateDirection(CurrentCourse,DestCourse):
  """ returns the positive or negative value in which direction one have
  to steer to get on the course to the target. """

  CourseCorrection = DestCourse - CurrentCourse
  if (CourseCorrection == 180):
    return 180
  if (CourseCorrection > 180):
    return -(360 - CourseCorrection)
  else:
    return CourseCorrection
# estimateDirection


class GPSPosition(object):
  R = long(6378137.0)  # Aequatorradius der Erde in Kilometer in Meter

  def __init__(self, ilat, ilon):
    # TODO: Different Error Handling. Raise error message instead of checking the
    #       variables for correctnes.
    self.latitude =None
    self.longitude = None

    if isinstance(ilat, tuple):
      self.latitude = parseLatitude( ilat[0], ilat[1] )

    if isinstance(ilon, tuple):
      self.longitude = parseLongitude( ilon[0], ilon[1] )

    if (isinstance(ilon, float) or isinstance(ilon, long)) and ((ilon <= 180) and (ilon >= -180)):
      self.longitude = ilon

    if (isinstance(ilat, float) or isinstance(ilat, long)) and ((ilat >= -90) and (ilat <= 90)):
      self.latitude = ilat


  def calculateBearing(self, destination):
    """ calculateBearing - Returns the true course of the destination

    Based on the following websites and some information of a colleague
      - http://williams.best.vwh.net/avform.htm#Crs
      - http://www.movable-type.co.uk/scripts/latlong.html"""


    if not isinstance(destination, GPSPosition):
      raise Exception("ERROR: Destinationparameter has to be an instance of GPSPosition!")
    if (destination.latitude == None) or (destination.longitude == None):
      raise Exception("ERROR: Destinationparamter does not have a valid position!")
    if (self.latitude == None) or (self.longitude == None):
      raise Exception("ERROR: This instance does not have a valid position!")

    SLat = long()
    SLong = long()
    ZLat = long()
    ZLong = long()

    SLat = math.radians(self.latitude)
    SLong = math.radians(self.longitude)
    ZLat = math.radians(destination.latitude)
    ZLong = math.radians(destination.longitude)

    # http://williams.best.vwh.net/avform.htm
    y = math.sin( ZLong - SLong ) * math.cos(ZLat)
    x = (math.cos(SLat)*math.sin(ZLat)) - math.sin(SLat)*math.cos(ZLat)*math.cos(ZLong - SLong)

    return ( math.degrees(math.atan2(y,x)) + 360 ) % 360

  def calculateDistance(self, destination):
    """ calculateDistance - Distance betweeen this object and the other object

    This calculations are based on the following websites and information:
    URL: http://de.wikipedia.org/wiki/Orthodrome"""
    if not isinstance(destination, GPSPosition):
      raise Exception("ERROR: Destinationparameter has to be an instance of GPSPosition!")
    if (destination.latitude == None) or (destination.longitude == None):
      raise Exception("ERROR: Destinationparamter does not have a valid position!")
    if (self.latitude == None) or (self.longitude == None):
      raise Exception("ERROR: This instance does not have a valid position!")

    sf = long()           # Abplattung der Erde
    sa = long(self.R)  # Aequatorradius der Erde in Kilometer
    cF = long()
    cG = long()
    sl = long()
    cS = long()           # Bestimmung des groben Abstands D
    cC = long()           # Bestimmung des groben Abstands D
    sw = long()           # Bestimmung des groben Abstands D
    cD = long()           # Abstand D
    cR = long()
    cH1 = long()          # Korrekturfaktor H1
    cH2 = long()          # Korrekturfaktor H2

    sf = 1 / 298.257223563    # WGS84 Referenzellipsoid zugrunde gelegt

    cF = (self.latitude + destination.latitude) / 2.0
    cG = (self.latitude - destination.latitude) / 2.0
    sl = (self.longitude - destination.longitude) / 2.0
    cF = math.radians(cF)
    cG = math.radians(cG)
    sl = math.radians(sl)

    cS =  ((math.sin(cG)**2) * (math.cos(sl)**2)) + ((math.cos(cF)**2)  * (math.sin(sl)**2))
    cC =  ((math.cos(cG)**2) *  (math.cos(sl)**2)) + ((math.sin(cF)**2) * (math.sin(sl)**2))

    sw = math.atan( math.sqrt(cS / cC) )
    cD = (2 * sw * sa)

    try:
      cR = math.sqrt(cS * cC) / sw
    except ZeroDivisionError:
      return 0.0

    cH1 = (3 * cR - 1) / (2 * cC)
    cH2 = (3 * cR + 1) / (2 * cS)

    # Entfernung in Metern / distance in meters
    return cD * (1 + sf * cH1 * (math.sin(cF)**2) * (math.cos(cG)**2) - sf * cH2 * (math.cos(cF)**2) * (math.sin(cG)**2) )

  def projectGPSPosition(self, distance, direction):
    """ This function projects a new waypoint from a GPS position. The method needs a speed (in knots) and a course. """ 

    # not yet ready!
    pass

  def __getitem__(self,i):
    """ In case one want to try this object as an array (<Objekt>[i]). """
    if (i == 0):
      return     self.latitude
    elif (i == 1):
      return self.longitude
    else:
      raise IndexError("No such index available!")

##################### Test section ###########################################
if __name__ == '__main__':
  t1 = GPSPosition((5336.3190,"N"),  6.4325416563436667)
  t2 = GPSPosition((5336.3190,"N"),  6.4325416563436667)
  print  t1.calculateBearing(t2)
  print "----------------------------"
  print t1.calculateDistance(t2)
  print "----------------------------"

  t3 = GPSPosition((5333.276,"N"), (959.707,"E"))
  print t3.latitude, t3.longitude
  t4 = GPSPosition(52.515735, 13.369744)
  print t4.latitude, t4.longitude
  print "----------------------------"
  print t3.calculateBearing(t4)
  print t3.calculateDistance(t4) / 1000
  print "----------------------------"
  print "only by item id"
  print t3[0]
  print t3[1]
  print "----------------------------"
  # print t3[2]
  print "----------------------------"
  print parseLatitude("5336.3190","")
  print "----------------------------"
  print convertKMHToKnots(1)
  print convertKMHToKnots(2)
  print convertKMHToKnots("sdfsdf")
  # convertKnotsToKMH
  print convertKnotsToKMH(1)
  print convertKnotsToKMH(2)
  print convertKnotsToKMH("foooar")

