# Python ST7735 library for Raspberry Pi
# Display Test
# Copyright 2017 jackw01
# Distributed under the MIT license

# Import modules
import RPi.GPIO as GPIO
from ST7735 import *
import time

# Import fonts
from ST7735.fonts.font4x5 import *
from ST7735.fonts.font5x7 import *
from ST7735.fonts.font7x10 import *

# Pins
pinDataCommand = 22

# Main Program

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

display = ST7735.ST7735(128, 128, pinDataCommand)

display.clearScreen()
display.fastDrawHLine(85, 117, 16, ST7735.Colors.Green)
display.fastDrawVLine(16, 76, 117, ST7735.Colors.Blue)
display.drawLine(85, 32, 117, 64, ST7735.Colors.Yellow)
display.drawLine(85, 64, 117, 32, ST7735.Colors.LightBlue)
display.drawRect(32, 76, 64, 117, ST7735.Colors.Magenta)
display.fillRect(0, 0, 76, 64, ST7735.Colors.Red)
display.drawPixel(4, 4, ST7735.Colors.Black)
display.drawCircle(96, 96, 16, ST7735.Colors.White)
display.fillCircle(96, 96, 8, ST7735.Colors.Gray128)

time.sleep(5)

display.clearScreen()
display.drawString(font4x5, "abcdefghijklm\nnopqrstuvwxyz\n0123456789", 4, 4, ST7735.Colors.White, ST7735.Colors.Black)
display.drawString(font5x7, "abcdefghijklm\nnopqrstuvwxyz\n0123456789", 4, 40, ST7735.Colors.White, ST7735.Colors.Black)
display.drawString(font7x10, "abcdefghijklm\nnopqrstuvwxyz\n0123456789", 4, 80, ST7735.Colors.White, ST7735.Colors.Black)

display.closeSPI()
