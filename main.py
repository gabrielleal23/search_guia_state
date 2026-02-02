from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import traceback

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Servidor de Rastreo - Modo Resiliente"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    with sync_playwright() as p:
        # Lanzamos el navegador con argumentos de bypass total
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-web-security", # Ignora políticas que bloquean recursos
                "--disable-features=IsolateOrigins,site-per-process"
            ]
        )
        
        # Simulamos una pantalla y un usuario común
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        page = context.new_page()
        
        try:
            # 1. Navegación con tiempo extendido (Servientrega es lento desde el exterior)
            page.goto("https://www.servientrega.com/wps/portal/rastreo-envio", 
                      timeout=80000, 
                      wait_until="commit") # 'commit' es más rápido que 'load'
            
            # 2. Espera manual para dejar que el JS de Servientrega se ejecute
            page.wait_for_timeout(5000)
            
            # 3. Intentamos llenar la guía (usamos un selector más amplio por si cambia el ID)
            input_selector = 'input[id*="txtGuia"]'
            page.wait_for_selector(input_selector, timeout=20000, state="visible")
            page.fill(input_selector, guia)
            
            # 4. Click en consultar
            btn_selector = 'button[id*="btnConsultar"]'
            page.click(btn_selector)
            
            # 5. Esperamos a que aparezca el resultado (lblEstadoActual)
            # Le damos 40 segundos porque el backend de Servientrega suele demorar la respuesta
            res_selector = '[id*="lblEstadoActual"]'
            page.wait_for_selector(res_selector, timeout=40000, state="attached")
            
            # Capturamos el texto
            estado = page.locator(res_selector).inner_text()
            
            if not estado or len(estado.strip()) < 2:
                # Si está vacío, puede ser que el rastreo sea una tabla
                return {"status": "success", "guia": guia, "resultado": "Guía en proceso o no encontrada en el sistema."}

            return {
                "status": "success",
                "guia": guia,
                "resultado": estado.strip()
            }
            
        except Exception as e:
            # Imprimimos el error real en los logs de Railway para que lo veas
            print(f"Error técnico en Railway: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": "Servientrega no respondió. Esto suele ser un bloqueo de IP. Intenta de nuevo en unos minutos."
            }
        
        finally:
            browser.close()
