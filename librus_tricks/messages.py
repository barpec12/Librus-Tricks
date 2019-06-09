from bs4 import BeautifulSoup
import requests


class Message:
    def __init__(self, url, parent_web_session, header=None, author=None):
        """

        :type url: str
        :type parent_web_session: requests.sessions.Session
        """
        self.web_session = parent_web_session
        self.url = url
        self.header = header
        self.author_alias = author

    def read(self):
        response = self.web_session.get('https://synergia.librus.pl' + self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find('div', attrs={'class': 'container-message-content'}).text

    def __repr__(self):
        return f'<Message from {self.author_alias} into {self.url}>'


class MessageReader:
    def __init__(self, username, password):
        self.web_session = requests.session()
        self.web_session.get('https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata')
        login_response = self.web_session.post('https://api.librus.pl/OAuth/Authorization?client_id=46', data={
            'action': 'login', 'login': username, 'pass': password
        })
        self.web_session.get('https://api.librus.pl' + login_response.json()['goTo'])

    def read_messages(self):
        response = self.web_session.get('https://synergia.librus.pl/wiadomosci')
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', attrs={'class': 'decorated stretch'})
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        messages = []
        for message in rows:
            cols = message.find_all('td')
            messages.append(Message(
                url=cols[3].a['href'],
                header=cols[3].text.strip(),
                author=cols[2].text.strip(),
                parent_web_session=self.web_session
            ))
        return messages
