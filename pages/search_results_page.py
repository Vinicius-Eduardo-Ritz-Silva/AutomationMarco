import os
from selenium.webdriver.common.by import By
from .base_page import BasePage

class SearchResultsPage(BasePage):
    # Locator para os títulos dos produtos na listagem
    # AliExpress usa div[role='heading'] para os títulos nos cards de produto
    PRODUCT_TITLES = (By.CSS_SELECTOR, "div[role='heading']")

    # Locator da primeira imagem de produto nos cards de resultado
    # Tenta pegar a primeira <img> dentro dos cards de produto (role=item ou similar)
    FIRST_PRODUCT_IMAGE = (By.CSS_SELECTOR, "div[class*='card'] img, a[class*='card'] img, div[class*='product'] img")

    def __init__(self, driver):
        super().__init__(driver)

    def get_product_titles(self):
        """Retorna uma lista com o texto de todos os títulos de produtos visíveis."""
        elements = self.driver.find_elements(*self.PRODUCT_TITLES)
        return [el.text for el in elements if el.text.strip() != ""]

    def is_on_results_page(self, search_term):
        """Verifica se a URL atual condiz com uma página de resultados de busca."""
        url_atual = self.driver.current_url.lower()
        # AliExpress pode usar 'SearchText' ou 'wholesale-termo-com-hifens'
        term_slug = search_term.lower().replace(" ", "-")
        return "searchtext" in url_atual or term_slug in url_atual or "wholesale" in url_atual

    def capture_first_product_image(self, save_path):
        """
        Captura um screenshot da primeira imagem de produto visível nos resultados
        e salva no caminho especificado. Retorna True se bem-sucedido, False caso contrário.
        
        Uso opcional — não afeta nenhum teste existente.
        """
        try:
            images = self.driver.find_elements(*self.FIRST_PRODUCT_IMAGE)
            # Filtra imagens que têm dimensão real (descarta ícones e placeholders)
            valid = [img for img in images if img.size["width"] > 50 and img.size["height"] > 50]
            if not valid:
                print("Nenhuma imagem de produto encontrada para captura.")
                return False

            first_img = valid[0]
            # Garante que o diretório de destino exista
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            first_img.screenshot(save_path)
            print(f"Imagem capturada e salva em: {save_path}")
            return True
        except Exception as e:
            print(f"Erro ao capturar imagem do produto: {e}")
            return False
