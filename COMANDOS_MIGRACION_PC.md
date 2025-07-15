# 🖥️ COMANDOS MIGRACIÓN A OTRO PC - CHEAT SHEET

## 🎯 **COMANDOS ESENCIALES (COPIA Y PEGA)**

### **🚀 CONFIGURACIÓN INICIAL (Solo primera vez en nuevo PC)**

```bash
# 1. Descargar/copiar proyecto
git clone <tu-repositorio>
cd driver-bloqueo-digital-huella-main

# 2. Configurar automáticamente TODO (UN SOLO COMANDO)
./configurar_nuevo_pc.sh

# 3. Reiniciar sistema cuando termine
sudo reboot
```

### **💻 USO DIARIO (Después del reinicio)**

```bash
# INICIAR SISTEMA (COMANDO PRINCIPAL)
./iniciar_sistema_robusto.sh

# PARAR SISTEMA (AL TERMINAR)
./parar_sistema.sh
```

### **🚨 COMANDOS DE EMERGENCIA**

```bash
# Si algo falla, ejecutar en orden:
./parar_sistema.sh
sudo python3 reset_usb_device.py
./iniciar_sistema_robusto.sh
```

### **🔍 VERIFICACIONES**

```bash
# Verificar que todo funciona
python3 test_sistema_robusto.py

# Probar API
curl -X POST http://localhost:5000/initialize
```

---

## 📋 **CHECKLIST MIGRACIÓN**

### **✅ ANTES DE MIGRAR**
- [ ] Dispositivo SecuGen conectado
- [ ] Sistema Ubuntu/Debian
- [ ] Acceso sudo disponible
- [ ] Todos los archivos del proyecto copiados

### **✅ DESPUÉS DE CONFIGURAR**
- [ ] `lsusb | grep "1162:2201"` → Debe mostrar dispositivo
- [ ] `ls -la /dev/secugen_device` → Debe mostrar symlink
- [ ] `groups` → Debe incluir 'dialout' y 'plugdev'
- [ ] `./iniciar_sistema_robusto.sh` → Debe iniciar sin errores

### **✅ PARA USO DIARIO**
- [ ] NUNCA usar `python3 app.py` directamente
- [ ] SIEMPRE usar `./iniciar_sistema_robusto.sh`
- [ ] SIEMPRE usar `./parar_sistema.sh` para parar
- [ ] Activar monitor cuando se ofrezca (responder 'y')

---

## 📁 **ARCHIVOS CRÍTICOS PARA MIGRAR**

### **🔴 CRÍTICOS (No puede faltar ninguno)**
- `iniciar_sistema_robusto.sh` → Inicio robusto
- `parar_sistema.sh` → Parada segura
- `configurar_nuevo_pc.sh` → Configuración automática
- `reset_usb_device.py` → Reset USB mejorado
- `docker/99SecuGen.rules` → Reglas udev
- `app.py` → Aplicación principal
- `sdk/` → SDK de SecuGen
- `lib/` → Librerías compartidas

### **🟡 IMPORTANTES (Recomendados)**
- `monitor_sistema_completo.py` → Monitoreo automático
- `test_sistema_robusto.py` → Pruebas del sistema
- `app_backup.py` → Backup para restauración
- `README_SISTEMA_ROBUSTO.md` → Documentación
- `RESUMEN_MEJORAS.md` → Resumen de mejoras

---

## ⚡ **COMANDOS RÁPIDOS**

### **Configurar nuevo PC**
```bash
./configurar_nuevo_pc.sh && sudo reboot
```

### **Iniciar sistema**
```bash
./iniciar_sistema_robusto.sh
```

### **Parar sistema**
```bash
./parar_sistema.sh
```

### **Reset de emergencia**
```bash
./parar_sistema.sh && sudo python3 reset_usb_device.py && ./iniciar_sistema_robusto.sh
```

### **Verificar estado**
```bash
python3 test_sistema_robusto.py
```

### **Ver logs**
```bash
tail -f logs/sistema_robusto.log
```

---

## 🔧 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **Error: "Dispositivo no encontrado"**
```bash
lsusb | grep "1162:2201"
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### **Error: "Puerto ocupado"**
```bash
./parar_sistema.sh
lsof -t -i:5000 | xargs kill -9
./iniciar_sistema_robusto.sh
```

### **Error: "Sintaxis incorrecta"**
```bash
cp app_backup.py app.py
./iniciar_sistema_robusto.sh
```

### **Error: "Permisos negados"**
```bash
groups  # Debe incluir dialout y plugdev
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
sudo reboot
```

---

## 🎯 **FLUJO COMPLETO**

### **Primera vez en nuevo PC:**
```bash
git clone <repositorio>
cd driver-bloqueo-digital-huella-main
./configurar_nuevo_pc.sh
sudo reboot
```

### **Después del reinicio:**
```bash
./iniciar_sistema_robusto.sh
# Responder 'y' para activar monitor
```

### **Para trabajar:**
```bash
# Sistema ya está corriendo
curl -X POST http://localhost:5000/initialize
```

### **Al terminar:**
```bash
./parar_sistema.sh
```

---

## 📞 **CONTACTO DE EMERGENCIA**

Si nada funciona:
1. Revisar logs: `tail -f logs/sistema_robusto.log`
2. Verificar dispositivo: `lsusb | grep "1162:2201"`
3. Verificar permisos: `groups`
4. Reconfigurar: `./configurar_nuevo_pc.sh`
5. Reiniciar sistema: `sudo reboot`

---

**🎉 ¡Con estos comandos, el lector NUNCA fallará en cualquier PC!** 