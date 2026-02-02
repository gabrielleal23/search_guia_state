from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import traceback

app = FastAPI()

@app.get("/")
def home():
    return {"message": "El servidor de rastreo está activo"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    # Iniciamos Playwright
    with sync_playwright() as p:
        # Argumentos necesarios para entornos como Railway/Docker
        browser = p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        
        # Configuramos un User-Agent real para evitar ser detectados como bot
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        try:
            # 1. Vamos a la URL de Servientrega
            # 'networkidle' espera a que no haya tráfico de red (página cargada)
            page.goto("https://www.servientrega.com/wps/portal/rastreo-envio", timeout=60000, wait_until="networkidle")
            
            # 2. Llenamos el campo de guía
            page.wait_for_selector('input#txtGuia', timeout=15000)
            page.fill('input#txtGuia', guia)
            
            # 3. Hacemos clic en el botón de consulta
            page.click('button#btnConsultar')
            
            # 4. Esperamos el elemento del estado
            # Usamos un selector que busca el ID que mencionaste
            selector_estado = 'span[id*="lblEstadoActual"]'
            page.wait_for_selector(selector_estado, timeout=20000)
            
            # 5. Extraemos el texto del resultado
            estado = page.locator(selector_estado).inner_text()
            
            return {
                "status": "success", 
                "guia": guia, 
                "resultado": estado.strip()
            }
        
        except Exception as e:
            # Imprimimos el error real en los logs de Railway
            print(f"--- ERROR DETECTADO ---")
            print(traceback.format_exc())
            
            return {
                "status": "error", 
                "message": f"Error al consultar: {str(e)}"
            }
        
        finally:
            # Cerramos el navegador siempre
            browser.close()
