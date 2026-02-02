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
        # Configuración de lanzamiento optimizada para servidores
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox", 
                "--disable-dev-shm-usage", 
                "--disable-setuid-sandbox",
                "--no-zygote"
            ]
        )
        
        # User-Agent actualizado para parecer un navegador humano real
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.new_page()
        
        try:
            # 1. Navegación rápida: 'domcontentloaded' es más veloz que 'networkidle'
            page.goto(
                "https://www.servientrega.com/wps/portal/rastreo-envio", 
                timeout=45000, 
                wait_until="domcontentloaded"
            )
            
            # 2. Espera corta para asegurar que el input cargó
            page.wait_for_selector('input#txtGuia', timeout=10000)
            page.fill('input#txtGuia', guia)
            
            # 3. Ejecución de la búsqueda
            page.click('button#btnConsultar')
            
            # 4. Espera específica por el ID que necesitas
            # Usamos un selector CSS que busca cualquier span cuyo ID contenga 'lblEstadoActual'
            selector_final = 'span[id*="lblEstadoActual"]'
            page.wait_for_selector(selector_final, timeout=25000)
            
            # 5. Captura del texto
            resultado_texto = page.locator(selector_final).inner_text()
            
            if not resultado_texto:
                return {"status": "error", "message": "Guía no encontrada o sin estado actual."}

            return {
                "status": "success",
                "guia": guia,
                "resultado": resultado_texto.strip()
            }
            
        except Exception as e:
            # Imprime el error completo en los logs de Railway para tu revisión técnica
            print(f"Error detectado en la consulta {guia}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error: {str(e)}"
            }
        
        finally:
            browser.close()
