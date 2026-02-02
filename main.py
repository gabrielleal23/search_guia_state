from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API de Rastreo Directa Activa"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    # URL del portal de rastreo
    url = "https://www.servientrega.com/wps/portal/rastreo-envio"
    
    # Headers para parecer un navegador real y no ser bloqueado
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,.*/*;q=0.8",
        "Referer": "https://www.servientrega.com/"
    }

    try:
        # 1. Iniciamos una sesión para manejar cookies (crucial para Servientrega)
        session = requests.Session()
        session.headers.update(headers)
        
        # 2. Primera petición para obtener las cookies de sesión
        response = session.get(url, timeout=20)
        
        # 3. Segunda petición simulando la búsqueda de la guía
        # Nota: Servientrega usa parámetros específicos en el GET o POST. 
        # Esta es la URL de consulta directa simplificada:
        params = {"idGuia": guia}
        search_url = f"https://www.servientrega.com/wps/portal/rastreo-envio/!ut/p/z1/?" # URL dinámica
        
        # Intentamos obtener el resultado
        res = session.get(url, params=params, timeout=20)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Buscamos el ID que identificaste: lblEstadoActual
            estado_tag = soup.find(id=lambda x: x and 'lblEstadoActual' in x)
            
            if estado_tag:
                return {
                    "status": "success",
                    "guia": guia,
                    "resultado": estado_tag.text.strip()
                }
            
        # Si no lo encuentra por ID, intentamos un método genérico de respaldo
        return {
            "status": "error",
            "message": "Guía no encontrada o el portal cambió su estructura."
        }

    except Exception as e:
        return {
            "status": "error", 
            "message": f"Fallo de conexión: {str(e)}"
        }
