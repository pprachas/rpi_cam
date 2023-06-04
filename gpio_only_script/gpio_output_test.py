import utils.gpio_control as sig 

gpio_pin = sig.init_pin()
sig.send_sig(gpio_pin)