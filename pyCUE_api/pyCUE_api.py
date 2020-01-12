from collections import namedtuple
from ctypes import Structure, CDLL, c_double, c_int, c_bool, c_char_p, byref, POINTER
from operator import attrgetter

class _CorsairDeviceInfo(Structure):
    """
    Structure containing device info
    """
    __slots__ = [
        "type",
        "model",
        "physicalLayout",
        "logicalLayout",
        "capsMask",
        "ledsCount"
    ]

    _fields_ = [
        ("type", c_int),
        ("model", c_char_p),
        ("physicalLayout", c_int),
        ("logicalLayout", c_int),
        ("capsMask", c_int),
        ("ledsCount", c_int)
    ]

class CorsairDeviceInfo(namedtuple('CorsairDeviceInfo', _CorsairDeviceInfo.__slots__)):

    def __new__(cls, dev_info):
        """
        Args:
            dev_info (_CorsairDeviceInfo): Structure containing device info
        Returns:
            CorsairDeviceInfo: namedtuple containing device info
        """
        #dev_type = CDT(dev_info.type)
        dev_type = dev_info.type
        dev_model = dev_info.model.decode()
        dev_pl = dev_info.physicalLayout
        dev_ll = dev_info.logicalLayout
        dev_cm = dev_info.capsMask
        dev_ledscount = dev_info.ledsCount
        return super(CorsairDeviceInfo, cls).__new__(cls, dev_type, dev_model, dev_pl, dev_ll, dev_cm, dev_ledscount)

class CorsairLedColor(Structure):
    """
    Structure representing a LED color
    """
    __slots__ = [
        "ledId",
        "r",
        "g",
        "b"
    ]

    _fields_ = [
        ("ledId", c_int),
        ("r", c_int),
        ("g", c_int),
        ("b", c_int)
    ]

    def __init__(self, led_id, r, g, b):
        """
        Args:
            led_id (int): The LED id you want to set
            r (int): Red component value
            g (int): Green component value
            b (int): You guessed it! Blue component value
        """
        super(CorsairLedColor, self).__init__(led_id, r, g, b)

class _CorsairProtocolDetails(Structure):
    """
    Structure representing protocol details
    """
    __slots__ = [
        "sdkVersion",
        "serverVersion",
        "sdkProtocolVersion",
        "serverProtocolVersion",
        "breakingChanges"
    ]

    _fields_ = [
        ("sdkVersion", c_char_p),
        ("serverVersion", c_char_p),
        ("sdkProtocolVersion", c_int),
        ("serverProtocolVersion", c_int),
        ("breakingChanges", c_bool)
    ]

class _CorsairLedPosition(Structure):
    """
    Structure representing a LED position
    """
    __slots__ = [
        "ledId",
        "top",
        "left",
        "height",
        "width"
    ]

    _fields_ = [
        ("ledId", c_int),
        ("top", c_double),
        ("left", c_double),
        ("height", c_double),
        ("width", c_double)
    ]


class CorsairLedPosition(namedtuple('CorsairLedPosition', _CorsairLedPosition.__slots__)):

    def __new__(cls, led):
        """
        Args:
            led (_CorsairLedPosition): LED position structure
        Returns:
            CorsairLedPosition: LED position namedtuple
        """
        #return super(CorsairLedPosition, cls).__new__(cls, CLK(led.ledId), led.top, led.left, led.height, led.width)
        return super(CorsairLedPosition, cls).__new__(cls, led.ledId, led.top, led.left, led.height, led.width)


class _CorsairLedPositions(Structure):
    """
    Structure representing LED positions
    """
    __slots__ = [
        "numberOfLed",
        "pLedPosition"
    ]

    _fields_ = [
        ("numberOfLed", c_int),
        ("pLedPosition", POINTER(_CorsairLedPosition))
    ]


class CorsairLedPositions(namedtuple('CorsairLedPositions', _CorsairLedPositions.__slots__)):

    def __new__(cls, leds):
        """
        Args:
            leds (_CorsairLedPositions): Structure containing LED positions
        Returns:
            CorsairLedPositions: namedtuple containing LED positions
        """
        led_positions = tuple(sorted((CorsairLedPosition(leds.pLedPosition[x]) for x in range(leds.numberOfLed)),
                                     key=attrgetter('ledId')))
        return super(CorsairLedPositions, cls).__new__(cls, leds.numberOfLed, led_positions)

class CorsairProtocolDetails(namedtuple('CorsairProtocolDetails', _CorsairProtocolDetails.__slots__)):
    def __new__(cls, details):
        """
        Args:
            details (_CorsairProtocolDetails): Structure containing the protocol handshake details.
        Returns:
            CorsairProtocolDetails: A namedtuple containing the protocol details.
        """
        sdk_ver = details.sdkVersion.decode()
        server_ver = details.serverVersion.decode()
        return super(CorsairProtocolDetails, cls).__new__(cls, sdk_ver, server_ver, details.sdkProtocolVersion,
                                                          details.serverProtocolVersion, details.breakingChanges)

class Controller(object):
  def __init__(self, priority=False):
    self.cue = CDLL("./CUESDK_2017.dll")
    self.cue.CorsairPerformProtocolHandshake.restype = _CorsairProtocolDetails
    
    self.cue.CorsairRequestControl.restype = c_bool
    self.cue.CorsairRequestControl.argtypes = [c_int]
    
    self.cue.CorsairGetLedPositions.restype = POINTER(_CorsairLedPositions)
        
    self.cue.CorsairGetLedPositionsByDeviceIndex.restype = POINTER(_CorsairLedPositions)
    self.cue.CorsairGetLedPositionsByDeviceIndex.argtypes = [c_int]
    
    self.cue.CorsairGetDeviceInfo.restype = POINTER(_CorsairDeviceInfo)
    self.cue.CorsairGetDeviceInfo.argtypes = [c_int]
    
    self.protocol_details = self.perform_protocol_handshake()
    
    self.cue.CorsairRequestControl(priority)
  
  def deviceGetModels(self, deviceid=None):
    if deviceid == None:
      devices = {}
      count = self.deviceGetCount()
      
      for deviceid in range(count):
        devices[deviceid] = self.deviceGetInfo(deviceid).model
    else:
      devices = self.deviceGetInfo(deviceid).model
    
    return devices
  
  def deviceGetInfo(self, deviceid):
    dev_info = self.cue.CorsairGetDeviceInfo(deviceid)
    if not bool(dev_info):  # False if `dev_info` is a NULL pointer
        return None
    return CorsairDeviceInfo(dev_info.contents)
  
  def deviceGetCount(self):
    return self.cue.CorsairGetDeviceCount()
  
  def flush(self):
    self.cue.CorsairSetLedsColorsFlushBuffer()
  
  def updateLED(self, deviceid, array):
    self.cue.CorsairSetLedsColorsBufferByDeviceIndex(deviceid, 1, array)
  
  def ledSet(self, deviceid, ledid, color):
    r, g, b = color
    
    colors = [CorsairLedColor(ledid, r, g, b)]
    array = (CorsairLedColor * len(colors))(*colors)
    self.updateLED(deviceid, array)
  
  def ledGetColor(self, deviceid, ledids):
    if not type(ledids) is list:
      ledids = [ledids]
    
    colors = []
    for ledid in ledids:
      colors.append(CorsairLedColor(ledid, 0, 0, 0))
    array = (CorsairLedColor * len(colors))(*colors)
    self.cue.CorsairGetLedsColorsByDeviceIndex(deviceid, len(colors), byref(array))
    
    return array
  
  def ledGetIds(self, deviceid):
    ledsinfo = self.ledGetInfo(deviceid)
    return [led.ledId for led in ledsinfo]
  
  def ledGetInfo(self, deviceid=None):
    if not deviceid is None:
      leds = self.cue.CorsairGetLedPositionsByDeviceIndex(deviceid)
    else:
      leds = self.cue.CorsairGetLedPositions()
    
    return CorsairLedPositions(leds.contents).pLedPosition
  
  def ledGetCount(self, deviceid=None):
    return len(self.ledGetInfo(deviceid))
    
  
  def perform_protocol_handshake(self):
    """
    Checks file and protocol version of CUE to understand which of SDK functions can be used.
    This is called automatically, there is no need to call for yourself.
    Returns:
        CorsairProtocolDetails: namedtuple containing protocol details.
    """
    return CorsairProtocolDetails(self.cue.CorsairPerformProtocolHandshake())
