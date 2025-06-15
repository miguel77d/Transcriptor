import os
import torch
import torchaudio
from pydub import AudioSegment
import numpy as np
import json
import time

def convertir_a_wav(ruta_entrada):
    """Convierte cualquier tipo de audio a WAV de 16kHz mono"""
    print(f"Convirtiendo {ruta_entrada} a formato WAV...")

    ruta_wav = "temp_audio.wav"
    
    try:
        # Detectar tipo de archivo automáticamente
        audio = AudioSegment.from_file(ruta_entrada)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)
        audio.export(ruta_wav, format="wav")
        
        print("Conversión completada.")
        return ruta_wav
    except Exception as e:
        print(f"Error al convertir a WAV: {e}")
        raise

def instalar_dependencias():
    """Instala las dependencias necesarias si no están ya instaladas"""
    try:
        import whisper
        print("Whisper ya está instalado.")
    except ImportError:
        print("Instalando OpenAI Whisper...")
        os.system("pip install -U openai-whisper")
        print("Whisper instalado.")
    
    try:
        import ffmpeg
        print("ffmpeg ya está instalado.")
    except ImportError:
        print("Instalando ffmpeg-python...")
        os.system("pip install ffmpeg-python")
        print("ffmpeg-python instalado.")

def mejorar_audio(ruta_wav):
    """Aplica mejoras básicas al audio para facilitar la transcripción"""
    import scipy.signal as signal
    from scipy.io import wavfile
    
    print("Aplicando mejoras al audio...")
    
    # Cargar el archivo
    rate, data = wavfile.read(ruta_wav)
    
    # Convertir a float
    if data.dtype.kind != 'f':
        data = data.astype(np.float32)
        if data.max() > 0:
            data = data / np.max(np.abs(data))
    
    # Amplificar señal
    data = np.clip(data * 1.5, -1.0, 1.0)
    
    # Guardar archivo mejorado
    wavfile.write(ruta_wav, rate, (data * 32767).astype(np.int16))
    
    print("Mejoras de audio aplicadas.")
    return ruta_wav

def cargar_modelo_whisper(tamaño_modelo="small"):
    """
    Carga el modelo Whisper con el tamaño especificado
    
    Tamaños disponibles:
    - tiny: más rápido pero menos preciso
    - base: equilibrio entre velocidad y precisión
    - small: buena precisión, velocidad moderada
    - medium: alta precisión, más lento
    - large: máxima precisión, muy lento
    """
    import whisper
    print(f"Cargando modelo Whisper {tamaño_modelo}...")
    try:
        modelo = whisper.load_model(tamaño_modelo)
        print(f"Modelo Whisper {tamaño_modelo} cargado correctamente.")
        return modelo
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        print("Intentando con modelo 'base'...")
        try:
            modelo = whisper.load_model("base")
            print("Modelo 'base' cargado como alternativa.")
            return modelo
        except:
            raise Exception("No se pudo cargar ningún modelo Whisper.")

def transcribir_con_whisper(ruta_audio, modelo, idioma="es"):
    """Transcribe audio usando el modelo Whisper"""
    import whisper
    
    print("Iniciando transcripción con Whisper...")
    
    # Opciones de transcripción
    opciones = {
        "language": idioma,         # Idioma del audio
        "task": "transcribe",       # Transcribir (en vez de traducir)
        "fp16": torch.cuda.is_available(),  # Usar precisión media si hay GPU
        "verbose": True             # Mostrar progreso detallado
    }
    
    # Realizar la transcripción
    print("Procesando audio, esto puede tardar unos minutos...")
    resultado = modelo.transcribe(ruta_audio, **opciones)
    
    print("Transcripción completada.")
    return resultado

def guardar_resultados(resultado, ruta_original):
    """Guarda los resultados de la transcripción en archivos de texto y JSON"""
    nombre_base = os.path.splitext(ruta_original)[0]
    
    # Guardar texto plano
    ruta_txt = f"{nombre_base}_whisper.txt"
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(resultado["text"])
    
    print(f"Resultados guardados en {ruta_txt}")
    return ruta_txt

def limpiar_archivos_temporales():
    """Elimina archivos temporales creados durante el proceso"""
    archivos_temp = ["temp_audio.wav"]
    for archivo in archivos_temp:
        if os.path.exists(archivo):
            os.remove(archivo)
    print("Archivos temporales eliminados.")

def mostrar_info_gpu():
    """Muestra información sobre la GPU disponible (si existe)"""
    if torch.cuda.is_available():
        print(f"GPU disponible: {torch.cuda.get_device_name(0)}")
        print(f"Memoria GPU total: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.2f} GB")
    else:
        print("No se detectó GPU. El proceso será más lento usando CPU.")

def transcribir_audio_whisper(ruta_mp3, tamaño_modelo="small", idioma="es"):
    """Función principal que orquesta todo el proceso de transcripción"""
    tiempo_inicio = time.time()
    
    try:
        # Paso 1: Verificar dependencias
        instalar_dependencias()
        
        # Paso 2: Mostrar información sobre GPU
        mostrar_info_gpu()
        
        # Paso 3: Convertir MP3 a WAV (formato requerido por Whisper)
        ruta_wav = convertir_a_wav(ruta_mp3)
        
        # Paso 4: Mejorar calidad del audio
        ruta_wav = mejorar_audio(ruta_wav)
        
        # Paso 5: Cargar modelo Whisper
        modelo = cargar_modelo_whisper(tamaño_modelo)
        
        # Paso 6: Transcribir audio
        resultado = transcribir_con_whisper(ruta_wav, modelo, idioma)
        
        # Paso 7: Guardar resultados
        ruta_txt = guardar_resultados(resultado, ruta_mp3)
        
        # Paso 8: Limpiar archivos temporales
        limpiar_archivos_temporales()
        
        # Mostrar resumen
        tiempo_total = time.time() - tiempo_inicio
        print(f"\nTranscripción completada en {tiempo_total:.2f} segundos")
        print(f"Texto guardado en: {ruta_txt}") 
        return resultado["text"]
        
    except Exception as e:
        print(f"Error durante la transcripción: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Solicitar información al usuario
    print("=" * 50)
    print("TRANSCRIPTOR DE AUDIO CON WHISPER")
    print("=" * 50)
    
    # Ruta del archivo
    ruta_por_defecto = "grabando2025-05-30 09-31-57.mp3"
    ruta_mp3 = input(f"Ruta del archivo MP3 [default: {ruta_por_defecto}]: ").strip()
    if not ruta_mp3:
        ruta_mp3 = ruta_por_defecto
    
    # Verificar que el archivo existe
    if not os.path.exists(ruta_mp3):
        print(f"ERROR: El archivo {ruta_mp3} no existe.")
        exit(1)
    
    # Tamaño del modelo
    print("\nTamaños de modelo disponibles:")
    print("- tiny: más rápido, menos preciso")
    print("- base: equilibrio entre velocidad y precisión")
    print("- small: buena precisión (recomendado)")
    print("- medium: alta precisión, más lento")
    print("- large: máxima precisión, muy lento")
    
    tamaño = input("\nSeleccione tamaño del modelo [default: small]: ").strip().lower()
    if tamaño not in ["tiny", "base", "small", "medium", "large"]:
        tamaño = "small"
    
    # Idioma
    idioma_defecto = "es"
    idioma = input(f"Código de idioma (es, en, fr, ...) [default: {idioma_defecto}]: ").strip().lower()
    if not idioma:
        idioma = idioma_defecto
    
    print("\nIniciando proceso de transcripción...")
    texto_transcrito = transcribir_audio_whisper(ruta_mp3, tamaño, idioma)
    
    if texto_transcrito:
        print("\n" + "=" * 50)
        print("TRANSCRIPCIÓN COMPLETA:")
        print("-" * 50)
        print(texto_transcrito)
        print("=" * 50)
    else:
        print("\nLa transcripción no pudo completarse.")
        print("Verifique que tiene todas las dependencias instaladas:")
        print("pip install openai-whisper torch torchaudio pydub numpy scipy ffmpeg-python")