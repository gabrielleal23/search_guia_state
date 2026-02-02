from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()

@app.get("/rastrear/{guia}")
def rastrear_servientrega(guia: str):
    with sync_playwright() as p:
        # Iniciamos el navegador (modo sin interfaz para ahorrar recursos)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. Vamos a la URL
            page.goto("https://www.servientrega.com/wps/portal/rastreo-envio", timeout=60000)
            
            # 2. Llenamos el campo y buscamos
            page.fill('input#txtGuia', guia)
            page.click('button#btnConsultar')
            
            # 3. Esperamos el resultado (ajusta el selector según la tabla)
            page.wait_for_selector('.table-responsive', timeout=10000)
            
            # 4. Extraemos el estado de la primera fila
            # Nota: Servientrega suele poner el estado en la columna 4
            estado = page.locator('table.table >> tr >> td').nth(3).inner_text()
            
            return {"status": "success", "guia": guia, "resultado": estado.strip()}
        
        except Exception as e:
            return {"status": "error", "message": "No se pudo encontrar la guía o la página tardó mucho."}
        
        finally:
            browser.close()