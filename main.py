import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QSizePolicy, QLineEdit, QPushButton, QVBoxLayout, QWidget, QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5 import QtGui
import qdarkstyle

class AdBlockingPage(QWebEnginePage):
    def __init__(self, ad_domains):
        super().__init__()
        self.ad_domains = ad_domains

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if is_main_frame and nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            return True  # Allow normal navigation
        elif is_main_frame and nav_type == QWebEnginePage.NavigationTypeTyped:
            return True  # Allow manually typed URLs
        else:
            return self.block_ad_request(url)

    def block_ad_request(self, url):
        for ad_domain in self.ad_domains:
            if ad_domain in url.toString():
                return False  # Block the request
        return True  # Allow the request

class WebBrowser(QMainWindow):

    def __init__(self):
        super().__init__()

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.init_ui()

    def read_ad_domains_from_file(self, filename):
        ad_domains = []
        try:
            with open(filename, "r") as file:
                for line in file:
                    ad_domains.append(line.strip())
        except FileNotFoundError:
            print(f"File {filename} not found. No ad domains will be blocked.")
        return ad_domains

    def init_ui(self):
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowTitle("Daemon Search")
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setCentralWidget(self.tab_widget)
        self.setWindowIcon(QtGui.QIcon("mask.png"))

        self.setup_toolbar()

    def create_new_browser_instance(self, url=None):
        new_browser = QWebEngineView()
        new_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        new_browser.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        new_browser.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        new_browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
        new_browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, False)
        new_browser.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        new_browser.settings().setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        new_browser.setPage(AdBlockingPage(self.read_ad_domains_from_file("adservers.txt")))
        new_browser.titleChanged.connect(self.update_tab_name)

        if url:
            new_browser.setUrl(QUrl(url))
        else:
            new_browser.setUrl(QUrl("https://duckduckgo.com"))

        return new_browser

    def add_new_tab(self, url=None):
        new_browser = self.create_new_browser_instance(url)
        new_browser.titleChanged.connect(self.update_tab_name)  # Connect to the update_tab_name method of WebBrowser
        self.tab_widget.addTab(new_browser, "Loading...")

    # Add this method inside the WebBrowser class
    def update_tab_name(self, title):
        index = self.tab_widget.indexOf(self.sender())  # Use self.sender() to get the current browser
        if index != -1:
            self.tab_widget.setTabText(index, title)

    def setup_toolbar(self):
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.setStatusTip("Open a new tab")
        new_tab_btn.triggered.connect(self.add_new_tab)
        nav_toolbar.addAction(new_tab_btn)

        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Back to the previous page")
        back_btn.triggered.connect(self.navigate_back)
        nav_toolbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.setStatusTip("Forward to the next page")
        forward_btn.triggered.connect(self.navigate_forward)
        nav_toolbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload the page")
        reload_btn.triggered.connect(self.reload_page)
        nav_toolbar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go to the homepage")
        home_btn.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_btn)

        self.url_input = QLineEdit(self)
        self.url_input.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_input)

        go_btn = QPushButton("Search", self)
        go_btn.clicked.connect(self.navigate_to_url)
        nav_toolbar.addWidget(go_btn)

    def update_tab_name(self, title):
        index = self.tab_widget.currentIndex()
        if index != -1:
            self.tab_widget.setTabText(index, title)

    def close_tab(self, index):
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.removeTab(index)

    def navigate_back(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.back()

    def navigate_forward(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.forward()

    def reload_page(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.reload()

    def navigate_home(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("https://duckduckgo.com"))

    def navigate_to_url(self):
        url = self.url_input.text()
        if not url.startswith("http") and not url.startswith("https"):
            url = "https://" + url
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = WebBrowser()
    browser.show()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec_())
