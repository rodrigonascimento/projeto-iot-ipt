from machine import Pin, SoftI2C
import mpu6050
import ssd1306
import time
import network
import urequests
import json

def config_wifi():
    wlan = network.WLAN(network.STA_IF) # create station interface
    wlan.active(True)       # activate the interface
    wlan.isconnected()      # check if the station is connected to an AP
    time.sleep_ms(500)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('meuwifi', '12345678') # connect to an AP
        time.sleep_ms(500)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan 

def init_mpu6050():
    mpu_i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
    accel = mpu6050.accel(mpu_i2c)
    return accel

def init_oled():
    # Heltec LoRa 32 with OLED Display
    oled_width = 128
    oled_height = 64

    # OLED reset pin
    i2c_rst = Pin(16, Pin.OUT)

    # Initialize the OLED display
    i2c_rst.value(0)
    time.sleep_ms(5)
    i2c_rst.value(1) # must be held high after initialization

    # Setup the I2C lines
    i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
    i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)

    # Create the bus object
    i2c = SoftI2C(scl=i2c_scl, sda=i2c_sda)

    # Create the display object
    return ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


def main():
    oled = init_oled()
    accel = init_mpu6050()
    wlan = config_wifi()

    oled.fill(0)
    oled.text(wlan.ifconfig()[0], 0, 0)
    oled.text('ThingsBoard', 0, 10)
    oled.show()

    while True:
        data = accel.get_values()
        telemetry = {'AcX': data['AcX'], 'AcY': data['AcY'], 'AcZ': data['AcZ'], 'Temp': data['Tmp']}
        oled.fill(0)
        oled.text('AcX: ' + str(data['AcX']), 0, 20)
        oled.text('AcY:' + str(data['AcY']), 0, 30)
        oled.text('AcZ:' + str(data['AcZ']), 0, 40)
        res = urequests.post('http://34.170.18.196:8080/api/v1/esp32-iotqueda/telemetry', headers={'content-type': 'application/json'}, data=json.dumps(telemetry))
        if res.status_code == 200:            
            oled.text('Enviado!', 0, 10)
        else:
            oled.text('Falhou!', 0, 20)

        oled.show()
        res.close()

        time.sleep(1)
        
if __name__ == '__main__':
    main()
