from fastapi import FastAPI
import requests
import traceback

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API Directa de Rastreo Activa"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    # Esta es la URL de la API interna que descubriste
    # Usamos la estructura que viste en el tráfico de red
    api_url = f"https://www.servientrega.com/wps/portal/rastreo-envio/Services/ShipmentTracking/api/confirmation/{guia}/1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.servientrega.com/wps/portal/rastreo-envio",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        # Hacemos la petición directa a la API
        response = requests.get(api_url, headers=headers, timeout=15)
        
        # Si la API responde correctamente
        if response.status_code == 200:
            data = response.json()
            
            # Nota: Aquí asumo que la API devuelve un JSON. 
            # Según la URL, debería traer la información del envío.
            # Ajustamos el mapeo según lo que devuelva la API (usualmente 'Estado' o 'UltimoEstado')
            
            # Ejemplo de extracción basada en APIs comunes de Servientrega:
            estado = data.get("EstadoActual") or data.get("Movimiento") or "Información no disponible"
            
            return {
                "status": "success",
                "guia": guia,
                "resultado": estado,
                "detalles": data # Esto te sirve para ver todo lo que devuelve
            }
        else:
            return {
                "status": "error",
                "message": f"Servidor de Servientrega respondió con error {response.status_code}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": "No se pudo conectar con la API de Servientrega."
        }
