from collections import namedtuple
from ctypes import Structure, CDLL, c_int, c_bool, c_char_p, byref

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
    
    self.protocol_details = self.perform_protocol_handshake()
    
    self.cue.CorsairRequestControl(priority)
  
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
  
  def ledGetCount(self, deviceid=None):
    if not deviceid is None:
      leds = self.cue.CorsairGetLedPositionsByDeviceIndex(deviceid)
    else:
      leds = self.cue.CorsairGetLedPositions()
    
    return leds
  
  def perform_protocol_handshake(self):
    """
    Checks file and protocol version of CUE to understand which of SDK functions can be used.
    This is called automatically, there is no need to call for yourself.
    Returns:
        CorsairProtocolDetails: namedtuple containing protocol details.
    """
    return CorsairProtocolDetails(self.cue.CorsairPerformProtocolHandshake())
