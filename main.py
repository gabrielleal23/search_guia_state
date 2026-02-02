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
        # Lanzamiento con bypass de detección de bots
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        
        # Simulamos un navegador real totalmente
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        try:
            # 1. Vamos a la web (esperamos que cargue el DOM principal)
            page.goto("https://www.servientrega.com/wps/portal/rastreo-envio", 
                      timeout=60000, 
                      wait_until="domcontentloaded")
            
            # 2. Esperamos un poco para que carguen los scripts internos
            page.wait_for_timeout(2000)
            
            # 3. Llenamos la guía
            input_selector = 'input#txtGuia'
            page.wait_for_selector(input_selector, timeout=15000)
            page.fill(input_selector, guia)
            
            # 4. Click en el botón
            page.click('button#btnConsultar')
            
            # 5. Esperamos por el ID lblEstadoActual
            # Usamos un selector que sea flexible con el ID
            selector_estado = '[id*="lblEstadoActual"]'
            page.wait_for_selector(selector_estado, timeout=30000)
            
            # 6. Extraemos el texto
            estado = page.locator(selector_estado).inner_text()
            
            return {
                "status": "success",
                "guia": guia,
                "resultado": estado.strip() if estado else "Estado no disponible"
            }
            
        except Exception as e:
            print(f"Error en Railway: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": "La página de Servientrega no respondió a tiempo o la guía es inválida."
            }
        
        finally:
            browser.close()
