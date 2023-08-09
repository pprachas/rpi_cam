import utils.gpio_control as sig 

gpio_pin = sig.init_pin(17)
print('Sending Signal:')
sig.send_sig(gpio_pin)