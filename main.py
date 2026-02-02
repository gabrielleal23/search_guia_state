from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import traceback

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Servidor de Rastreo Activo"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    with sync_playwright() as p:
        # Lanzamiento con banderas para evitar detección y optimizar memoria en Railway
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled" # Oculta que es un bot
            ]
        )
        
        # Creamos un contexto con un User-Agent de Chrome real y moderno
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.new_page()
        
        try:
            # 1. Navegamos con 'load' en lugar de 'domcontentloaded' para dar tiempo a los scripts
            page.goto(
                "https://www.servientrega.com/wps/portal/rastreo-envio", 
                timeout=60000, 
                wait_until="load" 
            )
            
            # 2. Espera extra por si el servidor está lento
            page.wait_for_timeout(3000) 

            # 3. Buscamos el input. Si falla aquí, es que el sitio bloqueó la IP de Railway
            page.wait_for_selector('input#txtGuia', timeout=20000, state="visible")
            page.fill('input#txtGuia', guia)
            
            # 4. Click en consultar
            page.click('button#btnConsultar')
            
            # 5. Esperamos el resultado
            selector_final = 'span[id*="lblEstadoActual"]'
            page.wait_for_selector(selector_final, timeout=25000)
            
            estado = page.locator(selector_final).inner_text()
            
            return {
                "status": "success",
                "guia": guia,
                "resultado": estado.strip()
            }
            
        except Exception as e:
            print(f"Error en consulta {guia}: {str(e)}")
            return {
                "status": "error",
                "message": f"No se pudo cargar el formulario. Servientrega podría estar saturado o bloqueando la conexión."
            }
        
        finally:
            browser.close()
