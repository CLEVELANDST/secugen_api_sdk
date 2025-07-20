from flask import Flask, request, jsonify
from flask_cors import CORS
from sdk import PYSGFPLib
from sdk.sgfdxerrorcode import SGFDxErrorCode
import base64
from ctypes import c_int, byref, c_long, c_ubyte, POINTER, c_bool
import time
import sys
import os
import subprocess
import glob

app = Flask(__name__)
CORS(app)

class SecugenController:
    def __init__(self):
        self.sgfp = None
        self.initialized = False
        self.init_error = None
        self.stored_templates = {}  # Para almacenar templates de referencia
        try:
            self.sgfp = PYSGFPLib()
            self.initializeDevice()
        except Exception as e:
            self.init_error = str(e)
            print(f"Error al crear instancia de SecugenController: {e}")
    
    def find_secugen_device(self):
        """Encuentra el dispositivo USB SecuGen dinámicamente"""
        try:
            # Buscar dispositivos USB con VendorID:ProductID de SecuGen (1162:0300)
            print("Buscando dispositivo SecuGen USB...")
            
            # Método 1: Usar lsusb para encontrar el dispositivo
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise Exception(f"Error ejecutando lsusb: {result.stderr}")
            
            secugen_lines = []
            for line in result.stdout.split('\n'):
                if '1162:0300' in line or 'SecuGen' in line:
                    secugen_lines.append(line.strip())
                    print(f"Dispositivo SecuGen encontrado: {line.strip()}")
            
            if not secugen_lines:
                raise Exception("No se encontró dispositivo SecuGen USB")
            
            # Método 2: Buscar en /sys/bus/usb/devices/ para obtener el device_id
            usb_devices = glob.glob('/sys/bus/usb/devices/*-*')
            device_id = None
            
            for device_path in usb_devices:
                try:
                    # Leer idVendor e idProduct
                    with open(f'{device_path}/idVendor', 'r') as f:
                        vendor_id = f.read().strip()
                    with open(f'{device_path}/idProduct', 'r') as f:
                        product_id = f.read().strip()
                    
                    # Verificar si es el dispositivo SecuGen
                    if vendor_id == '1162' and product_id == '0300':
                        device_id = os.path.basename(device_path)
                        print(f"Dispositivo SecuGen encontrado en: {device_id}")
                        break
                        
                except (FileNotFoundError, PermissionError) as e:
                    continue
            
            if not device_id:
                raise Exception("No se pudo determinar el device_id del dispositivo SecuGen")
            
            return device_id
            
        except Exception as e:
            print(f"Error en find_secugen_device: {str(e)}")
            raise e
    
    def reset_usb_device(self):
        """Resetea el dispositivo USB SecuGen mediante unbind/bind"""
        try:
            print("Iniciando reset del dispositivo USB SecuGen...")
            
            # Encontrar el dispositivo dinámicamente
            device_id = self.find_secugen_device()
            print(f"Device ID encontrado: {device_id}")
            
            # Cerrar el dispositivo SDK antes del reset
            if self.initialized and self.sgfp:
                print("Cerrando dispositivo SDK antes del reset USB...")
                try:
                    self.sgfp.CloseDevice()
                    self.initialized = False
                    print("Dispositivo SDK cerrado")
                except Exception as e:
                    print(f"Error al cerrar dispositivo SDK: {e}")
            
            # Realizar unbind del dispositivo
            print(f"Realizando unbind del dispositivo {device_id}...")
            unbind_path = f'/sys/bus/usb/drivers/usb/unbind'
            
            try:
                with open(unbind_path, 'w') as f:
                    f.write(device_id)
                print("Unbind completado exitosamente")
            except PermissionError:
                raise Exception("Permisos insuficientes para realizar unbind. Ejecute como root o agregue reglas udev")
            except Exception as e:
                raise Exception(f"Error en unbind: {str(e)}")
            
            # Esperar 1 segundo
            print("Esperando 1 segundo...")
            time.sleep(1)
            
            # Realizar bind del dispositivo
            print(f"Realizando bind del dispositivo {device_id}...")
            bind_path = f'/sys/bus/usb/drivers/usb/bind'
            
            try:
                with open(bind_path, 'w') as f:
                    f.write(device_id)
                print("Bind completado exitosamente")
            except PermissionError:
                raise Exception("Permisos insuficientes para realizar bind. Ejecute como root o agregue reglas udev")
            except Exception as e:
                raise Exception(f"Error en bind: {str(e)}")
            
            # Esperar un poco más para que el dispositivo se estabilice
            print("Esperando estabilización del dispositivo...")
            time.sleep(2)
            
            # Reinicializar el SDK después del reset
            print("Reinicializando SDK después del reset USB...")
            success = self.initializeDevice()
            
            if success:
                print("Reset USB completado exitosamente")
                return True
            else:
                print("Reset USB completado pero falló la reinicialización del SDK")
                return False
                
        except Exception as e:
            print(f"Error en reset_usb_device: {str(e)}")
            raise e
    
    def initializeDevice(self):
        try:
            print("Iniciando dispositivo...")
            err = self.sgfp.Create()
            if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                raise Exception(f"Error al crear la instancia: {err}")

            print("Inicializando...")
            err = self.sgfp.Init(1)
            if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                raise Exception(f"Error al inicializar: {err}")

            print("Abriendo dispositivo...")
            # Intentar con diferentes IDs de dispositivo
            device_ids = [0, 1]  # Podemos agregar más IDs si es necesario
            device_opened = False
            
            for device_id in device_ids:
                print(f"Intentando abrir dispositivo con ID: {device_id}")
                err = self.sgfp.OpenDevice(device_id)
                if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    device_opened = True
                    print(f"Dispositivo abierto exitosamente con ID: {device_id}")
                    break
                else:
                    print(f"No se pudo abrir dispositivo con ID {device_id}, error: {err}")
            
            if not device_opened:
                raise Exception(f"No se pudo abrir el dispositivo con ningún ID")

            self.initialized = True
            print("Dispositivo inicializado correctamente")
            return True
        except Exception as e:
            self.init_error = str(e)
            print(f"Error en initializeDevice: {str(e)}")
            return False
    
    def recover_if_needed(self):
        """Cierra el dispositivo y lo reinicializa para recuperar de estados corruptos"""
        try:
            print("Iniciando proceso de recuperación del dispositivo...")
            
            # Cerrar el dispositivo si está inicializado
            if self.initialized and self.sgfp:
                print("Cerrando dispositivo...")
                try:
                    self.sgfp.CloseDevice()
                    print("Dispositivo cerrado exitosamente")
                except Exception as e:
                    print(f"Error al cerrar dispositivo: {e}")
            
            # Marcar como no inicializado
            self.initialized = False
            self.init_error = None
            
            # Reinicializar el dispositivo
            print("Reinicializando dispositivo...")
            success = self.initializeDevice()
            
            if success:
                print("Recuperación completada exitosamente")
                return True
            else:
                print(f"Error en la recuperación: {self.init_error}")
                return False
                
        except Exception as e:
            print(f"Error en recover_if_needed: {str(e)}")
            self.init_error = str(e)
            return False
    
    def led_control(self, state):
        try:
            if not self.initialized:
                # Intentar reinicializar si falló anteriormente
                if not self.initializeDevice():
                    raise Exception(f"Dispositivo no inicializado. Error original: {self.init_error}")
            
            print(f"Intentando {'encender' if state else 'apagar'} el LED del lector...")
            
            result = self.sgfp.SetLedOn(state)
            print(f"Resultado de SetLedOn: {result}")
            
            if result != SGFDxErrorCode.SGFDX_ERROR_NONE:
                error_msg = {
                    2: "Error de acceso al dispositivo. Verifique permisos y conexión USB",
                    3: "Error de índice del dispositivo",
                    4: "Dispositivo no encontrado",
                    5: "Error al abrir el dispositivo"
                }.get(result, f"Error desconocido: {result}")
                
                raise Exception(f"Error al controlar LED: {error_msg}")
            
            return {"success": True, "message": f"LED del lector {'encendido' if state else 'apagado'}"}
        except Exception as e:
            print(f"Error en led_control: {str(e)}")
            return {"success": False, "error": str(e)}

    def create_template(self, image_buffer):
        """Crear template a partir de una imagen de huella"""
        try:
            # Por ahora deshabilitamos la creación de template para evitar problemas
            # Se puede habilitar cuando se solucionen los problemas de tipos
            print("Función create_template deshabilitada temporalmente")
            return None
        except Exception as e:
            print(f"Error en create_template: {str(e)}")
            return None

    def compare_templates(self, template1, template2, security_level=1):
        """Comparar dos templates de huellas"""
        try:
            # Función simplificada para evitar problemas con ctypes
            # Simulamos una comparación básica basada en el contenido
            import hashlib
            
            # Crear hashes de los templates para comparación
            hash1 = hashlib.md5(template1 if isinstance(template1, bytes) else bytes(template1)).hexdigest()
            hash2 = hashlib.md5(template2 if isinstance(template2, bytes) else bytes(template2)).hexdigest()
            
            # Comparación simple: exactamente iguales
            matched = hash1 == hash2
            
            # Simulamos un score básico
            score = 100 if matched else 0
            
            return {
                'success': True,
                'matched': matched,
                'score': score,
                'message': 'Comparación exitosa (simplificada)'
            }
        except Exception as e:
            print(f"Error en compare_templates: {str(e)}")
            return {'success': False, 'error': str(e)}

    def store_template(self, template_id, template_data):
        """Almacenar template de referencia"""
        try:
            self.stored_templates[template_id] = template_data
            return {'success': True, 'message': f'Template {template_id} almacenado'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_stored_templates(self):
        """Obtener lista de templates almacenados"""
        return list(self.stored_templates.keys())

controller = SecugenController()

@app.route('/initialize', methods=['POST'])
def initialize_device():
    try:
        if controller.initialized:
            return jsonify({
                "success": True,
                "message": "Dispositivo ya está inicializado correctamente"
            })
        
        result = controller.initializeDevice()
        if result:
            return jsonify({
                "success": True,
                "message": "Dispositivo inicializado correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Error al inicializar: {controller.init_error}"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/reset-usb', methods=['POST'])
def reset_usb():
    """Endpoint para resetear el dispositivo USB SecuGen"""
    try:
        print("Solicitud de reset USB recibida...")
        
        # Realizar el reset del dispositivo USB
        success = controller.reset_usb_device()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Lector USB reseteado correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Reset USB completado pero falló la reinicialización del SDK"
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error en reset_usb: {error_msg}")
        
        # Agregar información de diagnóstico para errores comunes
        if "Permisos insuficientes" in error_msg:
            error_msg += ". Solución: Ejecute la aplicación como root o configure reglas udev para el dispositivo SecuGen"
        elif "No se encontró dispositivo SecuGen" in error_msg:
            error_msg += ". Verifique que el dispositivo esté conectado y sea reconocido por el sistema"
        
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@app.route('/led', methods=['POST'])
def control_led():
    try:
        data = request.get_json()
        if data is None:
            raise Exception("No se recibieron datos JSON")
        
        state = data.get('state', False)
        result = controller.led_control(state)
        
        if not result['success']:
            # Intentar reinicializar el dispositivo si hay error
            print("Intentando reinicializar el dispositivo...")
            controller.initializeDevice()
            result = controller.led_control(state)
            
            if not result['success']:
                raise Exception(result['error'])
            
        return jsonify({
            "success": True,
            "message": result['message']
        })
    except Exception as e:
        error_msg = str(e)
        # Agregar información de diagnóstico
        if "Error de acceso al dispositivo" in error_msg:
            error_msg += ". Verifique: \n1. El dispositivo está conectado\n2. Las reglas udev están instaladas\n3. El usuario tiene permisos suficientes"
        
        return jsonify({
            "success": False,
            "error": error_msg
        }), 500

@app.route('/capturar-huella', methods=['POST'])
def capturar_huella():
    try:
        data = request.get_json() or {}
        save_image = data.get('save_image', False)  # Por defecto no guardar
        create_template = data.get('create_template', False)  # Por defecto no crear template
        template_id = data.get('template_id', None)  # ID para almacenar template
        
        # Inicializar variables para width y height
        width = c_long(258)    # Ancho típico del sensor
        height = c_long(336)   # Alto típico del sensor
        
        print("Obteniendo información del dispositivo...")
        err = controller.sgfp.GetDeviceInfo(width, height)
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            raise Exception(f'Error al obtener información del dispositivo: {err}')
        
        print(f"Dimensiones del sensor: {width.value}x{height.value}")
        
        # Crear buffer del tamaño correcto
        buffer_size = width.value * height.value
        imageBuffer = bytearray(buffer_size)
        
        print("Encendiendo LED...")
        controller.led_control(True)  # Encender LED
        
        print("Capturando imagen...")
        print("Tamaño del buffer:", len(imageBuffer))
        
        # Modificación de intentos y tiempo de espera
        max_attempts = 5  # Aumentado de 3 a 5 intentos
        wait_time = 3    # Aumentado de 1 a 3 segundos
        
        for attempt in range(max_attempts):
            print(f"Intento {attempt + 1} de {max_attempts}")
            err = controller.sgfp.GetImage(imageBuffer)
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                break
            time.sleep(wait_time)  # Espera 3 segundos entre intentos
        
        print("Apagando LED...")
        controller.led_control(False)  # Apagar LED después de la captura
        
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"Error al capturar la huella después de {max_attempts} intentos: {err}")
            print("Iniciando proceso de recuperación del dispositivo...")
            controller.recover_if_needed()
            raise Exception(f'Error al capturar la huella: {err}')

        # Convertir a base64
        imagen_base64 = base64.b64encode(bytes(imageBuffer)).decode('utf-8')
        
        # Crear template si se solicita
        template_base64 = None
        if create_template:
            template_data = controller.create_template(imageBuffer)
            if template_data:
                template_base64 = base64.b64encode(bytes(template_data)).decode('utf-8')
                
                # Almacenar template si se proporciona ID
                if template_id:
                    controller.store_template(template_id, template_data)
        
        # Guardar la imagen solo si se solicita
        if save_image:
            try:
                with open('/app/images/huella.png', 'wb') as f:
                    f.write(base64.b64decode(imagen_base64))
            except Exception as e:
                print(f"Error al guardar imagen: {e}")
                pass
        
        return jsonify({
            'success': True,
            'data': {
                'imagen': imagen_base64,
                'template': template_base64,
                'width': width.value,
                'height': height.value,
                'mensaje': 'Huella capturada exitosamente',
                'template_stored': template_id if template_id and template_base64 else None
            }
        })

    except Exception as e:
        # Asegurarse de apagar el LED en caso de error
        try:
            controller.led_control(False)
        except:
            pass
        print(f"Error en capturar_huella: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/comparar-huellas', methods=['POST'])
def comparar_huellas():
    try:
        data = request.get_json()
        if not data:
            raise Exception("No se recibieron datos JSON")
        
        # Opciones de comparación
        template1_id = data.get('template1_id')
        template2_id = data.get('template2_id')
        template1_data = data.get('template1_data')  # Base64
        template2_data = data.get('template2_data')  # Base64
        security_level = data.get('security_level', 1)  # Nivel de seguridad por defecto
        
        # Obtener templates para comparar
        if template1_id and template1_id in controller.stored_templates:
            template1 = controller.stored_templates[template1_id]
        elif template1_data:
            template1 = bytearray(base64.b64decode(template1_data))
        else:
            raise Exception("No se proporcionó template1 válido")
        
        if template2_id and template2_id in controller.stored_templates:
            template2 = controller.stored_templates[template2_id]
        elif template2_data:
            template2 = bytearray(base64.b64decode(template2_data))
        else:
            raise Exception("No se proporcionó template2 válido")
        
        # Comparar templates
        result = controller.compare_templates(template1, template2, security_level)
        
        if result['success']:
            return jsonify({
                'success': True,
                'matched': result['matched'],
                'score': result['score'],
                'message': result['message'],
                'comparison_info': {
                    'template1_source': template1_id if template1_id else 'data',
                    'template2_source': template2_id if template2_id else 'data',
                    'security_level': security_level
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        print(f"Error en comparar_huellas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/templates', methods=['GET'])
def listar_templates():
    try:
        templates = controller.get_stored_templates()
        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates)
        })
    except Exception as e:
        print(f"Error en listar_templates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/templates/<template_id>', methods=['DELETE'])
def eliminar_template(template_id):
    try:
        if template_id in controller.stored_templates:
            del controller.stored_templates[template_id]
            return jsonify({
                'success': True,
                'message': f'Template {template_id} eliminado'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Template no encontrado'
            }), 404
    except Exception as e:
        print(f"Error en eliminar_template: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 