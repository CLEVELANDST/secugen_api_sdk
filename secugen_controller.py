import sgfplib
import sys
import json

class SecugenController:
    def __init__(self):
        self.sgfp = sgfplib.SgFpLib()
        self.initializeDevice()
    
    def initializeDevice(self):
        try:
            self.sgfp.Init(sgfplib.DEVICENAME)
            self.sgfp.OpenDevice(0)
            return True
        except Exception as e:
            return str(e)
    
    def led_control(self, state):
        try:
            if state:
                self.sgfp.SetLedOn(True)
            else:
                self.sgfp.SetLedOn(False)
            return {"success": True, "message": f"LED {'encendido' if state else 'apagado'}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    controller = SecugenController()
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    if command == "led_on":
        result = controller.led_control(True)
    elif command == "led_off":
        result = controller.led_control(False)
    else:
        result = {"success": False, "error": "Comando no válido"}
    
    print(json.dumps(result)) 