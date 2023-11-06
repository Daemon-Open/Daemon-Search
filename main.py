import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QSizePolicy, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt5 import QtGui
import qdarkstyle
import os

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

        self.ad_blocker_profile = None
        self.browser = QWebEngineView()
        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)  # Enable JavaScript
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)  # Disable local storage
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls,
                              False)  # Limit local content access to remote URLs
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)  # Disable plugins
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)  # Disable pop-up windows
        settings.setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)  # Enable XSS auditing

        self.init_ui()

    def init_ui(self):
        self.browser.setUrl(QUrl("https://duckduckgo.com/"))
        print("Init UI - Default homepage URL:", self.browser.url().toString())
        self.setGeometry(100, 100, 1024, 768)
        self.setWindowTitle("Daemon Search")
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setup_toolbar()
        self.setup_main_widget()
        self.centralWidget().setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.browser.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.browser.page().setBackgroundColor(QtGui.QColor(30, 30, 30))  # Set the background color
        
        # Read ad domains from the text file and store them in a list
        self.ad_domains = self.read_ad_domains_from_file("adservers.txt")

        self.page = AdBlockingPage(self.ad_domains)
        self.browser.setPage(self.page)

    def setup_toolbar(self):
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)

        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Back to the previous page")
        back_btn.triggered.connect(self.browser.back)
        nav_toolbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.setStatusTip("Forward to the next page")
        forward_btn.triggered.connect(self.browser.forward)
        nav_toolbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload the page")
        reload_btn.triggered.connect(self.browser.reload)
        nav_toolbar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go to the homepage")
        home_btn.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_btn)

        self.url_input = QLineEdit(self)
        self.url_input.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_input)

        go_btn = QPushButton("Go", self)
        go_btn.clicked.connect(self.navigate_to_url)
        nav_toolbar.addWidget(go_btn)

    def setup_main_widget(self):
        main_widget = QWidget(self)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.browser)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def read_ad_domains_from_file(self, filename):
        ad_domains = []
        try:
            with open(filename, "r") as file:
                for line in file:
                    ad_domains.append(line.strip())
        except FileNotFoundError:
            print(f"File {filename} not found. No ad domains will be blocked.")
        return ad_domains

    def navigate_home(self):
        self.browser.setUrl(QUrl("https://duckduckgo.com/"))

    def navigate_to_url(self):
        url = self.url_input.text()
        if not url.startswith("http") and not url.startswith("https"):
            url = "https://" + url
        self.browser.setUrl(QUrl(url))

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("mask.png"))
    browser = WebBrowser()
    browser.show()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()