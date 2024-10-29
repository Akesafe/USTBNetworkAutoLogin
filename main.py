from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import yaml
import time
import os
import schedule
import logging
from datetime import datetime
import sys


class AutoLogin:
    def __init__(self, config_path='config.yaml', log_dir='logs'):
        """
        初始化自动登录类

        参数:
        config_path: 配置文件路径
        log_dir: 日志文件目录
        """
        self.config = self.load_config(config_path)
        self.driver = None


    def load_config(self, config_path):
        """
        加载配置文件
        """
        if not os.path.exists(config_path):
            default_config = {
                'username': '',
                'password': '',
                'headless': True,  # 定时任务建议使用无头模式
                'driver_path': 'driver/chromedriver.exe',
                'url': 'http://202.204.48.66',
                'login_success_text': '当前余额',  # 登录成功判定文本
                'auto_run': {  # 自动运行配置
                    'enabled': True,
                    'interval_hours': 2
                },
                'proxy': {
                    'enabled': False,
                    'type': 'socks5',
                    'host': '127.0.0.1',
                    'port': '8080'
                }
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, allow_unicode=True)
            logger.warning(f"找不到配置文件，已创建默认配置文件: {config_path}")
            return default_config

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def setup_proxy(self, chrome_options):
        """
        设置代理
        """
        proxy_config = self.config.get('proxy', {})
        if proxy_config.get('enabled', False):
            proxy_type = proxy_config.get('type', 'socks5')
            host = proxy_config.get('host', '127.0.0.1')
            port = proxy_config.get('port', '7890')

            proxy_string = f"{proxy_type}://{host}:{port}"
            chrome_options.add_argument(f'--proxy-server={proxy_string}')

            logger.info(f"使用代理: {proxy_string}")

            if proxy_type.startswith('socks'):
                chrome_options.add_argument("--disable-webrtc")

    def setup_driver(self):
        """
        设置并初始化WebDriver
        """
        chrome_options = Options()
        self.setup_proxy(chrome_options)

        if self.config.get('headless', True):
            logger.info("已使用无头模式，运行过程中不会显示浏览器界面。可以在config.yaml中修改")
            chrome_options.add_argument('--headless')
        else:
            logger.info("未使用无头模式，运行过程中会显示浏览器界面。可以在config.yaml中修改")

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--dns-prefetch-disable')

        service = Service(self.config['driver_path'])
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5)

    def test_proxy_connection(self):
        """
        测试代理连接是否正常
        """
        try:
            self.driver.get("http://httpbin.org/ip")
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"代理连接测试失败: {str(e)}")
            return False

    def is_logged_in(self):
        """
        检查是否已经登录
        """
        success_text = self.config.get('login_success_text', '当前余额')
        try:
            balance_element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{success_text}')]")
            return True
        except NoSuchElementException:
            return False

    def login(self):
        """
        执行登录流程
        """
        logger.info("开始执行登录流程")
        try:
            self.setup_driver()

            if self.config.get('proxy', {}).get('enabled', False):
                if not self.test_proxy_connection():
                    logger.error(
                        "代理连接测试失败，请检查代理设置，或将config.yaml中的proxy->enabled参数设置为false")
                    return False

            self.driver.get(self.config['url'])
            time.sleep(2)

            if self.is_logged_in():
                logger.info("已经登录完成！无需重复登录")
                return True

            # 最多尝试10次TAB切换来查找输入框
            for _ in range(10):
                active_element = self.driver.switch_to.active_element
                element_type = active_element.get_attribute('type')

                if element_type == 'text':
                    logger.info("已输入用户名")
                    active_element.send_keys(self.config['username'])
                    time.sleep(0.5)
                elif element_type == 'password':
                    logger.info("已输入密码")
                    active_element.send_keys(self.config['password'])
                    time.sleep(0.5)
                    active_element.send_keys(Keys.RETURN)
                    break

                active_element.send_keys(Keys.TAB)

            success_text = self.config.get('login_success_text', '当前余额')
            try:
                balance_text = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{success_text}')]"))
                )
                logger.info("登录成功！")
                time.sleep(2)
                return True

            except TimeoutException:
                logger.error(
                    f"登录失败：未能找到\"{success_text}\"文字，您可以将config.yaml文件中的headless参数设置为false并重新运行程序以查看登录过程")
                return False

        except Exception as e:
            logger.error(
                f"登录过程中发生错误: {str(e)}，您可以将config.yaml文件中的headless参数设置为false并重新运行程序以查看登录过程")
            return False

        finally:
            if self.driver:
                self.driver.quit()

def setup_logging(log_dir='logs'):
    """
    全局日志配置
    """
    # 创建日志目录
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 获取当前日期作为日志文件名
    log_file = os.path.join(log_dir, f'auto_login_{datetime.now().strftime("%Y%m%d")}.log')

    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

def job():
    """
    定时任务执行的函数
    """
    auto_login = AutoLogin()
    success = auto_login.login()


def run_scheduler():
    """
    运行定时调度器
    """
    # 读取配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    auto_run_config = config.get('auto_run', {'enabled': True, 'interval_hours': 2})

    if not auto_run_config.get('enabled', True):
        logging.info("自动运行已禁用，程序将在执行一次登录后退出")
        job()
        return

    job()  # 设置任务之前先首次运行一次

    interval_hours = auto_run_config.get('interval_hours', 2)
    schedule.every(interval_hours).hours.do(job)

    logging.info(f"定时任务已启动，将每{interval_hours}小时自动登录一次")

    while True:
        schedule.run_pending()
        time.sleep(interval_hours*60*60/5)  # 例如：设置为1小时运行间隔，则休眠时间为12分钟

if __name__ == "__main__":
    logger = setup_logging()

    logging.info("程序已启动！")
    run_scheduler()

'''
BY Akesafe.
'''
