import magicbulb_control as magicbulb
import schedule
import time

def test():
	print("i'm called!")
	bulb = magicbulb.MagicBulb("98:7B:F3:5A:F2:3A")
	bulb.turn_off()
	time.sleep(3)
	bulb.turn_on()

def alarm():
	print("Alarm called!!")
	bulb = magicbulb.MagicBulb("98:7B:F3:5A:F2:3A")
	for brightness in range(0, 255):
		bulb.set_color(0, 0, 0, brightness)
		time.sleep(7.1)

schedule.every().day.at("23:30").do(alarm) 
schedule.every().day.at("07:30").do(alarm)

while True:
	schedule.run_pending()
	time.sleep(1)
