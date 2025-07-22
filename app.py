from flask import Flask, request, jsonify
from flask_cors import CORS
from sdk import PYSGFPLib
from sdk.sgfdxerrorcode import SGFDxErrorCode
import base64
from ctypes import c_int, byref, c_long, c_ubyte, POINTER, c_bool
import time
import sys
import os

app = Flask(__name__)
CORS(app)

class SecugenController:
    def __init__(self):
        self.sgfp = None
        self.initialized = False
        self.init_error = None
        self.stored_templates = {}  # Para almacenar templates de referencia
        self.device_opened = False
        self.current_device_id = None
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
        self.last_error_time = None
        
        # PREVENCIÓN: Control de recursos y operaciones
        import threading
        self.operation_lock = threading.Lock()  # Prevenir operaciones concurrentes
        self.operation_count = 0  # Contador de operaciones para limpieza preventiva
        self.max_operations_before_refresh = 50  # Límite antes de refrescar SDK
        self.last_successful_operation = time.time()
        self.device_health_threshold = 300  # 5 minutos sin problemas = sano
        try:
            self.sgfp = PYSGFPLib()
            self.initializeDevice()
        except Exception as e:
            self.init_error = str(e)
            print(f"Error al crear instancia de SecugenController: {e}")

    def preventive_maintenance(self):
        """Mantenimiento preventivo del SDK para evitar acumulación de recursos"""
        try:
            current_time = time.time()
            
            # Si han pasado muchas operaciones, refrescar el SDK
            if self.operation_count >= self.max_operations_before_refresh:
                print(f"=== MANTENIMIENTO PREVENTIVO: {self.operation_count} operaciones ===")
                self._refresh_sdk_connection()
                self.operation_count = 0
                return True
                
            # Si ha pasado mucho tiempo sin operaciones exitosas, verificar salud
            if (current_time - self.last_successful_operation) > self.device_health_threshold:
                print("=== VERIFICACIÓN PREVENTIVA: Tiempo excedido sin operaciones ===")
                if not self._health_check():
                    print("Health check falló, refrescando conexión...")
                    self._refresh_sdk_connection()
                    return True
                    
            return False
        except Exception as e:
            print(f"Error en mantenimiento preventivo: {e}")
            return False
    
    def _health_check(self):
        """Verificación rápida de salud del dispositivo"""
        try:
            if not self.initialized:
                return False
                
            # Test simple: obtener info del dispositivo
            width = c_long(0)
            height = c_long(0)
            result = self.sgfp.GetDeviceInfo(width, height)
            return result == SGFDxErrorCode.SGFDX_ERROR_NONE
        except:
            return False
    
    def _refresh_sdk_connection(self):
        """Refresca la conexión del SDK sin perder el estado inicializado"""
        try:
            print("Refrescando conexión SDK...")
            
            # Cerrar conexión actual
            if self.sgfp:
                try:
                    self.sgfp.CloseDevice()
                except:
                    pass
            
            # Breve pausa para limpiar recursos
            time.sleep(1)
            
            # Reinicializar SDK
            self.sgfp = PYSGFPLib()
            self.sgfp.Init()
            
            # Reabrir dispositivo
            if self.current_device_id is not None:
                result = self.sgfp.OpenDevice(self.current_device_id)
                if result == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    print("Conexión SDK refrescada exitosamente")
                    self.last_successful_operation = time.time()
                    return True
            
            # Si no hay device_id guardado, buscar nuevamente
            return self._reconnect_device()
            
        except Exception as e:
            print(f"Error al refrescar conexión SDK: {e}")
            return False
    
    def _reconnect_device(self):
        """Reconecta al dispositivo buscando en todos los IDs disponibles"""
        try:
            for device_id in [0, 1]:
                result = self.sgfp.OpenDevice(device_id)
                if result == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    self.current_device_id = device_id
                    print(f"Dispositivo reconectado exitosamente con ID: {device_id}")
                    self.last_successful_operation = time.time()
                    return True
            return False
        except Exception as e:
            print(f"Error al reconectar dispositivo: {e}")
            return False
    
    def auto_recovery(self):
        """Intenta recuperación automática del dispositivo con múltiples niveles"""
        import time
        
        current_time = time.time()
        
        # Evitar intentos de recuperación muy frecuentes
        if self.last_error_time and (current_time - self.last_error_time) < 3:
            print("Esperando antes del siguiente intento de recuperación...")
            return False
        
        if self.recovery_attempts >= self.max_recovery_attempts:
            print(f"Máximo de intentos de recuperación alcanzado ({self.max_recovery_attempts})")
            # Intentar reset USB como último recurso
            return self._emergency_usb_reset()
        
        self.recovery_attempts += 1
        self.last_error_time = current_time
        
        print(f"=== INTENTO DE RECUPERACIÓN AUTOMÁTICA #{self.recovery_attempts} ===")
        
        try:
            # Recuperación por niveles según el intento
            if self.recovery_attempts == 1:
                # Nivel 1: Recuperación básica
                return self._basic_recovery()
            elif self.recovery_attempts == 2:
                # Nivel 2: Recuperación con pausa larga
                return self._extended_recovery()
            else:
                # Nivel 3: Recuperación profunda
                return self._deep_recovery()
                
        except Exception as e:
            print(f"Error durante recuperación automática: {e}")
            return False
    
    def _basic_recovery(self):
        """Recuperación básica - rápida"""
        import time
        print("Ejecutando recuperación básica...")
        
        try:
            if self.sgfp:
                print("Cerrando dispositivo actual...")
                self.sgfp.CloseDevice()
        except:
            pass
        
        self.initialized = False
        self.device_opened = False
        time.sleep(2)
        
        result = self.initializeDevice()
        if result:
            print("=== RECUPERACIÓN BÁSICA EXITOSA ===")
            self.recovery_attempts = 0
            return True
        
        print("Recuperación básica falló")
        return False
    
    def _extended_recovery(self):
        """Recuperación extendida - con pausa larga"""
        import time
        print("Ejecutando recuperación extendida...")
        
        try:
            if self.sgfp:
                self.sgfp.CloseDevice()
        except:
            pass
        
        # Reset más completo
        self.initialized = False
        self.device_opened = False
        self.sgfp = None
        
        print("Pausa extendida de 5 segundos...")
        time.sleep(5)
        
        # Recrear instancia completa
        try:
            from sdk import PYSGFPLib
            self.sgfp = PYSGFPLib()
            result = self.initializeDevice()
            
            if result:
                print("=== RECUPERACIÓN EXTENDIDA EXITOSA ===")
                self.recovery_attempts = 0
                return True
        except Exception as e:
            print(f"Error en recuperación extendida: {e}")
        
        print("Recuperación extendida falló")
        return False
    
    def _deep_recovery(self):
        """Recuperación profunda - reset completo con verificaciones"""
        import time
        print("Ejecutando recuperación profunda...")
        
        # Reset total del estado
        try:
            if self.sgfp:
                self.sgfp.CloseDevice()
        except:
            pass
        
        self.initialized = False
        self.device_opened = False
        self.sgfp = None
        self.init_error = None
        
        print("Pausa profunda de 8 segundos...")
        time.sleep(8)
        
        # Recrear desde cero con verificaciones
        try:
            from sdk import PYSGFPLib
            print("Recreando instancia SDK...")
            self.sgfp = PYSGFPLib()
            
            # Múltiples intentos de inicialización
            for attempt in range(3):
                print(f"Intento de inicialización profunda {attempt + 1}/3")
                time.sleep(2)
                
                result = self.initializeDevice()
                if result:
                    print("=== RECUPERACIÓN PROFUNDA EXITOSA ===")
                    self.recovery_attempts = 0
                    return True
                
                print(f"Intento {attempt + 1} falló, continuando...")
        
        except Exception as e:
            print(f"Error en recuperación profunda: {e}")
        
        print("Recuperación profunda falló")
        return False
    
    def _emergency_usb_reset(self):
        """Reset USB de emergencia cuando todo lo demás falla"""
        print("=== INICIANDO RESET USB DE EMERGENCIA ===")
        
        try:
            import subprocess
            import time
            
            # Buscar dispositivo USB
            result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
            secugen_line = None
            for line in result.stdout.split('\n'):
                if 'Secugen' in line or '1162:' in line:
                    secugen_line = line
                    break
            
            if secugen_line:
                parts = secugen_line.split()
                bus = parts[1]
                device = parts[3].rstrip(':')
                
                print(f"Reset USB de emergencia - Bus: {bus}, Device: {device}")
                
                # Reset USB usando authorized
                reset_path = f"/sys/bus/usb/devices/{bus}-{device}/authorized"
                
                try:
                    # Desautorizar
                    subprocess.run(['sudo', 'sh', '-c', f'echo 0 > {reset_path}'], 
                                  capture_output=True, timeout=5)
                    time.sleep(2)
                    
                    # Reautorizar
                    subprocess.run(['sudo', 'sh', '-c', f'echo 1 > {reset_path}'], 
                                  capture_output=True, timeout=5)
                    time.sleep(5)
                    
                    # Reinicializar después del reset USB
                    self.initialized = False
                    self.device_opened = False
                    self.sgfp = None
                    self.recovery_attempts = 0
                    
                    from sdk import PYSGFPLib
                    self.sgfp = PYSGFPLib()
                    result = self.initializeDevice()
                    
                    if result:
                        print("=== RESET USB DE EMERGENCIA EXITOSO ===")
                        return True
                    
                except Exception as usb_error:
                    print(f"Error en reset USB: {usb_error}")
            
            print("Reset USB de emergencia falló")
            return False
            
        except Exception as e:
            print(f"Error crítico en reset de emergencia: {e}")
            return False

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
                    self.current_device_id = device_id  # PREVENCIÓN: Guardar ID para reconexión
                    print(f"Dispositivo abierto exitosamente con ID: {device_id}")
                    break
                else:
                    print(f"No se pudo abrir dispositivo con ID {device_id}, error: {err}")
            
            if not device_opened:
                raise Exception(f"No se pudo abrir el dispositivo con ningún ID")

            self.initialized = True
            self.last_successful_operation = time.time()  # PREVENCIÓN: Actualizar tiempo de éxito
            print("Dispositivo inicializado correctamente")
            return True
        except Exception as e:
            self.init_error = str(e)
            print(f"Error en initializeDevice: {str(e)}")
            return False
    
    def led_control(self, state):
        with self.operation_lock:  # PREVENCIÓN: Evitar operaciones concurrentes
            try:
                # PREVENCIÓN: Mantenimiento antes de cada operación crítica
                self.preventive_maintenance()
                
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
                    
                    # Intentar recuperación automática si es error de acceso
                    if result == 2:  # Error de acceso al dispositivo
                        print("Detectado error de acceso, intentando recuperación automática...")
                        if self.auto_recovery():
                            # Reintentar la operación después de la recuperación
                            print("Reintentando operación LED después de recuperación...")
                            retry_result = self.sgfp.SetLedOn(state)
                            if retry_result == SGFDxErrorCode.SGFDX_ERROR_NONE:
                                # PREVENCIÓN: Operación exitosa tras recuperación
                                self.last_successful_operation = time.time()
                                self.operation_count += 1
                                return {"success": True, "message": f"LED del lector {'encendido' if state else 'apagado'} (tras recuperación)"}
                    
                    raise Exception(f"Error al controlar LED: {error_msg}")
                
                # PREVENCIÓN: Operación exitosa
                self.last_successful_operation = time.time()
                self.operation_count += 1
                return {"success": True, "message": f"LED del lector {'encendido' if state else 'apagado'}"}
            except Exception as e:
                print(f"Error en led_control: {str(e)}")
                return {"success": False, "error": str(e)}

    def create_template(self, image_buffer):
        """Crear template a partir de una imagen de huella"""
        try:
            if not self.initialized:
                print("Dispositivo no inicializado")
                return None
            
            from ctypes import c_char
            
            # Crear buffer para el template (SG400 template size = 400 bytes)
            template_buffer = (c_char * self.sgfp.constant_sg400_template_size)()
            
            # Convertir image_buffer a formato ctypes si es necesario
            if isinstance(image_buffer, bytearray):
                image_data = (c_char * len(image_buffer)).from_buffer(image_buffer)
            else:
                image_data = image_buffer
            
            print("Creando template desde imagen...")
            result = self.sgfp.CreateSG400Template(image_data, template_buffer)
            
            if result != SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"Error al crear template: {result}")
                return None
            
            print("Template creado exitosamente")
            return bytearray(template_buffer)
            
        except Exception as e:
            print(f"Error en create_template: {str(e)}")
            return None

    def compare_templates(self, template1, template2, security_level=5):
        """Comparar dos templates de huellas usando el SDK de SecuGen"""
        try:
            if not self.initialized:
                print("Dispositivo no inicializado")
                return {'success': False, 'error': 'Dispositivo no inicializado'}
            
            from ctypes import c_char, c_bool, c_int, byref
            from sdk.sgfdxsecuritylevel import SGFDxSecurityLevel
            
            # Convertir templates a formato ctypes
            template1_buffer = (c_char * self.sgfp.constant_sg400_template_size)()
            template2_buffer = (c_char * self.sgfp.constant_sg400_template_size)()
            
            # Copiar los datos de los templates
            if isinstance(template1, bytearray):
                for i, byte in enumerate(template1[:self.sgfp.constant_sg400_template_size]):
                    template1_buffer[i] = byte
            else:
                template1_bytes = bytes(template1)
                for i, byte in enumerate(template1_bytes[:self.sgfp.constant_sg400_template_size]):
                    template1_buffer[i] = byte
            
            if isinstance(template2, bytearray):
                for i, byte in enumerate(template2[:self.sgfp.constant_sg400_template_size]):
                    template2_buffer[i] = byte
            else:
                template2_bytes = bytes(template2)
                for i, byte in enumerate(template2_bytes[:self.sgfp.constant_sg400_template_size]):
                    template2_buffer[i] = byte
            
            # Realizar la comparación usando el SDK
            matched = c_bool(False)
            print(f"Comparando templates con nivel de seguridad: {security_level}")
            
            result = self.sgfp.MatchTemplate(
                template1_buffer, 
                template2_buffer, 
                security_level, 
                byref(matched)
            )
            
            if result != SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"Error en MatchTemplate: {result}")
                return {'success': False, 'error': f'Error en comparación: {result}'}
            
            # Obtener el score de matching
            score = c_int(0)
            score_result = self.sgfp.GetMatchingScore(
                template1_buffer,
                template2_buffer, 
                byref(score)
            )
            
            final_score = score.value if score_result == SGFDxErrorCode.SGFDX_ERROR_NONE else 0
            
            print(f"Resultado de comparación: {'MATCH' if matched.value else 'NO MATCH'}, Score: {final_score}")
            
            return {
                'success': True,
                'matched': bool(matched.value),
                'score': final_score,
                'message': f'Comparación exitosa usando SDK SecuGen'
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
    with controller.operation_lock:  # PREVENCIÓN: Evitar operaciones concurrentes críticas
        try:
            # PREVENCIÓN: Mantenimiento preventivo antes de operaciones críticas
            controller.preventive_maintenance()
            
            data = request.get_json() or {}
            save_image = data.get('save_image', False)  # Por defecto no guardar
            create_template = data.get('create_template', False)  # Por defecto no crear template
            template_id = data.get('template_id', None)  # ID para almacenar template
            
            # Inicializar variables para width y height
            width = c_long(258)    # Ancho típico del sensor
            height = c_long(336)   # Alto típico del sensor
            
            # Verificar estado del dispositivo antes de continuar
            if not controller.initialized:
                print("Dispositivo no inicializado, intentando recuperación...")
                if not controller.auto_recovery():
                    raise Exception("No se pudo inicializar el dispositivo tras múltiples intentos")
        
        print("Obteniendo información del dispositivo...")
        err = controller.sgfp.GetDeviceInfo(width, height)
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            # Intentar recuperación automática si falla GetDeviceInfo
            print(f"Error al obtener info del dispositivo: {err}, intentando recuperación...")
            if controller.auto_recovery():
                # Reintentar después de recuperación
                err = controller.sgfp.GetDeviceInfo(width, height)
                if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                    raise Exception(f'Error al obtener información del dispositivo tras recuperación: {err}')
            else:
                raise Exception(f'Error al obtener información del dispositivo: {err}')
        
        print(f"Dimensiones del sensor: {width.value}x{height.value}")
        
        # Validar dimensiones antes de crear buffer (SEGURIDAD)
        if width.value <= 0 or height.value <= 0 or width.value > 1000 or height.value > 1000:
            raise Exception(f"Dimensiones del sensor inválidas: {width.value}x{height.value}")
        
        # Crear buffer del tamaño correcto con protección
        buffer_size = width.value * height.value
        if buffer_size > 1000000:  # Máximo 1MB de buffer
            raise Exception(f"Buffer de imagen demasiado grande: {buffer_size} bytes")
        
        try:
            imageBuffer = bytearray(buffer_size)
        except MemoryError:
            raise Exception(f"No se pudo asignar memoria para buffer de {buffer_size} bytes")
        
        print("Encendiendo LED...")
        led_result = controller.led_control(True)  # Encender LED
        
        if not led_result.get('success', False):
            print(f"Advertencia: No se pudo encender LED: {led_result.get('error')}")
            # Continuar sin LED si es necesario
        
        print("Capturando imagen...")
        print("Tamaño del buffer:", len(imageBuffer))
        
        # Modificación de intentos y tiempo de espera con timeout total
        max_attempts = 3  # Reducido para evitar bloqueos largos
        wait_time = 1    # Reducido a 1 segundo
        total_timeout = 10  # Máximo 10 segundos total
        start_time = time.time()
        
        capture_success = False
        for attempt in range(max_attempts):
            print(f"Intento {attempt + 1} de {max_attempts}")
            
            # Verificar timeout total
            if (time.time() - start_time) > total_timeout:
                print("Timeout total alcanzado, abortando captura")
                break
            
            try:
                err = controller.sgfp.GetImage(imageBuffer)
                if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                    capture_success = True
                    break
                elif err == 2:  # Error de acceso al dispositivo
                    print("Error de acceso detectado, intentando recuperación...")
                    if controller.auto_recovery():
                        print("Recuperación exitosa, reintentando captura...")
                        continue
                    else:
                        print("Recuperación falló")
                        break
                else:
                    print(f"Error en captura: {err}")
            except Exception as capture_error:
                print(f"Excepción durante captura: {capture_error}")
                break
            
            if attempt < max_attempts - 1:  # No esperar después del último intento
                time.sleep(wait_time)
        
        # Siempre intentar apagar LED, incluso si hay errores
        print("Apagando LED...")
        try:
            controller.led_control(False)
        except Exception as led_error:
            print(f"Error al apagar LED: {led_error}")
            # No es crítico si no se puede apagar el LED
        
        if not capture_success:
            raise Exception(f'Error al capturar la huella tras {max_attempts} intentos. Último error: {err if "err" in locals() else "Timeout o error desconocido"}')

        # Convertir a base64
        imagen_base64 = base64.b64encode(bytes(imageBuffer)).decode('utf-8')
        
        # Crear template si se solicita (con manejo de errores mejorado)
        template_base64 = None
        template_created = False
        if create_template:
            try:
                print("Iniciando creación de template...")
                template_data = controller.create_template(imageBuffer)
                if template_data and len(template_data) > 0:
                    template_base64 = base64.b64encode(bytes(template_data)).decode('utf-8')
                    template_created = True
                    print(f"Template creado exitosamente, tamaño: {len(template_data)} bytes")
                    
                    # Almacenar template si se proporciona ID
                    if template_id:
                        try:
                            store_result = controller.store_template(template_id, template_data)
                            print(f"Template almacenado con ID {template_id}: {store_result}")
                        except Exception as store_error:
                            print(f"Advertencia: Error al almacenar template: {store_error}")
                            # No es crítico si no se puede almacenar
                else:
                    print("Advertencia: No se pudo crear template válido")
            except Exception as template_error:
                print(f"Advertencia: Error en creación de template: {template_error}")
                # No lanzar excepción, solo continuar sin template
        
        # Guardar la imagen solo si se solicita
        if save_image:
            try:
                with open('/app/images/huella.png', 'wb') as f:
                    f.write(base64.b64decode(imagen_base64))
            except Exception as e:
                print(f"Error al guardar imagen: {e}")
                pass
        
        # PREVENCIÓN: Operación exitosa - actualizar contadores
        controller.last_successful_operation = time.time()
        controller.operation_count += 1
        
        return jsonify({
            'success': True,
            'data': {
                'imagen': imagen_base64,
                'template': template_base64,
                'template_created': template_created,
                'width': width.value,
                'height': height.value,
                'buffer_size': buffer_size,
                'mensaje': 'Huella capturada exitosamente',
                'template_stored': template_id if template_id and template_created else None,
                'capture_attempts': max_attempts,
                'device_status': 'responsive',
                'operation_count': controller.operation_count,  # DIAGNÓSTICO: Mostrar contador de operaciones
                'last_maintenance': controller.operation_count >= controller.max_operations_before_refresh - 10  # Advertir si se acerca mantenimiento
            }
        })

    except Exception as e:
        # Asegurarse de apagar el LED en caso de error
        try:
            print("Apagando LED tras error...")
            controller.led_control(False)
        except Exception as led_cleanup_error:
            print(f"Error al apagar LED durante limpieza: {led_cleanup_error}")
            pass
        
        error_msg = str(e)
        print(f"Error en capturar_huella: {error_msg}")
        
        # Agregar información de diagnóstico
        diagnostic_info = {
            'error': error_msg,
            'device_initialized': controller.initialized,
            'recovery_attempts': getattr(controller, 'recovery_attempts', 0),
            'timestamp': time.time(),
            'suggestion': 'Verifique la conexión del dispositivo y reinicie si persiste el error'
        }
        
        return jsonify(diagnostic_info), 500

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
        security_level = data.get('security_level', 5)  # SL_NORMAL por defecto
        
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

@app.route('/reset-device', methods=['POST'])
def reset_device():
    """Resetear completamente el dispositivo lector de huellas"""
    try:
        print("=== INICIANDO RESET COMPLETO DEL DISPOSITIVO ===")
        
        # 1. Cerrar dispositivo actual si está abierto
        try:
            if hasattr(controller, 'sgfp') and controller.sgfp:
                print("Cerrando dispositivo actual...")
                controller.sgfp.CloseDevice()
                print("Dispositivo cerrado")
        except Exception as e:
            print(f"Error al cerrar dispositivo: {e}")
        
        # 2. Reset del estado interno
        controller.initialized = False
        controller.device_opened = False
        controller.current_device_id = None
        controller.recovery_attempts = 0  # Reset del contador también
        print("Estado interno reseteado")
        
        # 3. Pausa para permitir que el dispositivo se libere
        import time
        print("Esperando 2 segundos para liberar el dispositivo...")
        time.sleep(2)
        
        # 4. Reinicializar completamente
        print("Reinicializando dispositivo...")
        result = controller.initializeDevice()
        
        if result:
            print("=== RESET COMPLETO EXITOSO ===")
            return jsonify({
                'success': True,
                'message': 'Dispositivo reseteado e inicializado exitosamente',
                'device_ready': True
            })
        else:
            print("=== RESET FALLÓ ===")
            return jsonify({
                'success': False,
                'message': 'Error al reinicializar el dispositivo después del reset',
                'device_ready': False
            }), 500
            
    except Exception as e:
        print(f"Error durante el reset: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error durante el reset: {str(e)}',
            'device_ready': False
        }), 500

@app.route('/device-status', methods=['GET'])
def device_status():
    """Obtener el estado actual del dispositivo"""
    try:
        status = {
            'initialized': controller.initialized,
            'device_opened': hasattr(controller, 'device_opened') and controller.device_opened,
            'current_device_id': getattr(controller, 'current_device_id', None)
        }
        
        # Intentar obtener info del dispositivo para verificar si está realmente funcionando
        try:
            if controller.initialized and controller.sgfp:
                from ctypes import c_long
                width = c_long(0)
                height = c_long(0)
                err = controller.sgfp.GetDeviceInfo(width, height)
                if err == 0:  # SGFDxErrorCode.SGFDX_ERROR_NONE
                    status['device_responsive'] = True
                    status['image_dimensions'] = {'width': width.value, 'height': height.value}
                else:
                    status['device_responsive'] = False
                    status['last_error'] = f'Error GetDeviceInfo: {err}'
            else:
                status['device_responsive'] = False
        except Exception as e:
            status['device_responsive'] = False
            status['last_error'] = str(e)
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
#test
@app.route('/force-usb-reset', methods=['POST'])
def force_usb_reset():
    """Intento de reset USB programático (experimental)"""
    try:
        print("=== INICIANDO RESET USB PROGRAMÁTICO ===")
        
        # Buscar el dispositivo USB
        import subprocess
        import time
        
        # Obtener información del dispositivo USB
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        secugen_line = None
        for line in result.stdout.split('\n'):
            if 'Secugen' in line or '1162:' in line:
                secugen_line = line
                break
        
        if not secugen_line:
            return jsonify({
                'success': False,
                'message': 'Dispositivo SecuGen no encontrado en USB'
            }), 404
        
        print(f"Dispositivo encontrado: {secugen_line}")
        
        # Extraer bus y device
        parts = secugen_line.split()
        bus = parts[1]
        device = parts[3].rstrip(':')
        
        print(f"Bus: {bus}, Device: {device}")
        
        # Intentar reset USB usando el kernel
        try:
            # Método 1: Reset por archivo de sistema
            reset_path = f"/sys/bus/usb/devices/{bus}-{device}/authorized"
            
            # Desautorizar
            subprocess.run(['sudo', 'sh', '-c', f'echo 0 > {reset_path}'], 
                          capture_output=True, timeout=5)
            time.sleep(1)
            
            # Reautorizar
            subprocess.run(['sudo', 'sh', '-c', f'echo 1 > {reset_path}'], 
                          capture_output=True, timeout=5)
            time.sleep(3)  # Esperar re-enumeración
            
            print("Reset USB con authorized/unauthorized completado")
            
            # Intentar reinicializar
            controller.initialized = False
            controller.device_opened = False
            result = controller.initializeDevice()
            
            return jsonify({
                'success': True,
                'message': 'Reset USB programático exitoso',
                'method': 'authorize_reset',
                'device_reinitialized': result
            })
            
        except Exception as e:
            print(f"Método authorize/unauthorize falló: {e}")
        
        # Si llegamos aquí, los métodos programáticos fallaron
        return jsonify({
            'success': False,
            'message': 'Los métodos de reset USB programático fallaron. Puede requerirse desconexión física.',
            'recommendation': 'Usar /reset-device primero, si falla contactar soporte técnico'
        }), 500
        
    except Exception as e:
        print(f"Error en force_usb_reset: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error en reset USB: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 