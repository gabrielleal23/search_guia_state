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
        # Lanzamiento con modo 'stealth' manual
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # Simulamos una resolución y un User-Agent muy común
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768}
        )
        
        page = context.new_page()
        
        try:
            # 1. Navegación con tiempo de espera extendido
            page.goto("https://www.servientrega.com/wps/portal/rastreo-envio", 
                      timeout=90000, 
                      wait_until="networkidle") # Esperamos a que la red descanse
            
            # 2. Asegurarnos de que el input está listo
            page.wait_for_selector('input#txtGuia', timeout=20000)
            page.fill('input#txtGuia', guia)
            
            # 3. Pequeña pausa humana antes de clickear
            page.wait_for_timeout(1500)
            page.click('button#btnConsultar')
            
            # 4. CAMBIO CLAVE: Esperar a que la URL cambie o que el elemento aparezca
            # Servientrega a veces recarga la página o actualiza un fragmento.
            # Probamos con un selector que espera el texto que realmente nos importa
            selector_final = '#lblEstadoActual' 
            
            # Esperamos que el elemento sea visible y no esté vacío
            page.wait_for_selector(selector_final, timeout=40000, state="visible")
            
            # Extraemos el contenido
            estado = page.locator(selector_final).inner_text()
            
            # Si el texto está vacío, puede que necesitemos esperar un poco más
            if not estado.strip():
                page.wait_for_timeout(2000)
                estado = page.locator(selector_final).inner_text()

            return {
                "status": "success",
                "guia": guia,
                "resultado": estado.strip()
            }
            
        except Exception as e:
            # Esto imprimirá el error real en los logs de Railway
            print(f"Error detallado para guía {guia}: {traceback.format_exc()}")
            return {
                "status": "error", 
                "message": f"Timeout o error de red: {str(e)[:100]}" 
            }
        
        finally:
            browser.close()
