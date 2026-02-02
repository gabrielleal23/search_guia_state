from fastapi import FastAPI
import requests
import traceback

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API Directa de Rastreo Activa"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    # Usamos una sesión para mantener las cookies entre peticiones
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.servientrega.com/wps/portal/rastreo-envio",
        "Connection": "keep-alive"
    }
    
    session.headers.update(headers)

    try:
        # 1. "Tocamos" la página principal para obtener cookies de sesión (JSESSIONID, etc.)
        session.get("https://www.servientrega.com/wps/portal/rastreo-envio", timeout=15)
        
        # 2. Ahora consultamos la API que encontraste con la sesión activa
        # Agregamos un 1 al final porque es el parámetro típico de 'tipo de consulta'
        api_url = f"https://www.servientrega.com/wps/portal/rastreo-envio/Services/ShipmentTracking/api/confirmation/{guia}/1"
        
        response = session.get(api_url, timeout=15, verify=True)
        
        if response.status_code == 200:
            data = response.json()
            
            # Servientrega suele devolver una lista o un objeto. 
            # Si 'data' es una lista, tomamos el primer elemento.
            if isinstance(data, list) and len(data) > 0:
                info = data[0]
            else:
                info = data

            # Extraemos el campo del estado (ajusta según lo que veas en tu Network Tab)
            # Normalmente es 'EstadoActual' o 'Movimiento'
            estado = info.get("EstadoActual") or info.get("UltimoEstado") or "Estado no encontrado en JSON"
            
            return {
                "status": "success",
                "guia": guia,
                "resultado": estado
            }
        
        return {
            "status": "error",
            "message": f"Servientrega respondió con código {response.status_code}"
        }

    except Exception as e:
        # Esto te dirá en Railway si es un error de SSL, DNS o Timeout
        print(f"Error técnico: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": f"Error de conexión: {str(e)[:50]}"
        }
