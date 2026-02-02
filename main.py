from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()
@app.get("/")
def home():
    return {"message": "El servidor está encendido"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    with sync_playwright() as p:
        # Iniciamos el navegador (modo sin interfaz para ahorrar recursos)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # 1. Navegamos a la URL con espera de carga de red
            page.goto("https://www.servientrega.com/wps/portal/rastreo-envio", timeout=60000, wait_until="networkidle")
            
            # 2. Llenamos el número de guía
            page.wait_for_selector('input#txtGuia', timeout=10000)
            page.fill('input#txtGuia', guia)
            
            # 3. Hacemos clic en consultar
            page.click('button#btnConsultar')
            
            # 4. Esperamos específicamente por el ID del estado actual
            # Usamos el prefijo '#' para indicar que es un ID de CSS
            page.wait_for_selector('#lblEstadoActual', timeout=20000)
            
            # 5. Extraemos el texto
            estado = page.locator('#lblEstadoActual').inner_text()
            
            return {"status": "success", "guia": guia, "resultado": estado.strip()}
        
        except Exception as e:
            # Imprimimos el error en los logs de Railway para debuguear
            print(f"Error en scraping: {e}")
            return {"status": "error", "message": "No se encontró el estado o la guía es inválida."}
        
        
        finally:
            browser.close()
