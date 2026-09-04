import random
import time

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

        # --- Fingerprint / automation-flag hardening ---
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
        })

        # --- Stability / sandboxing ---
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--lang=bg-BG")  # match locale to the site being scraped

        # --- Reduce automation "tells" further ---
        self.options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        self.options.add_argument("--disable-web-security")  # optional, use only if needed
        self.options.add_argument("--no-first-run")
        self.options.add_argument("--no-default-browser-check")

        width, height = window_size
        self.options.add_argument(f"--window-size={width},{height}")

        if headless:
            self.options.add_argument("--headless=new")

        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, timeout)

        # --- CDP-level patching: strip webdriver flag + cdc_ variables ---
        self._patch_automation_fingerprint()

        if url is not None:
            self.driver.get(url)

    def _patch_automation_fingerprint(self):
        """Inject JS before every page load to mask common automation tells."""
        stealth_js = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['bg-BG', 'bg', 'en-US', 'en']});
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters)
            );
        """
        try:
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": stealth_js}
            )
        except Exception as e:
            print(f"Warning: could not patch automation fingerprint: {e}")

    def random_sleep(self, x: float, y: float):
        """Sleep for a random duration between x and y seconds (human-like jitter)."""
        duration = random.uniform(x, y)
        time.sleep(duration)

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
