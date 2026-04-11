# Configuración del Canal de Voz para el Bot

## Pasos para configurar el bot en un canal de voz:

### 1. Obtener el ID del canal de voz
1. Ve a tu servidor de Discord
2. Haz clic derecho en el canal de voz donde quieres que esté el bot
3. Activa "Modo Desarrollador" en Configuración de Discord > Avanzado
4. Vuelve a hacer clic derecho en el canal y selecciona "Copiar ID"

### 2. Configurar el ID en el código
Edita el archivo `main.py` y busca la línea que define `VOICE_CHANNEL_ID`:
```python
VOICE_CHANNEL_ID = None  # O el ID anterior
```

Reemplaza el valor actual con el ID que copiaste, por ejemplo:
```python
VOICE_CHANNEL_ID = 1453589053432926440
```

### 3. Permisos necesarios
Asegúrate de que el bot tenga estos permisos en el canal de voz:
- **Conectar** (Connect)
- **Hablar** (Speak)
- **Usar Actividad de Voz** (Use Voice Activity)

### 4. Características implementadas
- **Conexión automática**: El bot se conectará al canal al iniciar
- **Reconexión automática**: Si el bot es desconectado, intentará reconectarse
- **Sistema robusto**: Manejo de errores con reintento exponencial
- **Logging detallado**: Registro de todos los eventos de conexión

### 5. Ejecución del bot
Ejecuta el bot con:
```bash
python main.py
```

El bot ahora se mantendrá conectado todo el día en el canal de voz configurado.

## Solución de problemas

### Si el bot no se conecta:
1. Verifica que el ID del canal sea correcto
2. Asegúrate de que el bot tenga los permisos necesarios
3. Revisa los logs para ver mensajes de error

### Si el bot se desconecta frecuentemente:
1. Verifica la estabilidad de tu conexión a internet
2. Asegúrate de que el bot no sea expulsado manualmente
3. Revisa los logs para identificar patrones

## Notas importantes
- El bot solo puede estar en un canal de voz a la vez
- Si hay múltiples servidores, el bot buscará el canal en todos ellos
- El sistema de reconexión tiene un límite de 10 intentos consecutivos
