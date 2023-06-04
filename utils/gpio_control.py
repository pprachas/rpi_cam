import gpiozero as gpio
from time import sleep

def init_pin(pin = 17):
    gpio_pin = gpio.DigitalOutputDevice(pin)

    return gpio_pin

def send_sig(gpio_pin):
    gpio_pin.on()
    sleep(1)
    gpio_pin.off()
