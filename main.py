from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import traceback

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Servidor de Rastreo Servientrega Activo"}

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    with sync_playwright() as p:
        # Lanzamiento con banderas para reducir la huella de automatización
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # Simulamos un perfil de usuario real
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.new_page()
        
        try:
            # 1. Navegación con espera moderada
            page.goto("https://www.servientrega.com/wps/portal/rastreo-envio", timeout=60000, wait_until="load")
            
            # 2. Espera a que el input sea interactuable
            input_selector = 'input#txtGuia'
            page.wait_for_selector(input_selector, timeout=20000)
            page.fill(input_selector, guia)
            
            # 3. Forzar el clic y esperar la respuesta de red
            # A veces el botón necesita un pequeño delay para que el script de la página esté listo
            page.wait_for_timeout(1000)
            page.click('button#btnConsultar')
            
            # 4. CRUCIAL: Esperamos a que el label de estado cambie o aparezca
            # Usamos un selector que busque el ID parcial ya que Servientrega usa portlets dinámicos
            selector_estado = 'span[id*="lblEstadoActual"]'
            
            # Esperamos hasta 30 segundos porque el backend de Servientrega suele ser lento
            page.wait_for_selector(selector_estado, timeout=30000)
            
            # 5. Extracción limpia
            estado = page.locator(selector_estado).inner_text()
            
            if not estado or len(estado.strip()) == 0:
                return {"status": "error", "message": "Guía encontrada pero sin estado disponible."}

            return {
                "status": "success",
                "guia": guia,
                "resultado": estado.strip()
            }
            
        except Exception as e:
            # Log detallado para ti en Railway
            print(f"Error consultando guía {guia}: {str(e)}")
            return {
                "status": "error", 
                "message": "No se pudo obtener el estado. Verifique que el número de guía sea correcto."
            }
        
        finally:
            browser.close()
