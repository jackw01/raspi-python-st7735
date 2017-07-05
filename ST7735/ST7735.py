# Python ST7735 library for Raspberry Pi
# Copyright 2016-2017 jackw01
# Distributed under the MIT license

# Imports
import RPi.GPIO as GPIO
from PIL import Image
import time, math, spidev, copy

# Colors
class Colors:
    Black = (0, 0, 0)
    Gray48 = (48, 48, 48)
    Gray64 = (64, 64, 64)
    Gray128 = (128, 128, 128)
    Gray164 = (164, 164, 164)
    Gray192 = (192, 192, 192)
    Gray208 = (208, 208, 208)
    Gray224 = (224, 224, 224)
    White = (255, 255, 255)
    Red = (255, 0, 0)
    Orange = (255, 64, 0)
    Yellow = (255, 208, 0)
    Green = (0, 255, 0)
    Teal = (0, 255, 128)
    LightBlue = (0, 128, 255)
    Blue = (0, 64, 255)
    Purple = (144, 0, 255)
    Magenta = (255, 0, 255)

# Text align
class TextAlignment:
    LeftAlign = 0;
    RightAlign = 1;
    HorizontalCenterAlign = 2;
    VerticalCenterAlign = 3;
    HorizontalAndVerticalCenterAlign = 4;

# ST7735 commands
class SPICommand:
    SWRESET = 0x01
    SLPIN = 0x10
    SLPOUT = 0x11
    PTLON = 0x12
    NORON = 0x13
    INVOFF = 0x20
    INVON = 0x21
    DISPOFF = 0x28
    DISPON = 0x29
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    RAMRD = 0x2E
    PTLAR = 0x30
    MADCTL = 0x36
    COLMOD = 0x3A
    FRMCT1 = 0xB1
    FRMCT2 = 0xB2
    FRMCT3 = 0xB3
    INVCTR = 0xB4
    DISSET = 0xB6
    PWRCT1 = 0xC0
    PWRCT2 = 0xC1
    PWRCT3 = 0xC2
    PWRCT4 = 0xC3
    PWRCT5 = 0xC4
    VMCTR1 = 0xC5
    PWRCT6 = 0xFC
    GAMCTP = 0xE0
    GAMCTN = 0xE1

# ST7735 object
class ST7735(object):

    def __init__(self, width, height, pinDataCommand):

        self.width = width
        self.height = height

        self.pinDataCommand = pinDataCommand

        GPIO.setup(self.pinDataCommand, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.mode = 0

        self.framebuffer = []

        for x in range(self.widthh + 1):
            array = []

            for y in range(self.heighth + 1):
                array.append(0)

            self.framebuffer.append(array)

        self.previousFramebuffer = []

        for x in range(self.width + 1):
            array = []

            for y in range(self.height + 1):
                array.append(0)

            self.previousFramebuffer.append(array)

        self.resetDisplay()

    def writeByte(self, value):
        "Send byte to display"
        GPIO.output(self.pinDataCommand, 1)
        self.spi.writebytes([value])

    def writeWord(self, value):
        "Send 16-bit word to display as data"
        GPIO.output(self.pinDataCommand, 1)
        self.spi.writebytes([value >> 8, value & 0xFF])

    def writeCommand(self, command, *bytes):
        "Send command byte to display"
        GPIO.output(self.pinDataCommand, 0)
        self.spi.writebytes([command])

        if len(bytes) > 0:
            GPIO.output(self.pinDataCommand, 1)
            self.spi.writebytes(list(bytes))

    def resetDisplay(self):
        "Resets and prepares display for active use."
        self.writeCommand(SPICommand.SWRESET) # Put display into sleep
        time.sleep(0.2) # Wait 200mS for controller register init
        self.writeCommand(SPICommand.SLPOUT) # Sleep out
        time.sleep(0.2) # Wait 200mS for TFT driver circuits
        self.writeCommand(SPICommand.COLMOD, 0x05) # Set color mode to 16-bit
        self.writeCommand(SPICommand.DISPON) # Display on

        self.clearScreen();

    def closeSPI(self):
        "Closes the SPI connection to the display."
        self.spi.close()

    def setAddressWindow(self, x0, y0, x1, y1):
        "Sets a rectangular display window into which pixel data is placed"
        self.writeCommand(SPICommand.CASET, 0, x0, 0, x1) # Set column range (x0, x1)
        self.writeCommand(SPICommand.RASET, 0, y0, 0, y1) # Set row range (y0, y1)

    def writeBulk(self, color, reps, count = 1):
        "Sends a 24-bit color many times"
        self.writeCommand(SPICommand.RAMWR)
        GPIO.output(self.pinDataCommand, 1)
        color = self.packColor(color)
        byteArray = [color >> 8, color & 0xFF] * reps

        for a in range(count):
            self.spi.writebytes(byteArray)

    def drawPixel(self, x, y, color, framebuffer = False):
        "Draws a pixel"
        if framebuffer:
            self.fastDrawPixel(x, y, self.packColor(color))
        else:
            self.setAddressWindow(x, y, x, y)
            color = self.packColor(color)
            self.writeCommand(SPICommand.RAMWR, color >> 8, color & 0xFF)

    def fastDrawPixel(self, x, y, color, framebuffer = False):
        "Draws a pixel quickly with inlining. Color must be pre-packed."
        if framebuffer:
            self.framebuffer[x][y] = color
        else:
            GPIO.output(self.pinDataCommand, 0)
            self.spi.writebytes([SPICommand.CASET])
            GPIO.output(self.pinDataCommand, 1)
            self.spi.writebytes([0, x, 0, x])
            GPIO.output(self.pinDataCommand, 0)
            self.spi.writebytes([SPICommand.RASET])
            GPIO.output(self.pinDataCommand, 1)
            self.spi.writebytes([0, y, 0, y])
            GPIO.output(self.pinDataCommand, 0)
            self.spi.writebytes([SPICommand.RAMWR])
            GPIO.output(self.pinDataCommand, 1)
            self.spi.writebytes([color >> 8, color & 0xFF])

    def fastDrawHLine(self, x0, x1, y, color, framebuffer = False):
        "Draws a horizontal line in the given color"
        if framebuffer:
            color = self.packColor(color)
            for i in range(x1 - x0 + 1):
                self.framebuffer[x0 + i][y] = color
        else:
            width = x1 - x0 + 1
            self.setAddressWindow(x0, y, x1, y)
            self.writeBulk(color, width)

    def fastDrawVLine(self, x, y0, y1, color, framebuffer = False):
        "Draws a vertical line in the given color"
        if framebuffer:
            color = self.packColor(color)
            for i in range(y1 - y0 + 1):
                self.framebuffer[x][y0 + i] = color
        else:
            height = y1 - y0 + 1
            self.setAddressWindow(x, y0, x, y1)
            self.writeBulk(color, height)

    def drawLine(self, x0, y0, x1, y1, color, framebuffer = False):
        "Draws a line in the given color"
        if (x0 == x1):
            if y1 < y0:
                temp = y0
                y0 = y1
                y1 = temp
            self.fastDrawVLine(x0, y0, y1, color, framebuffer = framebuffer)
        elif (y0 == y1):
            if x1 < x0:
                temp = x0
                x0 = x1
                x1 = temp
            self.fastDrawHLine(x0, x1, y0, color, framebuffer = framebuffer)
        else:
            color = self.packColor(color)
            slope = float(y1 - y0) / (x1 - x0)

            if (abs(slope) < 1):
                if x1 + 1 < x0:
                    increment = -1
                else:
                    increment = 1

                for x in range(x0, x1 + 1, increment):
                    y = (x - x0) * slope + y0
                    self.fastDrawPixel(x, int(y + 0.5), color, framebuffer = framebuffer)
            else:
                if y1 + 1 < y0:
                    increment = -1
                else:
                    increment = 1

                for y in range(y0, y1 + 1, increment):
                    x = (y - y0) / slope + x0
                    self.fastDrawPixel(int(x + 0.5), y, color, framebuffer = framebuffer)

    def drawRect(self, x0, y0, x1, y1, color, framebuffer = False):
        "Draws a rectangle outline in the given color"
        self.fastDrawHLine(x0, x1, y0, color, framebuffer = framebuffer)
        self.fastDrawHLine(x0, x1, y1, color, framebuffer = framebuffer)
        self.fastDrawVLine(x0, y0, y1, color, framebuffer = framebuffer)
        self.fastDrawVLine(x1, y0, y1, color, framebuffer = framebuffer)

    def fillRect(self, x0, y0, x1, y1, color, framebuffer = False):
        "Fills a rectangle with the given color"
        if framebuffer:
            color = self.packColor(color)
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 1):
                    self.framebuffer[x][y] = color
        else:
            width = x1 - x0 + 1
            height = y1 - y0 + 1
            self.setAddressWindow(x0, y0, x1, y1)
            self.writeBulk(color, width, height)

    def drawCircle(self, xPos, yPos, r, color, framebuffer = False):
        "Draws a circle with the given color"
        color = self.packColor(color)
        xEnd = int(math.sqrt(2) / 2 * r) + 1

        for x in range(xEnd):
            y = int(math.sqrt(r * r - x * x))
            self.fastDrawPixel(xPos + x, yPos + y, color, framebuffer = framebuffer)
            self.fastDrawPixel(xPos + x, yPos - y, color, framebuffer = framebuffer)
            self.fastDrawPixel(xPos - x, yPos + y, color, framebuffer = framebuffer)
            self.fastDrawPixel(xPos - x, yPos - y, color, framebuffer = framebuffer)
            self.fastDrawPixel(xPos + y, yPos + x, color, framebuffer = framebuffer)
            self.fastDrawPixel(xPos + y, yPos - x, color, framebuffer = framebuffer)
            self.fastDrawPixel(xPos - y, yPos + x, color, framebuffer = framebuffer)
            self.fastDrawPixel(xPos - y, yPos - x, color, framebuffer = framebuffer)

    def fillCircle(self, xPos, yPos, r, color, framebuffer = False):
        "Fills a circle with the given color"
        r2 = r * r

        for x in range(r):
            y = int(math.sqrt(r2 - x * x))
            y0 = yPos - y
            y1 = yPos + y
            self.fastDrawVLine(xPos + x, y0, y1, color, framebuffer = framebuffer)
            self.fastDrawVLine(xPos - x, y0, y1, color, framebuffer = framebuffer)

    def fillScreen(self, color, framebuffer = False):
        "Fills the entire screen with the given color"
        self.fillRect(0, 0, self.width - 1, self.width - 1, color, framebuffer = framebuffer)

    def clearScreen(self, framebuffer = False):
        "Fills the entire screen with black"
        self.fillRect(0, 0, self.width + 1, self.width + 2, (0, 0, 0), framebuffer = framebuffer) # Green tab

    def drawChar(self, font, char, x, y, color, bgColor, framebuffer = False):
        "Write a character"
        color = self.packColor(color)
        bgColor = self.packColor(bgColor)

        if char in font:
            charData = font[char]
        elif char.lower() in font:
            charData = font[char.lower()]
        else:
            charData = font["NULL"]

        if not framebuffer:
            self.setAddressWindow(x, y, x + font["width"] + charData["kerning"] - 1, y + font["height"] - charData["descender"] - 1)
            self.writeCommand(SPICommand.RAMWR)
            GPIO.output(self.pinDataCommand, 1)

        pixelBuffer = []

        for row in range(font["height"] - charData["descender"]):
            for col in range(font["width"] + charData["kerning"]):
                bit = charData["pixels"][row][col]

                if (bit == 0):
                    pixel = bgColor
                else:
                    pixel = color

                if framebuffer:
                    self.framebuffer[x + col][y + row] = pixel
                else:
                    pixelBuffer.append(pixel >> 8)
                    pixelBuffer.append(pixel & 0xFF)

        if not framebuffer:
            self.spi.writebytes(pixelBuffer)

        return font["width"] + charData["kerning"]

    def getStringSize(self, font, string):
        "Get the size of a string"
        width = 0
        height = font["height"] + font["linespacing"]
        lastKerning = 0
        minWidth = 10000

        for char in string:
            if char == "\n":
                height += font["height"] + font["linespacing"]
                if width - font["charspacing"] - lastKerning * 2 < minWidth:
                    minWidth = width - font["charspacing"] - lastKerning * 2
            else:
                if char in font:
                    charData = font[char]
                elif char.lower() in font:
                    charData = font[char.lower()]
                else:
                    charData = font["NULL"]
                lastKerning = charData["kerning"]
                width += font["width"] + font["charspacing"] + charData["kerning"]

        if width - font["charspacing"] - lastKerning * 2 < minWidth:
            minWidth = width - font["charspacing"] - lastKerning * 2

        return (minWidth, height)

    def drawString(self, font, string, x, y, color, bgColor, align = TextAlignment.LeftAlign, wrap = False, fullBG = False, framebuffer = False):
        "Write a string"
        size = self.getStringSize(font, string)
        xPointer, yPointer = 0, 0

        if align == TextAlignment.LeftAlign:
            xPointer = x
            yPointer = y
        elif align == TextAlignment.RightAlign:
            xPointer = x - size[0]
            yPointer = y
        elif align == TextAlignment.HorizontalCenterAlign:
            xPointer = round(x + 2 - (size[0] / 2))
            yPointer = y
        elif align == TextAlignment.VerticalCenterAlign:
            xPointer = x
            yPointer = round(x + 2 - (size[1] / 2))
        elif align == TextAlignment.HorizontalAndVerticalCenterAlign:
            xPointer = round(x + 2 - (size[0] / 2))
            yPointer = round(x + 2 - (size[1] / 2))

        initialX = xPointer

        if fullBG:
            self.fillRect(xPointer, yPointer, xPointer + size[0], yPointer + size[1], bgColor, framebuffer = framebuffer)

        index = 0
        words = string.split(" ")
        for word in words:

            if align == TextAlignment.LeftAlign and wrap:
                newX = xPointer + self.getStringSize(font, word)[0] + font["charspacing"]

                if newX > 128 - x:
                    xPointer = initialX
                    yPointer += font["height"] + font["linespacing"]

            for char in word:
                if char == "\n":
                    xPointer = initialX
                    yPointer += font["height"] + font["linespacing"]
                else:
                    xPointer += self.drawChar(font, char, xPointer, yPointer, color, bgColor, framebuffer = framebuffer) + font["charspacing"]

            xPointer += self.drawChar(font, " ", xPointer, yPointer, color, bgColor, framebuffer = framebuffer) + font["charspacing"]

    def drawImage(self, image, drawX, drawY, bgColor, drawWidth = 0, drawHeight = 0, framebuffer = False):
        "Draws an image"
        width, height = image.size

        if drawWidth != 0 and drawHeight != 0:
            image = image.resize((drawWidth, drawHeight), Image.ANTIALIAS)
            width, height = image.size

        pixels = image.load()

        if framebuffer:
            for y in range(height):
                for x in range(width):
                    pixel = pixels[x, y]
                    prevColor = self.unpackColor(self.framebuffer[drawX + x][drawY + y])
                    newColor = [max(int(pixel[i] * (pixel[3] / 255.0)) + prevColor[i], 255) for i in range(3)]
                    self.framebuffer[drawX + x][drawY + y] = self.packColor(newColor)

        else:
            pixelBuffer = []

            self.setAddressWindow(x, y, x + width - 1, y + height - 1)
            self.writeCommand(SPICommand.RAMWR)
            GPIO.output(self.pinDataCommand, 1)

            for y in range(height):
                for x in range(width):
                    pixel = pixels[x, y]
                    if pixel[3] == 0:
                        color = self.packColor(bgColor)
                    else:
                        color = self.packColor(pixel[:3])

                    pixelBuffer.append(color >> 8)
                    pixelBuffer.append(color & 0xFF)

                self.spi.writebytes(pixelBuffer)
                pixelBuffer = []

    def updateFromFramebuffer(self, columnScan = False):
        "Updates the display from the framebuffer"

        if columnScan == False:
            for y in range(self.height + 1):
                self.setAddressWindow(0, y, 128, y)
                self.writeCommand(SPICommand.RAMWR)
                GPIO.output(self.pinDataCommand, 1)

                pixelBuffer = []
                updateRow = False

                for x in range(self.width + 1):
                    if self.framebuffer[x][y] != self.previousFramebuffer[x][y]:
                        updateRow = True

                if updateRow == True:
                    for x in range(self.width + 1):
                        pixelBuffer.append(self.framebuffer[x][y] >> 8)
                        pixelBuffer.append(self.framebuffer[x][y] & 0xFF)

                    self.spi.writebytes(pixelBuffer)

        elif columnScan == True:
            for x in range(self.width + 1):
                self.setAddressWindow(x, 0, x, 128)
                self.writeCommand(SPICommand.RAMWR)
                GPIO.output(self.pinDataCommand, 1)

                pixelBuffer = []
                updateRow = False

                for y in range(self.height + 1):
                    if self.framebuffer[x][y] != self.previousFramebuffer[x][y]:
                        updateRow = True

                if updateRow == True:
                    for y in range(self.height + 1):
                        pixelBuffer.append(self.framebuffer[x][y] >> 8)
                        pixelBuffer.append(self.framebuffer[x][y] & 0xFF)

                    self.spi.writebytes(pixelBuffer)

        self.previousFramebuffer = copy.deepcopy(self.framebuffer)

    def packColor(self, color):
        "Converts an 24-bit RGB color to a 16-bit BGR565 color"
        return ((color[2] // 8) << 11) | ((color[1] // 4) << 5) | (color[0] // 8)

    def unpackColor(self, color):
        "Converts a 16-bit BGR565 color to a 24-bit RGB color"
        return [((((color >> 11) & 0x1F) * 527) + 23) >> 6, ((((color >> 5) & 0x3F) * 259) + 33) >> 6, (((color & 0x1F) * 527) + 23) >> 6]
