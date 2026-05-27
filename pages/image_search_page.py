import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage


class ImageSearchPage(BasePage):
    """
    Page Object para a funcionalidade de pesquisa por imagem do AliExpress.

    Fluxo real (inspecionado ao vivo):
      1. Focar o campo de busca para o botão de câmera ficar acessível
      2. Clicar no div[class*='picture-search-btn'] (ícone de câmera)
      3. Aguardar o modal esm--upload-container aparecer
      4. O modal contém um input[type='file'] oculto (display:none)
      5. Usar JS para torná-lo visível e enviar o caminho absoluto da imagem
      6. O AliExpress analisa a imagem e redireciona para resultados de busca
    """

    # Ícone de câmera — aparece dentro do container de busca após focar o input
    IMAGE_SEARCH_BTN = (By.CSS_SELECTOR, "div[class*='picture-search-btn']")

    # Modal que aparece após clicar no ícone de câmera
    UPLOAD_CONTAINER = (By.CSS_SELECTOR, "div[class*='upload-container']")

    # Input de arquivo dentro do modal (oculto com display:none)
    IMAGE_UPLOAD_INPUT = (By.CSS_SELECTOR, "input[type='file'][accept*='jpg']")

    # Campo de busca (necessário para o botão de câmera aparecer)
    SEARCH_INPUT = (By.ID, "search-words")

    def __init__(self, driver):
        super().__init__(driver)

    def open_image_search(self):
        """
        1. Foca o campo de busca (necessário para o botão de câmera aparecer no DOM).
        2. Clica no ícone de câmera via JavaScript (está dentro de aria-hidden='true').
        3. Aguarda o modal de upload ficar visível.

        Levanta Exception se o botão ou o modal não forem encontrados.
        """
        # Foca o campo de busca para o botão de câmera aparecer
        try:
            search = self.wait.until(EC.presence_of_element_located(self.SEARCH_INPUT))
            search.click()
            time.sleep(1)
        except TimeoutException:
            raise Exception("Campo de busca não encontrado — verifique se a home carregou.")

        # Localiza o botão de câmera
        try:
            btn = self.wait.until(EC.presence_of_element_located(self.IMAGE_SEARCH_BTN))
            # Usa JS para clicar pois o botão está dentro de aria-hidden='true'
            self.driver.execute_script("arguments[0].click();", btn)
            print("Botão de câmera clicado.")
        except TimeoutException:
            raise Exception(
                "Botão de câmera (picture-search-btn) não encontrado. "
                "O seletor pode ter mudado — inspecione a página."
            )

        # Aguarda o modal de upload aparecer
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.UPLOAD_CONTAINER)
            )
            print("Modal de upload de imagem aberto.")
        except TimeoutException:
            raise Exception("Modal de upload não apareceu após clicar no botão de câmera.")

    def upload_image(self, image_path):
        """
        Envia o caminho absoluto da imagem para o input[type='file'] do modal.

        O input é oculto via display:none — usa JavaScript para torná-lo visível
        antes de chamar send_keys (necessário para Selenium interagir com ele).

        :param image_path: Caminho absoluto para o arquivo de imagem.
        :raises FileNotFoundError: Se o arquivo não existir.
        :raises Exception: Se o input de upload não for encontrado no modal.
        """
        import os
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

        # Aguarda o input de arquivo estar no DOM (dentro do modal)
        try:
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.IMAGE_UPLOAD_INPUT)
            )
        except TimeoutException:
            raise Exception(
                "Input de upload (input[type='file']) não encontrado no modal. "
                "Verifique se open_image_search() foi chamado antes."
            )

        # Remove o display:none via JavaScript para que send_keys funcione
        self.driver.execute_script(
            "arguments[0].style.display = 'block';"
            "arguments[0].style.visibility = 'visible';"
            "arguments[0].style.opacity = '1';",
            file_input
        )

        file_input.send_keys(image_path)
        print(f"Imagem enviada: {image_path}")

    def wait_for_image_search_results(self, timeout=20):
        """
        Aguarda a página navegar para os resultados após o upload da imagem.

        O AliExpress analisa a imagem e redireciona para uma página de busca
        com termos gerados automaticamente (URL contém 'SearchText' ou similar).
        """
        home_url = "pt.aliexpress.com/?gatewayAdapt"
        print("Aguardando redirecionamento para os resultados...")

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: home_url not in d.current_url and len(d.current_url) > 40
            )
            time.sleep(2)  # Aguarda a página de resultados estabilizar
            print(f"Redirecionado para: {self.driver.current_url}")
            return True
        except TimeoutException:
            print(f"Timeout aguardando resultados. URL atual: {self.driver.current_url}")
            return False

    def is_on_image_search_results(self):
        """
        Verifica se a URL atual indica resultados de pesquisa (por imagem ou texto gerado).

        Após a pesquisa por imagem, o AliExpress redireciona para uma página de resultados
        com SearchText gerado por IA — os mesmos indicadores de busca textual se aplicam.
        """
        url = self.driver.current_url.lower()
        indicators = [
            "searchtext",    # busca textual gerada pela IA a partir da imagem
            "imgurl",        # parâmetro direto de URL de imagem
            "imagesearch",   # caminho de pesquisa visual
            "wholesale",     # página de resultados do AliExpress
            "w/wholesale",   # variante do caminho de resultados
        ]
        # Garante também que não está mais na home
        is_home = "aliexpress.com/?gatewayAdapt" in self.driver.current_url
        return not is_home and any(ind in url for ind in indicators)
