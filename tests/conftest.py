"""Shared pytest configuration for browser-based tests."""


def pytest_setup_options():
    """Chrome options for dash_duo: force a software WebGL context (SwiftShader).

    Neither WSL dev machines nor GitHub Actions runners have a GPU; without these
    flags headless Chrome silently fails to create any WebGL context and deck.gl
    never renders, making browser assertions meaningless.
    """
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("--use-gl=angle")
    options.add_argument("--use-angle=swiftshader")
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--disable-gpu-sandbox")
    return options
