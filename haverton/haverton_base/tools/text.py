from bs4 import BeautifulSoup


def get_html_plain_text(html):
    html_str = str(html)
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text()
