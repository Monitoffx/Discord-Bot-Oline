import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import time
import logging
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True  # <-- AGREGAR ESTA LÍNEA

# Configurar el bot
bot = commands.Bot(command_prefix='!', intents=intents)


# ID del canal de bienvenida
WELCOME_CHANNEL_ID = 1444535044277534931

# ID del canal de despedida
GOODBYE_CHANNEL_ID = 1444541465580540097  # Canal de despedida actualizado

# ID del rol automático (autorole)
AUTOROLE_ID = 1428535811850240082  # Cambia esto por el ID del rol que quieres asignar

# ID del canal de voz donde el bot estará conectado
VOICE_CHANNEL_ID = 1453589053432926440  # Canal de voz configurado por el usuario

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Para evitar mensajes duplicados
last_welcome = {}

# Variable global para mantener la conexión de voz
voice_client = None

# Variables para controlar reconexiones de voz
voice_reconnect_attempts = 0
max_voice_reconnect_attempts = 5
last_voice_reconnect_time = 0
last_successful_connection = 0
is_reconnecting = False

@bot.event
async def on_member_join(member):
    """Envía un mensaje de bienvenida cuando un nuevo miembro se une al servidor."""
    try:
        # Siempre procesar nuevos miembros (sin cooldown para re-entradas)
        current_time = discord.utils.utcnow()
        last_welcome[member.id] = current_time

        welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)

        if welcome_channel is None:
            logger.error(f"No se pudo encontrar el canal de bienvenida con ID: {WELCOME_CHANNEL_ID}")
            return

        if not welcome_channel.permissions_for(welcome_channel.guild.me).send_messages:
            logger.warning("No tengo permisos para enviar mensajes en el canal de bienvenida")
            return

        member_count = member.guild.member_count

        # Crear el mensaje de bienvenida
        embed = discord.Embed(
            title=f"**🎉 𝗕𝗜𝗘𝗡𝗩𝗜𝗗𝗢 𝗔 𝗩𝗬𝗣𝗘𝗥 𝗠𝗢𝗗𝗦  🎉**",
            description=f"**Hola {member.mention} eres el miembro #{member_count}!**\n\n"

            f"**👑 Para conocer más sobre nuestros productos, revisa nuestros canales:**\n\n"

              f"**📌 VyperMods Store**\n\n"
              f"•  <#1459711154023825579>\n" 
              f"•  <#1459711257262161951>\n"
              f"•  <#1443695755394027520>\n\n"
              f"•  <#1441593476415226059>\n"
              f"•  <#1441593489329750237>\n"
              f"•  <#1443697381362241768>\n\n"
              f"**📌 Reglas importantes**\n\n"
              f"•  Por favor lee las <#1444538512971010229>\n"
              f"• Diviértete y comparte\n\n"
              f"**💡 ¿Necesitas ayuda?**\n\n"
              f"• Pregunta a los moderadores\n"
              f"• Usa los comandos de ayuda",
            color=0x00ff00
        )

        # Añadir imagen grande (GIF)
        embed.set_image(url="https://github.com/Samuel-bit-bot/URLS/releases/download/v1/Logo-VyperMods.png")

        # Añadir thumbnail con logo estático
        embed.set_thumbnail(url="https://github.com/Samuel-bit-bot/URLS/releases/download/v1/banner.gif")

        # Añadir pie de página con ícono estático
        embed.set_footer(
            text="Created by MonitoSamuel",
            icon_url="https://github.com/Samuel-bit-bot/URLS/releases/download/v1/Logo-VyperMods.png"
        )

        # Eliminar mensajes anteriores de bienvenida para este usuario
        async for message in welcome_channel.history(limit=10):
            if message.author == bot.user and message.embeds and member.mention in message.embeds[0].description:
                try:
                    await message.delete()
                except:
                    pass

        # Enviar mensaje de bienvenida
        mensaje = await welcome_channel.send(embed=embed)

        # Añadir reacciones
        try:
            await mensaje.add_reaction('👋')
        except Exception as e:
            logger.warning(f"Error al agregar reacciones: {e}")

        logger.info(f"Mensaje de bienvenida enviado a {member.name}")

        # Asignar rol automático (autorole)
        if AUTOROLE_ID is not None:
            try:
                logger.info(f"Intentando asignar rol con ID: {AUTOROLE_ID}")
                role = member.guild.get_role(AUTOROLE_ID)
                if role is None:
                    logger.error(f"No se pudo encontrar el rol con ID: {AUTOROLE_ID}")
                    logger.info(f"Roles disponibles: {[r.name + ' (ID: ' + str(r.id) + ')' for r in member.guild.roles]}")
                else:
                    logger.info(f"Rol encontrado: '{role.name}' (ID: {role.id})")
                    logger.info(f"Bot tiene permisos: {member.guild.me.guild_permissions.manage_roles}")
                    logger.info(f"Posición del bot: {member.guild.me.top_role.position}")
                    logger.info(f"Posición del rol: {role.position}")
                    logger.info(f"Roles actuales del miembro: {[r.name for r in member.roles]}")

                    # Verificar si ya tiene el rol
                    if role in member.roles:
                        logger.info(f"El miembro ya tiene el rol '{role.name}', pero se verificará nuevamente")

                    await member.add_roles(role, reason="Autorole automático")
                    logger.info(f"Rol '{role.name}' asignado exitosamente a {member.name}")
            except discord.Forbidden as e:
                logger.error(f"Error de permisos al asignar rol: {e}")
                logger.error(f"Bot tiene permiso manage_roles: {member.guild.me.guild_permissions.manage_roles}")
            except discord.HTTPException as e:
                logger.error(f"Error HTTP al asignar rol: {e}")
            except Exception as e:
                logger.error(f"Error inesperado al asignar rol: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        logger.error(f"Error al enviar mensaje de bienvenida: {e}")

        # Asegúrate de que 'bot' sea el nombre de tu instancia de comandos (commands.Bot o discord.Client)
@bot.event
async def on_member_remove(member):
    """Envía un mensaje de despedida cuando un miembro sale del servidor."""
    
    # Ignorar si el usuario es un bot para evitar logs innecesarios
    if member.bot:
        return
        
    try:
        # Usamos member.guild.get_channel() o bot.get_channel() si tienes el ID.
        # Usar bot.get_channel() es mejor si el ID está definido globalmente.
        goodbye_channel = bot.get_channel(GOODBYE_CHANNEL_ID)
        
        if goodbye_channel is None:
            # Puedes usar member.guild.name si no se encuentra el canal, para saber de qué servidor viene el error
            logger.error(f"No se pudo encontrar el canal de despedida con ID: {GOODBYE_CHANNEL_ID} en el servidor {member.guild.name}.")
            return
            
        # Verificar permisos
        if not goodbye_channel.permissions_for(goodbye_channel.guild.me).send_messages:
            logger.warning(f"No tengo permisos para enviar mensajes en el canal de despedida: {goodbye_channel.name}")
            return
        
        # Crear mensaje de despedida (Completando tu código)
        embed = discord.Embed(
            title=f"**👋 𝗔𝗗𝗜𝗢𝗦 𝗗𝗘 𝗩𝗬𝗣𝗘𝗥 𝗠𝗢𝗗𝗦 👋**",
            description=f"**{member.mention}** Ojala no vuelvas",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="Información",
            value=f"Se fue un gay: `{member.name}#{member.discriminator}`",
            inline=False
        )
        
        embed.add_field(
            name="Miembros Restantes",
            value=f"El servidor ahora tiene **{member.guild.member_count}** miembros.",
            inline=True
        )

        # Añadir imagen grande (GIF)
        embed.set_image(url="https://github.com/Samuel-bit-bot/URLS/releases/download/v1/Logo-VyperMods.png")

        # Añadir thumbnail con logo estático
        embed.set_thumbnail(url="https://github.com/Samuel-bit-bot/URLS/releases/download/v1/banner.gif")

        # Añadir pie de página con ícono estático
        embed.set_footer(
            text="Created by MonitoSamuel",
            icon_url="https://github.com/Samuel-bit-bot/URLS/releases/download/v1/Logo-VyperMods.png"
        )
        
        await goodbye_channel.send(embed=embed)

    except Exception as e:
        logger.error(f"Error general al procesar on_member_remove para {member.display_name}: {e}")

@bot.event
async def on_ready():
    logger.info(f'Bot conectado como {bot.user.name}')
    logger.info(f'Bot está en {len(bot.guilds)} servidores')
    
    # Cargar extensiones
    EXTENSIONS = ['rpc_status']
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            logger.info(f"Extensión cargada: {extension}")
        except Exception as e:
            logger.error(f"Error al cargar {extension}: {e}")
    
    # Conectar al canal de voz si está configurado
    await connect_to_voice_channel()

async def connect_to_voice_channel():
    """Conecta el bot a un canal de voz específico con sistema conservador de reconexión."""
    global voice_client, voice_reconnect_attempts, last_voice_reconnect_time, last_successful_connection, is_reconnecting
    
    if VOICE_CHANNEL_ID is None:
        logger.info("No se ha configurado un canal de voz. El bot no se conectará a voz.")
        return
    
    # Prevenir reconexiones simultáneas
    if is_reconnecting:
        logger.info("Reconexión ya en progreso, esperando...")
        return
    
    current_time = time.time()
    
    # Verificar si ya está conectado correctamente
    if voice_client and voice_client.is_connected() and voice_client.channel.id == VOICE_CHANNEL_ID:
        if current_time - last_successful_connection < 30:  # Si está conectado y estable por 30 segundos
            logger.info("Bot ya conectado y estable en el canal de voz")
            voice_reconnect_attempts = 0
            is_reconnecting = False
            return
    
    # Controlar frecuencia de reconexiones (mínimo 5 minutos entre intentos)
    if current_time - last_voice_reconnect_time < 300:
        logger.warning(f"Esperando antes de intentar reconectar a voz... ({300 - (current_time - last_voice_reconnect_time):.0f}s restantes)")
        return
    
    # Verificar límite de intentos
    if voice_reconnect_attempts >= max_voice_reconnect_attempts:
        logger.error(f"Límite de intentos de reconexión de voz alcanzado ({max_voice_reconnect_attempts}). Esperando 1 hora...")
        voice_reconnect_attempts = 0  # Resetear después de una hora
        return
    
    is_reconnecting = True
    
    try:
        # Buscar el canal de voz en todos los servidores del bot
        voice_channel = None
        for guild in bot.guilds:
            channel = guild.get_channel(VOICE_CHANNEL_ID)
            if channel and hasattr(channel, 'voice_states'):  # Es un canal de voz
                voice_channel = channel
                break
        
        if voice_channel is None:
            logger.error(f"No se encontró el canal de voz con ID: {VOICE_CHANNEL_ID}")
            is_reconnecting = False
            return
        
        # Si está conectado a otro canal, desconectar primero
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            voice_client = None
            await asyncio.sleep(2)
        
        # Incrementar contador y registrar tiempo
        voice_reconnect_attempts += 1
        last_voice_reconnect_time = current_time
        
        # Calcular delay con backoff exponencial más agresivo
        delay = min(10 * voice_reconnect_attempts, 120)  # 10, 20, 40, 80, 120 segundos
        if voice_reconnect_attempts > 1:
            logger.info(f"Esperando {delay} segundos antes de conectar (intento #{voice_reconnect_attempts}/{max_voice_reconnect_attempts})")
            await asyncio.sleep(delay)
        
        # Conectar al canal de voz
        voice_client = await voice_channel.connect()
        logger.info(f"Conectado exitosamente al canal de voz: {voice_channel.name}")
        
        # Resetear contadores y marcar como éxito
        voice_reconnect_attempts = 0
        last_successful_connection = current_time
        is_reconnecting = False
        
        # Esperar un momento para asegurar conexión estable
        await asyncio.sleep(5)
        
    except discord.errors.ConnectionClosed as e:
        if e.code == 4017:
            logger.error(f"Error 4017 de Discord - Servidores de voz sobrecargados (intento #{voice_reconnect_attempts})")
            # Para error 4017, esperar mucho más tiempo
            await asyncio.sleep(min(60, 10 * voice_reconnect_attempts))
        else:
            logger.error(f"Conexión de voz cerrada: {e}")
            await asyncio.sleep(10)
    except discord.Forbidden:
        logger.error("No tengo permisos para conectarme al canal de voz")
        voice_reconnect_attempts = max_voice_reconnect_attempts  # No reintentar
    except discord.ClientException as e:
        if "Already connected to a voice channel" in str(e):
            logger.warning("Ya conectado a un canal, forzando desconexión...")
            if voice_client:
                await voice_client.disconnect(force=True)
                voice_client = None
                await asyncio.sleep(5)
        else:
            logger.error(f"Error de cliente al conectarse a voz: {e}")
            await asyncio.sleep(10)
    except Exception as e:
        logger.error(f"Error inesperado al conectar al canal de voz: {e}")
        await asyncio.sleep(15)
    finally:
        is_reconnecting = False

async def check_voice_connection():
    """Verifica y reconecta el bot al canal de voz si es necesario."""
    global voice_client
    
    if VOICE_CHANNEL_ID is None:
        return
    
    try:
        # Si no está conectado o la conexión se perdió
        if not voice_client or not voice_client.is_connected():
            logger.warning("Conexión de voz perdida, intentando reconectar...")
            await connect_to_voice_channel()
    except Exception as e:
        logger.error(f"Error al verificar conexión de voz: {e}")

# NOTA: Esta función está deshabilitada para evitar bucles de reconexión
# Para habilitarla, descomenta la siguiente línea y agrégala a un task loop
# async def voice_monitor_task():
#     while True:
#         await check_voice_connection()
#         await asyncio.sleep(30)  # Verificar cada 30 segundos

@bot.event
async def on_voice_state_update(member, before, after):
    """Maneja cambios en el estado de voz de los miembros."""
    global voice_client, voice_reconnect_attempts, last_successful_connection
    
    # Si el bot fue desconectado por un administrador
    if member == bot.user and after.channel is None and before.channel is not None:
        logger.warning("El bot fue desconectado del canal de voz")
        voice_client = None
        voice_reconnect_attempts = 0  # Resetear contador para permitir reconexión
        last_successful_connection = 0  # Resetear tiempo de conexión exitosa
        
        # Esperar más tiempo antes de reconectar (más conservador)
        logger.info("Esperando 30 segundos antes de intentar reconectar...")
        await asyncio.sleep(30)
        
        # Intentar reconectar solo si no hay reconexiones en curso
        if voice_client is None:
            await connect_to_voice_channel()

# Iniciar el bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        logger.error("Error: No se encontró el token de Discord en las variables de entorno")
        exit(1)
    
    # Sistema de reconexión robusto
    reconnect_attempts = 0
    max_reconnect_attempts = 10
    base_delay = 5  # segundos
    
    while True:
        try:
            if reconnect_attempts > 0:
                delay = min(base_delay * (2 ** reconnect_attempts), 300)  # Máximo 5 minutos
                logger.info(f"Reiniciando bot en {delay} segundos (intento #{reconnect_attempts})...")
                time.sleep(delay)
            
            logger.info("Iniciando bot...")
            reconnect_attempts = 0  # Resetear contador cuando el inicio es exitoso
            
            # Crear un nuevo bucle de eventos para evitar problemas
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(bot.start(TOKEN))
            except KeyboardInterrupt:
                logger.info("Bot detenido por el usuario")
                break
            except discord.errors.ConnectionClosed as e:
                logger.error(f"Conexión cerrada: {e}")
                reconnect_attempts += 1
                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error("Máximo número de intentos de reconexión alcanzado")
                    break
                continue
            except discord.errors.HTTPException as e:
                logger.error(f"Error HTTP: {e}")
                reconnect_attempts += 1
                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error("Máximo número de intentos de reconexión alcanzado")
                    break
                continue
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
                reconnect_attempts += 1
                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error("Máximo número de intentos de reconexión alcanzado")
                    break
                continue
            finally:
                loop.close()
                
        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario")
            break
        except Exception as e:
            logger.error(f"Error crítico: {e}")
            reconnect_attempts += 1
            if reconnect_attempts >= max_reconnect_attempts:
                logger.error("Máximo número de intentos de reconexión alcanzado")
                break
            continue
    
    logger.info("Programa finalizado")