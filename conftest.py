import pytest
from selenium import webdriver

@pytest.fixture(scope="session")
def driver():
    # Setup do Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications") # Ajuda a evitar alguns popups nativos
    
    # Inicia o driver (Selenium 4.6+ gerencia o ChromeDriver automaticamente)
    driver = webdriver.Chrome(options=options)
    
    # Wait implícito global (pode ser sobrescrito por waits explícitos no BasePage)
    driver.implicitly_wait(5)
    
    yield driver
    
    # Teardown: fecha o navegador após o teste
    driver.quit()
