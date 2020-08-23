# -*- coding: ascii -*-

#### Importbereich
import serial

import time, sys
import threading

import NMEAtelegrams, NMEAutils
from GPSError import *

valid_baudrates = (4800, 9600, 19200, 38400, 57600, 115200)

#### GPS Main class
class GPSReader(threading.Thread, object):
  """ GPSReader - Handles the communication with a GPS reader of a phy or virt interface

  This class connects to a virt or phy serial interface and reads different NMEA sentence.
  Currently the following NMEA sentences will be converted to different classes: GGA, RMC, VTG
  but more are planed.

  At the moment there are no plans to communicate two-way with a GPS receiver. """
  def __init__(self, comport=None, baudr=4800):
    self._SerialObj = None
    self._rawdata = None
    self._stop = threading.Event()

    self.setBaudrate(baudr)

    self.GGA = NMEAtelegrams.NMEA_GGA()
    self.VTG = NMEAtelegrams.NMEA_VTG()
    self.RMC = NMEAtelegrams.NMEA_RMC()
    self.GLL = NMEAtelegrams.NMEA_GLL()
    self.DTM = NMEAtelegrams.NMEA_DTM()
    self.GSV = NMEAtelegrams.NMEA_GSV()

    # TODO: Add the GSV Sentence to this as well. Gonna need to rethink the way I handle
    # the read of the serial buffer.

    # No serial port? Error!
    if (comport == None):
      raise GPSCommError()
    self.connectToComport(comport)

    # let the __init__ of threading do some work :)
    threading.Thread.__init__(self)

    # Start the thread automatically
    self.daemon = True
    self.start()

  def __del__(self):
    # Master, shall I remove the connection the serial interface? Yes, you dummy!
    self.disconnect()

  def setBaudrate(self, baudrate):
    """ Sets Baudrate to da desired value. Bogus values will not be used """
    if baudrate in valid_baudrates:
      self._baudrate = baudrate
    else:
      self._baudrate = 4800

  def connectToComport(self, comport):
    """ Opens the comport with a baudrate of 4800 if it hasn't been changed and a timeout of 10seconds
    or throw a execption if no connection can be established. """
    try:
      self._SerialObj = serial.Serial(port=comport, baudrate=self._baudrate, timeout=10)
    except serial.SerialException:
      raise GPSCommError("Connection with Comport failed!")

  def disconnect(self):
    """ Closes the connection to the serial interface """
    if self._SerialObj <> None:
      self._SerialObj.close()

  def isConnected(self):
    """ Wrapper for the actual isOpen() of pyserial """
    if self._SerialObj <> None:
      return self._SerialObj.isOpen()

  def stop_thread(self):
    """ Stop the thread flag which is herewith set """
    self._stop.set()

  def join(self, timeout=None):
    self._stop.set()
    threading.Thread.join(self,timeout)

  def getRawdata(self):
    """ Lets you watch the rawdata in case something is bothering you :D"""
    return self._rawdata

  def run(self):
    """ threading.Thread.run() overloaded. Here the actual stuff is going on.

    Converts the different NMEA sentences into seperated classes which allow one
    better access to the different sentences. The classes have different methodes
    to access the fields."""
    # TODO: Do I really need to positions where the variables are initialized?
    # Also, add the GSV to this or the above initialization.
    self.GGA = NMEAtelegrams.NMEA_GGA()
    self.VTG = NMEAtelegrams.NMEA_VTG()
    self.RMC = NMEAtelegrams.NMEA_RMC()
    self.GLL = NMEAtelegrams.NMEA_GLL()
    self.DTM = NMEAtelegrams.NMEA_DTM()
    self.GSV = NMEAtelegrams.NMEA_GSV()

    while True:
      if (self._stop.isSet()):
        self.disconnect()
        break

      # Get a complete line from the internal serial buffer. In respect to the NMEA EOL
      t_sentence = self._SerialObj.readline().strip("\r\n")
      if len(t_sentence) > 0:
        self._rawdata = t_sentence  # Store the Raw Sentence for debugging purpose.

        # This will analyze the sentence (check the checksum) and try to use the sentence rules to parse
        # the sentence into the different objects.
        if ( ("VTG" in t_sentence) and (NMEAutils.VerifyNMEAChkSum(t_sentence) == True) ):
         self.VTG.parseSentence(t_sentence)
        elif ( ("RMC" in t_sentence) and (NMEAutils.VerifyNMEAChkSum(t_sentence) == True) ):
          self.RMC.parseSentence(t_sentence)
        elif ( ("GLL" in t_sentence) and (NMEAutils.VerifyNMEAChkSum(t_sentence) == True) ):
          self.GLL.parseSentence(t_sentence)
        elif ( ("GGA" in t_sentence) and (NMEAutils.VerifyNMEAChkSum(t_sentence) == True) ):
          self.GGA.parseSentence(t_sentence)
        elif ( ("DTM" in t_sentence) and (NMEAutils.VerifyNMEAChkSum(t_sentence) == True) ):
          self.DTM.parseSentence(t_sentence)
        elif ( ("GSV" in t_sentence) and (NMEAutils.VerifyNMEAChkSum(t_sentence) == True) ):
          self.GSV.parseSentence(t_sentence)

###### TEST #######
# section in where I test most stuff of the current module until I figured out the nose or other
# unittests are working.
if __name__ == '__main__':
  try:

    test = GPSReader("/dev/ttyACM0", 115200)
    counter = 0
    while (True and test.isAlive()):
      # print test.getRawdata()
      try:
        print "VTG - Course: ", test.VTG.getCourse()
        print "VTG - Speed: ", test.VTG.getSpeed()
        print
        print "RMC - Position: ", test.RMC.getPosition().latitude, test.RMC.getPosition().longitude
        print "RMC - TimeDate: ", test.RMC.getTimeDate()
        print "RMC - Course: ", test.RMC.getCourse()
        print "RMC - Speed:", test.RMC.getSpeed()
        print
        print "GLL - Position: ", test.GLL.getPosition().latitude, test.GLL.getPosition().longitude
        print "GLL - Time: ", test.GLL.getTime()
        print
        print "GGA - Position: ", test.GGA.getPosition().latitude, test.GGA.getPosition().longitude
        print "GGA - Time: ", test.GGA.getTime()
        print "GGA - AntennaHeight: ", test.GGA.getAntennaHeight()
        print
      except NMEANoValidFix:
        print "No Fix!"
      except AttributeError:
        print "None type... need to fix"

      time.sleep(0.5)
  except GPSCommError as e :
     print "some error occured during the start "
     print "it says: ",  e
     sys.exit(3)
  except KeyboardInterrupt:
    test.disconnect()

  sys.exit(0)
