import os
import time
import pytest
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.image_search_page import ImageSearchPage

# Caminho absoluto para o diretório de imagens do projeto
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")

# Imagem pré-pronta (Caminho 2)
PRESET_IMAGE_PATH = os.path.join(IMAGES_DIR, "Xicara.jpg")

# Imagem que será capturada em runtime (Caminho 1)
CAPTURED_IMAGE_PATH = os.path.join(IMAGES_DIR, "captured_from_search.png")


def _setup_home(driver):
    """Helper interno: acessa a home e fecha popups. Não é uma fixture pública."""
    home = HomePage(driver)
    home.load()
    home.close_popups()
    return home


def _perform_image_search(driver, image_path):
    """
    Helper interno: executa o fluxo de pesquisa por imagem dado um caminho de arquivo.
    Tenta abrir o modal de câmera primeiro; se não encontrar, faz upload direto.
    """
    img_search = ImageSearchPage(driver)

    # Tenta clicar no ícone de câmera (pode não ser necessário em todos os casos)
    img_search.open_image_search()

    # Envia a imagem para o input de upload
    img_search.upload_image(image_path)

    # Aguarda os resultados carregarem
    img_search.wait_for_image_search_results()

    return img_search


# ---------------------------------------------------------------------------
# CAMINHO 1: Captura a primeira imagem de um resultado de busca textual
#            e a usa para fazer pesquisa por imagem
# ---------------------------------------------------------------------------
def test_image_search_from_captured(driver):
    """
    Caso de Teste — Caminho 1:
    1. Realiza uma busca textual por 'xicara'
    2. Captura a primeira imagem de produto nos resultados via screenshot de elemento
    3. Volta para a home
    4. Usa a imagem capturada para realizar a pesquisa visual
    5. Valida que a página de resultados de imagem foi carregada

    Pode ser executado isoladamente:
        pytest tests/test_image_search.py::test_image_search_from_captured -v -s
    """
    termo_busca = "xicara"

    # --- ETAPA 1: Busca textual para chegar à página de resultados ---
    print(f"\n[Caminho 1] Acessando a home e buscando por '{termo_busca}'...")
    home = _setup_home(driver)
    home.search_for(termo_busca)

    # --- ETAPA 2: Captura a primeira imagem do produto ---
    print("[Caminho 1] Aguardando resultados carregarem...")
    time.sleep(4)  # Aguarda os cards de produto renderizarem

    results_page = SearchResultsPage(driver)
    captured = results_page.capture_first_product_image(CAPTURED_IMAGE_PATH)

    assert captured, (
        "Não foi possível capturar a primeira imagem de produto dos resultados de busca. "
        "Verifique se os cards de produto estão visíveis na página."
    )
    assert os.path.isfile(CAPTURED_IMAGE_PATH), (
        f"O arquivo de imagem capturada não foi encontrado em: {CAPTURED_IMAGE_PATH}"
    )
    print(f"[Caminho 1] Imagem capturada com sucesso: {CAPTURED_IMAGE_PATH}")

    # --- ETAPA 3: Volta para a home ---
    print("[Caminho 1] Voltando para a home para realizar a pesquisa por imagem...")
    _setup_home(driver)

    # --- ETAPA 4: Pesquisa visual com a imagem capturada ---
    print(f"[Caminho 1] Iniciando pesquisa por imagem com: {CAPTURED_IMAGE_PATH}")
    img_search = _perform_image_search(driver, CAPTURED_IMAGE_PATH)

    # --- ETAPA 5: Validação ---
    time.sleep(3)
    url_final = driver.current_url
    print(f"[Caminho 1] URL final: {url_final}")

    assert img_search.is_on_image_search_results(), (
        f"A pesquisa por imagem (Caminho 1) não redirecionou para uma página de resultados visuais. "
        f"URL obtida: {url_final}"
    )
    print("[Caminho 1] Teste finalizado com sucesso!")


# ---------------------------------------------------------------------------
# CAMINHO 2: Usa a imagem pré-pronta (images/Xicara.jpg) para pesquisa visual
# ---------------------------------------------------------------------------
def test_image_search_from_preset(driver):
    """
    Caso de Teste — Caminho 2:
    1. Acessa a home e fecha popups
    2. Usa o arquivo pré-pronto 'images/Xicara.jpg' para pesquisa visual
    3. Valida que a página de resultados de imagem foi carregada

    Pode ser executado isoladamente:
        pytest tests/test_image_search.py::test_image_search_from_preset -v -s
    """
    assert os.path.isfile(PRESET_IMAGE_PATH), (
        f"Imagem pré-pronta não encontrada em: {PRESET_IMAGE_PATH}. "
        "Verifique se o arquivo 'images/Xicara.jpg' está presente no projeto."
    )

    # --- ETAPA 1: Acessa a home ---
    print(f"\n[Caminho 2] Acessando a home...")
    _setup_home(driver)

    # --- ETAPA 2: Pesquisa visual com a imagem pré-pronta ---
    print(f"[Caminho 2] Iniciando pesquisa por imagem com: {PRESET_IMAGE_PATH}")
    img_search = _perform_image_search(driver, PRESET_IMAGE_PATH)

    # --- ETAPA 3: Validação ---
    time.sleep(3)
    url_final = driver.current_url
    print(f"[Caminho 2] URL final: {url_final}")

    assert img_search.is_on_image_search_results(), (
        f"A pesquisa por imagem (Caminho 2) não redirecionou para uma página de resultados visuais. "
        f"URL obtida: {url_final}"
    )
    print("[Caminho 2] Teste finalizado com sucesso!")
