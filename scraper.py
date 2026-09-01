from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium import webdriver


class Scraper:
    def __init__(self,
                 window_size: tuple[int, int] = (1920, 1080),
                 headless: bool = True,
                 timeout: int = 10,
                 url: str = None,
                 ):
        self.options = Options()
        self.options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)

        if headless:
            self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")

        width, height = window_size
        self.options.add_argument(f"--window-size={width},{height}")

        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, timeout)

        if url is not None:
            self.driver.get(url)

    def click_element(self, button_xpath: str = None):
        if not button_xpath:
            raise ValueError("button_xpath is required")
        try:
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            ).click()
        except TimeoutException as e:
            raise TimeoutException(f"Element not clickable: {button_xpath}") from e

    def input_data(self, data: str, field_xpath: str):
        if data is None:
            raise ValueError("data is required")
        if not field_xpath:
            raise ValueError("field_xpath is required")
        try:
            field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, field_xpath))
            )
        except TimeoutException as e:
            raise TimeoutException(f"Element not found: {field_xpath}") from e
        field.send_keys(data)

    def get_text_from_element(self, element_xpath: str) -> str:
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, element_xpath))
            )
        except TimeoutException as e:
            raise TimeoutException(f"Element not found: {element_xpath}") from e
        return element.text
