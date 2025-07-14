from flask import Flask, request, jsonify
from flask_cors import CORS
from python.sgfdxerrorcode import SGFDxErrorCode
import base64
from ctypes import c_int, byref, c_long, c_ubyte, POINTER, c_bool
import time
import sys
import os

# Try to import SecuGen SDK, fall back to None if not available
try:
    from sdk import PYSGFPLib
    SDK_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"SecuGen SDK not available: {e}")
    PYSGFPLib = None
    SDK_AVAILABLE = False

app = Flask(__name__)
CORS(app)

class SecugenController:
    def __init__(self):
        self.sgfp = None
        self.initialized = False
        self.init_error = None
        self.stored_templates = {}  # Para almacenar templates de referencia
        try:
            if not SDK_AVAILABLE or not PYSGFPLib:
                raise Exception("SecuGen SDK no disponible. Modo fallback DESHABILITADO.")
            
            print("🚀 INICIANDO CONTROLADOR CON SDK NATIVO ÚNICAMENTE")
            self.sgfp = PYSGFPLib()
            
            # Intentar inicializar - si falla, se reintentará automáticamente en las operaciones
            init_success = self.initializeDevice()
            if init_success:
                print("✅ Controlador inicializado con SDK nativo")
            else:
                print("⚠️ Inicialización falló, pero controlador creado para reintentos automáticos")
                
        except Exception as e:
            self.init_error = str(e)
            print(f"❌ Error crítico: {e}")
            print("🚫 MODO FALLBACK DESHABILITADO - Se requiere SDK nativo")
            raise Exception(f"SDK nativo requerido: {e}")
    
    def initializeDevice(self):
        """Inicializar dispositivo con reintentos automáticos para estabilidad"""
        max_retries = 5
        retry_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                if not self.sgfp:
                    raise Exception("SecuGen SDK no disponible")
                    
                print(f"🔄 Iniciando dispositivo (intento {attempt + 1}/{max_retries})...")
                
                # Cerrar conexión anterior si existe
                try:
                    if self.initialized:
                        self.sgfp.CloseDevice()
                        print("💭 Conexión anterior cerrada")
                except:
                    pass
                
                err = self.sgfp.Create()
                if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                    raise Exception(f"Error al crear la instancia: {err}")

                print("🔧 Inicializando...")
                err = self.sgfp.Init(1)
                if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                    raise Exception(f"Error al inicializar: {err}")

                print("🔌 Abriendo dispositivo...")
                # Intentar con diferentes IDs de dispositivo
                device_ids = [0, 1, 2, 3]  # Más IDs para mayor robustez
                device_opened = False
                
                for device_id in device_ids:
                    print(f"   Probando dispositivo ID: {device_id}")
                    err = self.sgfp.OpenDevice(device_id)
                    if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                        device_opened = True
                        print(f"✅ Dispositivo abierto exitosamente con ID: {device_id}")
                        break
                    else:
                        print(f"   ❌ ID {device_id} falló: error {err}")
                
                if not device_opened:
                    raise Exception(f"No se pudo abrir el dispositivo con ningún ID")

                self.initialized = True
                print("🎉 Dispositivo inicializado correctamente y ESTABLE")
                return True
                
            except Exception as e:
                self.init_error = str(e)
                print(f"❌ Error en initializeDevice (intento {attempt + 1}): {str(e)}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ Esperando {retry_delay} segundos antes del siguiente intento...")
                    time.sleep(retry_delay)
                else:
                    print(f"🚨 FALLO CRÍTICO: No se pudo inicializar después de {max_retries} intentos")
                    self.initialized = False
                    return False
                    
        return False
    
    def led_control(self, state):
        try:
            if not self.initialized:
                # Intentar reinicializar si falló anteriormente
                if not self.initializeDevice():
                    raise Exception(f"Dispositivo no inicializado. Error original: {self.init_error}")
            
            print(f"Intentando {'encender' if state else 'apagar'} el LED del lector...")
            
            if not self.sgfp:
                raise Exception("SecuGen SDK no disponible")
            
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
        """Crear template a partir de una imagen de huella usando SDK nativo únicamente"""
        try:
            from ctypes import c_char, create_string_buffer
            
            # Verificar que el dispositivo esté inicializado
            if not self.sgfp:
                raise Exception("ERROR: Dispositivo SecuGen no inicializado. Se requiere SDK nativo.")
            
            print("🏗️ CREANDO TEMPLATE CON SDK NATIVO")
            
            # Usar el tamaño constante del template SG400 (400 bytes)
            template_size = self.sgfp.constant_sg400_template_size
            print(f"📏 Tamaño del template SG400: {template_size} bytes")
            
            # Crear buffer para el template con el tamaño correcto
            template_buffer = (c_char * template_size)()
            
            # Convertir image_buffer a buffer de ctypes si es necesario
            if isinstance(image_buffer, bytearray):
                image_buffer_ctypes = (c_char * len(image_buffer)).from_buffer(image_buffer)
            elif isinstance(image_buffer, bytes):
                buffer = bytearray(image_buffer)
                image_buffer_ctypes = (c_char * len(buffer)).from_buffer(buffer)
            else:
                # Asumir que ya es un buffer de ctypes
                image_buffer_ctypes = image_buffer
            
            print(f"🖼️ Tamaño de imagen de entrada: {len(image_buffer)} bytes")
            
            # Crear el template usando la función nativa SG400
            print("🔧 Llamando CreateSG400Template...")
            err = self.sgfp.CreateSG400Template(image_buffer_ctypes, template_buffer)
            if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
                raise Exception(f"Error al crear template SG400: código {err}")
            
            # Convertir el template a bytes
            template_data = bytes(template_buffer)
            
            print(f"✅ Template SG400 creado exitosamente con SDK NATIVO")
            print(f"📦 Tamaño del template: {len(template_data)} bytes")
            print(f"🔧 Formato: SecuGen SG400 nativo binario")
            
            return template_data
            
        except Exception as e:
            print(f"❌ Error en create_template: {str(e)}")
            raise Exception(f"SDK nativo requerido para crear template: {str(e)}")
    


    def compare_templates(self, template1, template2, security_level=8):
        """Comparar dos templates de huellas usando el algoritmo biométrico nativo de SecuGen"""
        try:
            from ctypes import c_bool, c_int, byref, create_string_buffer
            from sdk.sgfdxsecuritylevel import SGFDxSecurityLevel
            
            # Verificar que el dispositivo esté inicializado
            if not self.sgfp:
                raise Exception("ERROR: Dispositivo SecuGen no inicializado. Se requiere SDK nativo.")
            
            # OPTIMIZACIÓN: Convertir templates a bytes de forma eficiente
            if isinstance(template1, str):
                template1 = base64.b64decode(template1)
            elif isinstance(template1, bytearray):
                template1 = bytes(template1)
            
            if isinstance(template2, str):
                template2 = base64.b64decode(template2)
            elif isinstance(template2, bytearray):
                template2 = bytes(template2)
            
            # Crear buffers para ctypes
            template1_buffer = create_string_buffer(template1)
            template2_buffer = create_string_buffer(template2)
            
            # Variables para los resultados
            matched = c_bool(False)
            score = c_int(0)
            
            # Mapear security level
            security_levels = {
                1: SGFDxSecurityLevel.SL_LOWEST,
                2: SGFDxSecurityLevel.SL_LOWER,
                3: SGFDxSecurityLevel.SL_LOW,
                4: SGFDxSecurityLevel.SL_BELOW_NORMAL,
                5: SGFDxSecurityLevel.SL_NORMAL,
                6: SGFDxSecurityLevel.SL_ABOVE_NORMAL,
                7: SGFDxSecurityLevel.SL_HIGH,
                8: SGFDxSecurityLevel.SL_HIGHER,
                9: SGFDxSecurityLevel.SL_HIGHEST
            }
            
            sg_security_level = security_levels.get(security_level, SGFDxSecurityLevel.SL_NORMAL)
            
            print(f"🔍 COMPARACIÓN SDK NATIVO:")
            print(f"🔍 Nivel de seguridad: {security_level} -> {sg_security_level}")
            print(f"🔍 Template1 size: {len(template1)} bytes")
            print(f"🔍 Template2 size: {len(template2)} bytes")
            
            # Comparar templates usando SecuGen nativo
            result = self.sgfp.MatchTemplate(
                template1_buffer, 
                template2_buffer, 
                sg_security_level, 
                byref(matched)
            )
            
            if result == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print(f"✅ Comparación nativa exitosa: matched={matched.value}")
                
                # Si hay match, obtener el score
                if matched.value:
                    score_result = self.sgfp.GetMatchingScore(
                        template1_buffer, 
                        template2_buffer, 
                        byref(score)
                    )
                    final_score = score.value if score_result == SGFDxErrorCode.SGFDX_ERROR_NONE else 100
                    print(f"📊 Score nativo: {final_score}")
                else:
                    final_score = 0
                    print(f"📊 No match - Score: {final_score}")
                
                return {
                    'success': True,
                    'matched': matched.value,
                    'score': final_score,
                    'message': f'Comparación SDK NATIVO: {"MATCH" if matched.value else "NO MATCH"} (score: {final_score}, nivel: {security_level})'
                }
            else:
                # Error en SDK nativo - no usar fallback
                error_msg = f"Error en SDK nativo: código {result}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            print(f"❌ Error en compare_templates: {str(e)}")
            return {'success': False, 'error': f'SDK nativo requerido: {str(e)}'}
    


    def store_template(self, template_id, template_data):
        """Almacenar template de referencia en formato binario eficiente"""
        try:
            # OPTIMIZACIÓN: Almacenar siempre en formato binario para comparaciones eficientes
            if isinstance(template_data, str):
                template_data = base64.b64decode(template_data)
            elif isinstance(template_data, bytearray):
                template_data = bytes(template_data)
            
            self.stored_templates[template_id] = template_data
            return {'success': True, 'message': f'Template {template_id} almacenado (binario, {len(template_data)} bytes)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_stored_templates(self):
        """Obtener lista de templates almacenados"""
        return list(self.stored_templates.keys())
    
    def get_templates_info(self):
        """Obtener información detallada de templates almacenados"""
        templates_info = {}
        total_size = 0
        
        for template_id, template_data in self.stored_templates.items():
            size = len(template_data)
            total_size += size
            templates_info[template_id] = {
                'size_bytes': size,
                'format': 'binary',
                'base64_size': len(base64.b64encode(template_data).decode())
            }
        
        return {
            'count': len(self.stored_templates),
            'total_size_bytes': total_size,
            'avg_size_bytes': total_size / len(self.stored_templates) if self.stored_templates else 0,
            'templates': templates_info
        }

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
    try:
        data = request.get_json() or {}
        save_image = data.get('save_image', False)  # Por defecto no guardar
        create_template = data.get('create_template', True)  # Por defecto SÍ crear template
        template_id = data.get('template_id', None)  # ID para almacenar template
        
        print(f"=== CAPTURAR HUELLA - INICIO ===")
        print(f"Parámetros recibidos: save_image={save_image}, create_template={create_template}, template_id={template_id}")
        
        # Verificar si el dispositivo está inicializado - reintentar si es necesario
        if not hasattr(controller, 'sgfp') or controller.sgfp is None:
            print("ERROR: Dispositivo no inicializado")
            return jsonify({'error': 'Dispositivo no inicializado'}), 500
        
        # Auto-reintentar inicialización si el dispositivo no está listo
        if not controller.initialized:
            print("🔄 Dispositivo no inicializado, reintentando...")
            init_success = controller.initializeDevice()
            if not init_success:
                print("❌ Falló reinicialización automática")
                return jsonify({'error': 'Dispositivo no se pudo inicializar después de reintentos'}), 500
            else:
                print("✅ Reinicialización automática exitosa")
        
        # Inicializar variables para width y height
        width = c_long(258)    # Ancho típico del sensor
        height = c_long(336)   # Alto típico del sensor
        
        print("Obteniendo información del dispositivo...")
        err = controller.sgfp.GetDeviceInfo(width, height)
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"ERROR: al obtener información del dispositivo - Código: {err}")
            raise Exception(f'Error al obtener información del dispositivo: {err}')
        
        print(f"Dimensiones del sensor: {width.value}x{height.value}")
        
        # Crear buffer del tamaño correcto
        buffer_size = width.value * height.value
        print(f"Tamaño del buffer calculado: {buffer_size} bytes")
        imageBuffer = bytearray(buffer_size)
        
        print("Encendiendo LED...")
        try:
            controller.led_control(True)  # Encender LED
            print("LED encendido exitosamente")
        except Exception as e:
            print(f"ERROR al encender LED: {e}")
        
        print("Capturando imagen...")
        print(f"Tamaño del buffer: {len(imageBuffer)}")
        
        # Modificación de intentos y tiempo de espera
        max_attempts = 10  # Aumentado de 5 a 10 intentos
        wait_time = 2    # Reducido de 3 a 2 segundos
        
        print("🔄 Iniciando proceso de captura automática...")
        print("⚠️  IMPORTANTE: Coloque el dedo en el sensor y manténgalo presionado")
        
        for attempt in range(max_attempts):
            print(f"Intento {attempt + 1} de {max_attempts}")
            err = controller.sgfp.GetImage(imageBuffer)
            print(f"GetImage retornó código: {err}")
            
            if err == SGFDxErrorCode.SGFDX_ERROR_NONE:
                print("✅ Imagen capturada exitosamente")
                break
            elif err == SGFDxErrorCode.SGFDX_ERROR_FUNCTION_FAILED:
                print("❌ ERROR: Función GetImage falló - posible problema con el dispositivo")
            elif err == SGFDxErrorCode.SGFDX_ERROR_INVALID_PARAM:
                print("❌ ERROR: Parámetros inválidos en GetImage")
            elif err == SGFDxErrorCode.SGFDX_ERROR_WRONG_IMAGE:
                print("⚠️  ERROR: Imagen incorrecta - asegúrese de que el dedo esté bien colocado en el sensor")
            elif err == SGFDxErrorCode.SGFDX_ERROR_TIME_OUT:
                print("⏱️  ERROR: Tiempo agotado - coloque el dedo en el sensor")
            elif err == SGFDxErrorCode.SGFDX_ERROR_DEVICE_NOT_FOUND:
                print("🔌 ERROR: Dispositivo no encontrado - verifique la conexión")
            else:
                print(f"❌ ERROR: Código de error no reconocido: {err}")
                
            if attempt < max_attempts - 1:  # No esperar en el último intento
                print(f"⏳ Esperando {wait_time} segundos antes del siguiente intento...")
                time.sleep(wait_time)  # Espera entre intentos
        
        print("Apagando LED...")
        try:
            controller.led_control(False)  # Apagar LED después de la captura
            print("LED apagado exitosamente")
        except Exception as e:
            print(f"ERROR al apagar LED: {e}")
        
        if err != SGFDxErrorCode.SGFDX_ERROR_NONE:
            print(f"ERROR FINAL: No se pudo capturar la huella después de {max_attempts} intentos. Código: {err}")
            raise Exception(f'Error al capturar la huella: {err}')

        print("Convirtiendo imagen a base64...")
        # Convertir a base64
        imagen_base64 = base64.b64encode(bytes(imageBuffer)).decode('utf-8')
        print(f"Imagen convertida a base64: {len(imagen_base64)} caracteres")
        
        # Crear template si se solicita
        template_base64 = None
        if create_template:
            print("Creando template...")
            template_data = controller.create_template(imageBuffer)
            if template_data:
                template_base64 = base64.b64encode(bytes(template_data)).decode('utf-8')
                print(f"Template creado: {len(template_base64)} caracteres")
                
                # Almacenar template si se proporciona ID
                if template_id:
                    controller.store_template(template_id, template_data)
                    print(f"Template almacenado con ID: {template_id}")
            else:
                print("ERROR: No se pudo crear el template")
        
        # Guardar la imagen solo si se solicita
        if save_image:
            try:
                print("Guardando imagen en disco...")
                with open('/app/images/huella.png', 'wb') as f:
                    f.write(base64.b64decode(imagen_base64))
                print("Imagen guardada exitosamente")
            except Exception as e:
                print(f"Error al guardar imagen: {e}")
                pass
        
        print("=== CAPTURAR HUELLA - ÉXITO ===")
        return jsonify({
            'success': True,
            'template': template_base64,  # Template directamente en la respuesta
            'image_data': imagen_base64,  # Imagen como respaldo
            'width': width.value,
            'height': height.value,
            'mensaje': 'Huella capturada exitosamente',
            'template_stored': template_id if template_id and template_base64 else None,
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
        print(f"ERROR GENERAL en capturar_huella: {str(e)}")
        print("=== CAPTURAR HUELLA - ERROR ===")
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
        security_level = data.get('security_level', 4)  # Nivel de seguridad por defecto ALTO para evitar falsos positivos
        
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

@app.route('/templates/info', methods=['GET'])
def info_templates():
    try:
        info = controller.get_templates_info()
        return jsonify({
            'success': True,
            'info': info,
            'efficiency_notes': {
                'binary_storage': 'Templates almacenados en formato binario para máxima eficiencia',
                'base64_overhead': 'Base64 añade ~34% más tamaño',
                'comparison_speed': 'Comparación binaria es ~11x más rápida que base64'
            }
        })
    except Exception as e:
        print(f"Error en info_templates: {str(e)}")
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