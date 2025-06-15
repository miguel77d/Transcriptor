from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import os
from converter2 import transcribir_audio_whisper

app = FastAPI()

@app.post("/transcribir/")
async def transcribir_audio(file: UploadFile = File(...)):
    try:
        # Guardar archivo temporal
        contenido = await file.read()
        nombre_temp = "temp_audio.mp3"
        with open(nombre_temp, "wb") as f:
            f.write(contenido)

        # Llamar a la función del script que ya tenés
        texto = transcribir_audio_whisper(nombre_temp)

        # Eliminar archivo temporal
        os.remove(nombre_temp)

        return {"transcripcion": texto}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 8000))
uvicorn.run("main:app", host="0.0.0.0", port=port)
