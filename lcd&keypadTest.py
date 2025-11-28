import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pcf8574 import PCF8574

# =========================
# I2C LCD DRIVER (same as your working version)
# =========================

i2c = busio.I2C(board.GP1, board.GP0)
LCD_ADDR = 0x27
pcf = PCF8574(i2c, LCD_ADDR)

RS = pcf.get_pin(0)
RW = pcf.get_pin(1)
E  = pcf.get_pin(2)
BL = pcf.get_pin(3)
D4 = pcf.get_pin(4)
D5 = pcf.get_pin(5)
D6 = pcf.get_pin(6)
D7 = pcf.get_pin(7)

BL.value = True

def pulseEnable():
    E.value = False
    time.sleep(0.000005)
    E.value = True
    time.sleep(0.000005)
    E.value = False
    time.sleep(0.0001)

def write4(bits):
    D4.value = bool(bits & 0x01)
    D5.value = bool(bits & 0x02)
    D6.value = bool(bits & 0x04)
    D7.value = bool(bits & 0x08)
    pulseEnable()

def send(byte, isChar=False):
    RS.value = isChar
    RW.value = False
    write4(byte >> 4)
    write4(byte & 0x0F)

def lcdCommand(cmd):
    send(cmd, False)

def lcdChar(ch):
    send(ord(ch), True)

def lcdString(s):
    for c in s:
        lcdChar(c)

def lcdClear():
    lcdCommand(0x01)
    time.sleep(0.005)

# LCD initialization
time.sleep(0.05)
write4(0x03); time.sleep(0.005)
write4(0x03); time.sleep(0.005)
write4(0x03); time.sleep(0.005)
write4(0x02)

lcdCommand(0x28)
lcdCommand(0x0C)
lcdCommand(0x06)
lcdClear()

lcdString("Keypad Ready...")


# =========================
# 4x4 KEYPAD SETUP
# =========================

keys = [
    ["1","2","3","A"],
    ["4","5","6","B"],
    ["7","8","9","C"],
    ["*","0","#","D"],
]

colPins = [board.GP9, board.GP8, board.GP7, board.GP6]
rowPins = [board.GP13, board.GP12, board.GP11, board.GP10]

rows = []
cols = []

# Setup row outputs (idle HIGH)
for p in rowPins:
    r = DigitalInOut(p)
    r.direction = Direction.OUTPUT
    r.value = True
    rows.append(r)

# Setup column inputs (pulled-up)
for p in colPins:
    c = DigitalInOut(p)
    c.direction = Direction.INPUT
    c.pull = Pull.UP
    cols.append(c)

# =========================
# KEYPAD SCAN LOOP
# =========================

def readKeypad():
    for rIndex, rPin in enumerate(rows):
        rPin.value = False   # pull row low

        for cIndex, cPin in enumerate(cols):
            if cPin.value == False:  # active LOW
                rPin.value = True
                return keys[rIndex][cIndex]

        rPin.value = True

    return None

# =========================
# MAIN LOOP
# =========================

time.sleep(0.2)
lcdClear()

while True:
    key = readKeypad()

    if key is not None:
        lcdClear()
        lcdString("Pressed: " + key)

        # debounce
        while readKeypad() is not None:
            time.sleep(0.02)

    time.sleep(0.02)
