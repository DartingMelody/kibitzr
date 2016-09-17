import logging
import time
from contextlib import contextmanager

from selenium import webdriver
from xvfbwrapper import Xvfb
from ..conf import settings


logger = logging.getLogger(__name__)


firefox_instance = {
    'xvfb_display': None,
    'driver': None,
}


def cleanup():
    """Must be called before exit"""
    global firefox_instance
    if firefox_instance['driver'] is not None:
        firefox_instance['driver'].quit()
    if firefox_instance['xvfb_display'] is not None:
        firefox_instance['xvfb_display'].stop()


def firefox_fetcher(conf):
    url = conf['url']
    delay = conf.get('delay')
    scenario = conf.get('scenario')
    with firefox() as driver:
        driver.get(url)
        if scenario:
            run_scenario(driver, scenario)
        if delay:
            time.sleep(delay)
        html = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
        return True, html


@contextmanager
def firefox():
    global firefox_instance
    if firefox_instance['xvfb_display'] is None:
        firefox_instance['xvfb_display'] = virtual_buffer()
    if firefox_instance['driver'] is None:
        firefox_instance['driver'] = webdriver.Firefox()
    yield firefox_instance['driver']


def virtual_buffer():
    """
    Try to start xvfb, trying multiple (up to 5) times if a failure
    """
    for i in range(0, 6):
        xvfb_display = Xvfb()
        xvfb_display.start()
        # If Xvfb started, return.
        if xvfb_display.proc is not None:
            return xvfb_display
    raise Exception("Xvfb could not be started after six attempts.")


def run_scenario(driver, code):
    logger.info("Executing custom scenario")
    logger.debug(code)
    exec(code, {'driver': driver, 'creds': settings().creds})