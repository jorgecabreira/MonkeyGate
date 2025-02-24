"""



"""


import serial
import struct
import binascii
import os
import time
import datetime
import calendar

def byteToBinaryString(hex):
    
    result = ""
    
    # shift 00000001 from right to left 7 times
    mask = 1 << 7
    
    # emulate do while loop
    while True:
        c = "1" if ( hex & mask ) != 0 else "0"
        result += c
        
        mask >>= 1
        if mask <= 0:
            break
    
    return result


# Protocol for the serial port sample.
#
# Eli Bendersky [http://eli.thegreenplace.net]
# This code is in the public domain.
#
# The response type returned by ProtocolWrapper
# 
# modified by M.Jeschke on 20180524
class ProtocolStatus(object):
    START_MSG = 'START_MSG'
    IN_MSG = 'IN_MSG'
    AFTER_MSG = 'GET_CHKSM'
    MSG_OK = 'MSG_OK'
    ERROR = 'ERROR'


class ProtocolWrapper(object):
    """ Wraps or unwraps a byte-stuffing header/footer protocol.
        First, create an object with the desired parameters.
        Then, to wrap a data block with a protocol, simply call
        wrap().
        To unwrap, the object is used as a state-machine that is
        fed a byte at a time by calling input(). After each byte
        a ProtocolStatus is returned:
         * ERROR: check .last_error for the message
         * MSG_OK: the received message is .last_message
         * START_MSG: a new message has just begun (header
           received)
         * IN_MSG: a message is in progress, so keep feeding bytes
        Bytes are binary strings one character long. I.e. 'a'
        means 0x61, '\x8B' means -0x8B.
        Messages - the one passed to wrap() and the one saved
        in .last_message, are strings.
    """
    def __init__(self,
            header=b'\x02',
            footer=b'\x03',
            dle=b'\x10',
            after_dle_func=lambda x: x,
            keep_header=True,
            keep_footer=True,
            keep_dle=True,
            has_checksum_appended=True):
        """ header:
                The byte value that starts a message
            footer:
                The byte value that ends a message
            dle:
                DLE value (the DLE is prepended to any header,
                footer and DLE in the stream)
            after_dle_func:
                Sometimes the value after DLE undergoes some
                transformation. Provide the function that does
                so here (i.e. XOR with some known value)
            keep_header/keep_footer:
                Keep the header/footer as part of the returned
                message.
        """
        self.header = header
        self.footer = footer
        self.dle = dle
        self.after_dle_func = after_dle_func
        self.keep_dle    = keep_dle
        self.keep_header = keep_header
        self.keep_footer = keep_footer
        self.has_checksum_appended = has_checksum_appended

        self.state = self.WAIT_HEADER
        self.last_message = b''
        self.last_messagetime = None
        self.message_buf = b''
        self.message_time = None
        self.last_error = b''    
        
        self.append_dle = b''
        if self.keep_dle:
            self.append_dle = self.dle        

    def wrap(self, message):
        """ Wrap a message with header, footer and DLE according
            to the settings provided in the constructor.
        """
        wrapped = b''
        wrapped += self.header
        for b in message:
            b = bytes([b])
            if b in (self.header, self.footer, self.dle):
                wrapped += (self.dle + self.after_dle_func(b))
            else:
                wrapped += b
               
        wrapped += self.footer
            
        return wrapped

    # internal state
    (WAIT_HEADER, IN_MSG, AFTER_DLE, AFTER_MSG) = range(4) # AFTER_MSG added to handle checksum after message plus footer

    def input(self, new_byte):
        """ Call this method whenever a new byte is received. It
            returns a ProtocolStatus (see documentation of class
            for info).
        """
        if self.state == self.WAIT_HEADER:
            if new_byte == self.header:
                self.message_time = datetime.datetime.now()
                if self.keep_header:
                    self.message_buf += self.dle + new_byte

                self.state = self.IN_MSG
                return ProtocolStatus.START_MSG
            else:
                if new_byte:     
                    self.last_error = 'Expected header (0x%02X), got 0x%02X' % (
                        ord(self.header), ord(new_byte))
                else:
                    self.last_error = 'Expected header (0x%02X), got empty byte' % (
                        ord(self.header))
                return ProtocolStatus.ERROR
        elif self.state == self.IN_MSG:
            if new_byte == self.dle:
                self.state = self.AFTER_DLE
                return ProtocolStatus.IN_MSG
            elif new_byte == self.footer:
                if self.keep_footer:
                    self.message_buf += self.dle + new_byte
                if self.has_checksum_appended:
                    self.state = self.AFTER_MSG 
                    return ProtocolStatus.AFTER_MSG 
                else:
                    return self._finish_msg()
            else: # just a regular message byte
                self.message_buf += new_byte
                return ProtocolStatus.IN_MSG
        elif self.state == self.AFTER_DLE:
            if new_byte == self.footer:
                if self.keep_footer:
                    self.message_buf += self.dle + new_byte
                if self.has_checksum_appended:
                    self.state = self.AFTER_MSG 
                    return ProtocolStatus.AFTER_MSG 
                else:
                    return self._finish_msg()
            else: # just a regular message byte     
                self.message_buf += self.append_dle + self.after_dle_func(new_byte)
                self.state = self.IN_MSG
                return ProtocolStatus.IN_MSG
        elif self.state == self.AFTER_MSG: # add a single checksum byte to message
            self.message_buf += new_byte
            return self._finish_msg()
        else:
            raise AssertionError()


    def _finish_msg(self):
        self.state = self.WAIT_HEADER
        self.last_message = self.message_buf
        self.last_messagetime = self.message_time
        self.message_buf = b''
        self.message_time = None
        return ProtocolStatus.MSG_OK
    
class TimeObj():
    
    def __init__(self, year = None, month = None, day = None, hour = None, minute = None, second = None):

        self.year = year
        self.month = month
        self.day   = day
        self.hour = hour
        self.minute =  minute
        self.second = second


class DorsetRFID650_Interface():
    
    def __init__(self, COMPort = '/dev/ttyUSB0', baudrate = 57600, UnitNr = '01', Host = 'FE'):

        self.ser = serial.Serial(
                port=COMPort,
                baudrate = baudrate, # 19200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
                )
        
        self.messageIDs = {'start': b'\x02', 'stop': b'\x03', 'DLE': b'\x10'}
        
        self.messageBuffer = b''
        
        self.UnitNr = UnitNr
        
        self.Host   = Host   
        
        self.ProtocolWrapper = ProtocolWrapper(header=self.messageIDs['start'],
            footer=self.messageIDs['stop'],
            dle=self.messageIDs['DLE'],
            has_checksum_appended=True)
        
        curTime = datetime.datetime.now()
        self.leapYear = curTime.year
        while not calendar.isleap(self.leapYear):
            self.leapYear -= 1
        
    def setTime(self, timeHex = '64', timeTuple = None):
        
        curTime = datetime.datetime.now() 
        if timeTuple:
            print('Using timetuple to set RFID time.')
            curTime = TimeObj(timeTuple[0], timeTuple[1], timeTuple[2], timeTuple[3], timeTuple[4], timeTuple[5])
            
            curTime = datetime.datetime(curTime.year, curTime.month, curTime.day, curTime.hour, curTime.minute, curTime.second)

        timeInfo = binascii.unhexlify("{0:02}{1:02}{2:02}".format(curTime.second, curTime.minute, curTime.hour))
        
        leapYear = curTime.year
        while not calendar.isleap(leapYear):
            leapYear -= 1
        
        leapyearDistStr = "{0:02b}".format(curTime.year - leapYear)
        tenDaysStr = "{0:02b}".format(curTime.day // 10)
        unitDaysStr = "{0:04b}".format(curTime.day % 10)
        
        dd = leapyearDistStr + tenDaysStr + unitDaysStr
        dd = bytes([int(dd,2)])
            
        weekdayStr = "{0:03b}".format(curTime.weekday()+1)
        tenMonthStr = "{0:01b}".format(curTime.month // 10)
        unitMonthStr = "{0:04b}".format(curTime.month % 10) 
        
        ee = weekdayStr + tenMonthStr + unitMonthStr
        ee = bytes([int(ee,2)])  
        
#        message =  bytes.fromhex(timeHex) + timeInfo + dd + ee
        message =  (bytes.fromhex(timeHex), timeInfo, dd, ee)  
        message = self._createMessage(message)  
        
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()
        self.ser.write(message)
        
        returnedFrame, returnedTime = self.getFrame()   
    
        if not self.validateMessage(returnedFrame):
            print('time could not be read from decoder!')
            
            return None
          
        Host, Unit, command, timeInfo, timeDummy = self.parseFrame(returnedFrame)
        
        returnedTime = self._parseTimeInfo( timeInfo)
        
        return returnedTime
        
    def getTime(self, timeHex = '44'):
        
        self.timeRequest = self._createMessage(bytes.fromhex(timeHex))
        
#        print(binascii.b2a_hex(self.timeRequest).decode("utf-8"))

        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()
        self.ser.write(self.timeRequest)
        
        returnedFrame, returnedTime = self.getFrame()
        
#        print(binascii.b2a_hex(returnedFrame).decode("utf-8"))      
#        print(self.validateMessage(returnedFrame))
        if not self.validateMessage(returnedFrame):
            print('time could not be read from decoder!')
            
            return None
          
        Host, Unit, command, timeInfo, timeDummy = self.parseFrame(returnedFrame)

        returnedTime = self._parseTimeInfo(timeInfo)
        
        return returnedTime

        
    def _parseTimeInfo(self, timeInfo):
        
#        print(timeInfo)
#        print(binascii.b2a_hex(timeInfo).decode("utf-8"))

        yearsDays = byteToBinaryString(timeInfo[3])
        weekdayMonths = byteToBinaryString(timeInfo[4])
        
        # convert to something readable
        timeOfDay = binascii.b2a_hex(timeInfo[:3])
        seconds, minutes, hours = int(timeOfDay[0:2]), int(timeOfDay[2:4]), int(timeOfDay[4:6])
        leapyearDist = int(yearsDays[0:2],2)
        Days  = int(yearsDays[2:4],2)*10+int(yearsDays[4::],2)
        
        # weekday = int(weekdayMonths[0:3],2) # NOT IN USE AS DATETIME DOES NOT NEED THIS INFO
        month = int(weekdayMonths[3:4],2)*10 + int(weekdayMonths[4::],2)
        
        year = leapyearDist + self.leapYear
        
        returnedTime = datetime.datetime(year, month, Days, hours, minutes, seconds)

        return returnedTime
    
    def getFrame(self, waitForStart = True):
        
        datWaiting = self.ser.inWaiting()
        if datWaiting > 0 or waitForStart == True:
            flagProcessed = 0
            while flagProcessed == 0:
                # read the message one by one and return the latest message          
                curByte = self.ser.read(size = 1)
                 
                statusMsg = self.ProtocolWrapper.input(curByte)
                if ProtocolStatus.MSG_OK == statusMsg:
                    Frame = self.ProtocolWrapper.last_message
                    FrameTime = self.ProtocolWrapper.last_messagetime
                    flagProcessed = 1            
             
        return Frame, FrameTime
    
    def _createMessage(self, message):
        
        messageDummy = b''
        if isinstance(message, tuple):
            for el in message:
                messageDummy += el
            message = messageDummy          

        # first stuff the message
        wrapped = b''
        for el in message:
            if isinstance(el, int):
                el = bytes([el])
            if el in (self.messageIDs['start'], self.messageIDs['stop'], self.messageIDs['DLE']):
                wrapped += (self.messageIDs['DLE'] + el)
            else:
                wrapped += el     
                
        # create full message
        message = b''
        message += self.messageIDs['DLE'] + self.messageIDs['start'] # add header
        message += bytes.fromhex(self.Host + self.UnitNr) # add Host and Unit
        message += wrapped # add the message
        message += self.messageIDs['DLE'] + self.messageIDs['stop'] # add footer

#        print(message)
#        print(binascii.b2a_hex(message))

        # create and add checksum
        message += self._HexChecksum(message) # always add the checksum
        
#        print(message)
#        print(binascii.b2a_hex(message))
        
        return message
    
    
    def validateMessage(self, message, checksum = 0):
        
        valid = 0
        if bytes([checksum]) == self._HexChecksum(message):
            valid = 1
            
        return valid
    
    def _HexChecksum(self, message):
        
        checksum = 0
        for element in message:
            checksum ^= element

        return bytes([checksum])
    
    def parseFrame(self, message, messageTime = None):
        
        if isinstance(message, tuple):
            message, messageTime = message[0], message[1]

        messageStart = message.find(self.messageIDs['DLE'] + self.messageIDs['start']) # frame start
        messageStop  = message.find(self.messageIDs['DLE'] + self.messageIDs['stop']) # frame stop
   
        Host, Unit, command, message = message[messageStart+2:messageStart+3:], message[messageStart+3:messageStart+4:], message[messageStart+4:messageStart+5:], message[messageStart+5:messageStop:]
        
        messageDummy = b''
        after_dle = 0
        for el in message:
            el = bytes([el])
            if el == self.messageIDs['DLE'] and after_dle == 0:
                after_dle = 1
            else:
                messageDummy += el
                after_dle = 0
                    
        return Host, Unit, command, messageDummy, messageTime
    
    def processFrame(self):
        
        return self.parseFrame(self.getFrame())

    class Message():
        
        def __init__(self):
            
            self.processed = 0
            self.message = []
            self.checksum = 0
            self.valid = 0
            
        def calcHexChecksum(self):
        
            checksum = 0
            for element in self.message:
                checksum ^= element
    
            return checksum
        
        def validate(self):
            """
            the calculated Hex checksum is zero if the message contains: 
                1) the frame start indicator
                2) the message
                3) the frame stop indicator
                4) the checksum from the device
        
            if the message does not contain (4) then the checksum should be set 
            before validation
            """
            
            self.valid = 0
            if self.checksum == self.calcHexChecksum(): # 
                self.valid = 1
            
            return self.valid
        
        def show(self):
            
            print('Message:         ' + binascii.b2a_hex(self.message).decode("utf-8"))
            print('Checksum calc:   ' + hex(self.calcHexChecksum())[2::])
            print('Checksum     :   ' + hex(self.checksum)[2::])
            print('Message valid:   ' + str(self.valid))   
            
if __name__ == '__main__':
    
    RFID = DorsetRFID650_Interface(baudrate = 57600)
    
#    print('RFIDDecoder returned the time: ' + RFID.getTime().isoformat())
    
#    timeTuple = (2017, 10, 10, 10, 10, 10)
#    print('RFIDDecoder set to time: ' + RFID.setTime(timeTuple = timeTuple).isoformat())
    
#    print('RFIDDecoder set to time: ' + RFID.setTime().isoformat())

    flag = 1
    while flag:
        try:
            time.sleep(0.1)
            
            datWaiting = RFID.ser.inWaiting()
            if datWaiting > 0:
                
                returnedData = RFID.processFrame()

                print('Message timestamp: ' + returnedData[-1].isoformat())
                print('Transponder type: ' + binascii.b2a_hex(returnedData[2]).decode("utf-8"))
                print('Tag: ' + binascii.b2a_hex(returnedData[3]).decode("utf-8"))
                
        except KeyboardInterrupt:
            print('finished')  # Add final newline
            
            RFID.ser.close()
            
            flag = 0
            break
    
    