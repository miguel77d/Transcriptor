from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import os
from converter2 import transcribir_audio_whisper

app = FastAPI()

# Ruta raíz: bienvenida
@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Transcripción con Whisper!"}

# Ruta POST para transcribir audio
@app.post("/transcribir")
async def transcribir_audio(file: UploadFile = File(...)):
    try:
        # Guardar archivo temporal
        contenido = await file.read()
        nombre_temp = "temp_audio.mp3"
        with open(nombre_temp, "wb") as f:
            f.write(contenido)

        # Llamar a la función de transcripción
        texto = transcribir_audio_whisper(nombre_temp)

        # Eliminar archivo temporal
        os.remove(nombre_temp)

        return {"transcripcion": texto}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Solo necesario si ejecutás localmente con Python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
