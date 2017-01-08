from bluepy import btle

class MagicBulb(object):
    """ A simple chinese magic bulb with bluetooth control

        Attributes:
            bulb: btle.Peripheral object, connected to the bulb
            bulb_addr: MAC addr of connected bulb
            red_uuid: uuid of service to set red color of bulb
            red_serivce: service instance to control red color
            green_uuid: uuid of service to set green color of bulb
            green_serivce: service instance to control green color
            blue_uuid: uuid of service to set blue color of bulb
            blue_serivce: service instance to control blue color
            white_uuid: uuid of service to set white color of bulb
            white_serivce: service instance to control white color
            
    """
    
    red_uuid = "0000ffe6-0000-1000-8000-00805f9b34fb"
    green_uuid = "0000ffe7-0000-1000-8000-00805f9b34fb"
    blue_uuid = "0000ffe8-0000-1000-8000-00805f9b34fb"
    white_uuid = "0000ffea-0000-1000-8000-00805f9b34fb"

    def __init__(self, bulb_addr):
        """ Return an object connected to the bulb via
        bluetooth """
        self.bulb = btle.Peripheral(bulb_addr)
        self.bulb_addr = bulb_addr

        self.red_service = self.bulb.getCharacteristics(uuid=self.red_uuid)[0]
        self.blue_service = self.bulb.getCharacteristics(uuid=self.blue_uuid)[0]
        self.green_service = self.bulb.getCharacteristics(uuid=self.green_uuid)[0]
        self.white_service = self.bulb.getCharacteristics(uuid=self.white_uuid)[0]
        self.disconnect()

    def set_color(self, red_value, green_value, blue_value, white_value):
        """ Set the color of the bulb. Setting rgb color with white is not
        recommended """
        self.red_service.write(bytes([red_value]))
        self.green_service.write(bytes([green_value]))
        self.blue_service.write(bytes([blue_value]))
        self.white_service.write(bytes([white_value]))

    def turn_on(self):
        """ Turn on the bulb in white mode """
        self.set_color(0, 0, 0, 255)

    def turn_off(self):
        """ Turn off the bulb """
        self.set_color(0, 0, 0, 0)

    def connect(self):
        self.bulb.connect(self.bulb_addr)

    def disconnect(self):
        self.bulb.disconnect()

    def reconnect(self):
        self.disconnect()
        self.connect()
