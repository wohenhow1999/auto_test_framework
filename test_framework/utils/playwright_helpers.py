import logging
import pytest
from playwright.sync_api import sync_playwright, BrowserContext, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from typing import Optional, Union, Tuple

class PlaywrightHelper:
    def __init__(
        self,
        logger: Optional[Union[logging.Logger, logging.LoggerAdapter]] = None,
        headless: bool = True
    ) -> None:
        """
        Initialize the PlaywrightHelper instance.

        Args:
            logger (Optional[Union[logging.Logger, logging.LoggerAdapter]]): 
                Optional logger instance to use for logging. 
                If None, the default logger for the module will be used.
            headless (bool): 
                Whether to launch the browser in headless mode. Default is True.

        Attributes:
            playwright (Optional[Playwright]): Playwright driver instance.
            browser (Optional[Browser]): Browser instance.
            context (Optional[BrowserContext]): Browser context instance.
            page (Optional[Page]): Browser page instance.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def start(self) -> None:
        """
        Start Playwright and launch browser.
        """
        self.logger.info("Starting Playwright driver...")
        try:
            self.playwright = sync_playwright().start()
            self.logger.debug("Playwright driver started successfully.")
        except Exception as e:
            self.logger.error(f"Failed to start Playwright driver: {e}")
            pytest.fail(f"Failed to start Playwright: {e}")

        self.logger.info(f"Launching Chromium browser (headless={self.headless})...")
        try:
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.logger.debug("Chromium browser launched successfully.")
        except Exception as e:
            self.logger.error(f"Failed to launch Chromium browser: {e}")
            pytest.fail(f"Failed to launch browser: {e}")

        self.logger.info("Browser started and ready for context creation.")

    def new_context(self) -> BrowserContext:
        """
        Create a new browser context without opening a page.

        Returns:
            BrowserContext: The newly created browser context.
        """
        if not self.browser:
            self.logger.error("Browser is not started. Cannot create context.")
            pytest.fail("Browser is not started. Call start() first.")

        self.context = self.browser.new_context()
        self.logger.info("New browser context created.")
        return self.context
    
    def new_page(self) -> Page:
        """
        Create a new page in the existing browser context. No navigation here.
        """
        if not self.context:
            self.logger.error("No browser context found. Cannot create page.")
            pytest.fail("Browser context is not created. Call new_context() first.")

        self.page = self.context.new_page()
        self.logger.info("New page created.")
        return self.page

    def launch(self) -> Page:
        """
        Start Playwright, create a new browser context, and open a blank page.

        Returns:
            Page: The created page object.
        """
        self.logger.info("Launching Playwright browser session...")
        self.start()
        self.new_context()
        page = self.new_page()
        self.logger.info("Browser session ready.")
        return page

    def open_page(
        self, 
        url: str,
        expected_title: Optional[str] = None,
        expect_url: Optional[str] = None,
        wait_for_selector: Optional[str] = None,
        timeout: int = 5000
    ) -> None:
        """
        Navigate to a URL and optionally verify page title, URL, and wait for an element.

        Args:
            url (str): URL to open.
            expected_title (Optional[str]): Substring expected in page title.
            expect_url (Optional[str]): Substring expected in final page URL.
            wait_for_selector (Optional[str]): CSS or XPath selector to wait for.
            timeout (int): Timeout in milliseconds for wait operations. Default is 5000 ms.
        """
        if not self.page:
            self.logger.error("Page is not created. Call new_context() first.")
            pytest.fail("Page is not created. Call new_context() first.")

        self.logger.info(f"Navigating to {url} ...")
        self.page.goto(url, timeout=timeout)

        if expected_title:
            title = self.page.title()
            if expected_title not in title:
                self.logger.error(f"Expected title to contain '{expected_title}', but got '{title}'.")
                pytest.fail(f"Page title validation failed: '{title}'")
            self.logger.info(f"Title validation passed: '{title}'")
        
        if expect_url:
            current_url = self.page.url
            if expect_url not in current_url:
                self.logger.error(f"Expected URL to contain '{expect_url}', but got '{current_url}'.")
                pytest.fail(f"URL validation failed: '{current_url}'")
            self.logger.info(f"URL validation passed: '{current_url}'")
        
        if wait_for_selector:
            try:
                self.page.wait_for_selector(wait_for_selector, timeout=timeout)
                self.logger.info(f"Element found: '{wait_for_selector}'")
            except PlaywrightTimeoutError:
                self.logger.error(f"Timeout waiting for selector: '{wait_for_selector}'")
                pytest.fail(f"Timeout waiting for element: '{wait_for_selector}'")
        
        self.logger.info(f"Successfully opened page: {url}")
    
    def close(self) -> None:
        """
        Close page, context, browser and stop Playwright.
        """
        if self.page:
            self.logger.info("Closing page...")
            try:
                self.page.close()
                self.logger.debug("Page closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing page: {e}")
            finally:
                self.page = None
        else:
            self.logger.debug("No active page to close.")

        if self.context:
            self.logger.info("Closing browser context...")
            try:
                self.context.close()
                self.logger.debug("Browser context closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing context: {e}")
            finally:
                self.context = None
        else:
            self.logger.debug("No active browser context to close.")

        if self.browser:
            self.logger.info("Closing browser instance...")
            try:
                self.browser.close()
                self.logger.debug("Browser instance closed successfully.")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            finally:
                self.browser = None
        else:
            self.logger.debug("No active browser instance to close.")

        if self.playwright:
            self.logger.info("Stopping Playwright driver...")
            try:
                self.playwright.stop()
                self.logger.debug("Playwright driver stopped successfully.")
            except Exception as e:
                self.logger.error(f"Error stopping Playwright: {e}")
            finally:
                self.playwright = None
        else:
            self.logger.debug("No active Playwright driver to stop.")

        self.logger.info(" All Playwright resources have been closed and released.")