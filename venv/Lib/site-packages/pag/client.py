import re

import bs4

import fedora.client

from pag.utils import repo_url

class PagureException(Exception):
    pass


class Pagure(fedora.client.OpenIdBaseClient):
    def __init__(self, url='https://pagure.io', insecure=False):
        super(Pagure, self).__init__(
            base_url=url,
            login_url=url + "/login/",
            useragent="pag (cli)",
            debug=False,
            insecure=insecure,
            openid_insecure=insecure,
            username=None,  # We supply this later
            cache_session=True,
            retries=7,
            timeout=120,
            retry_backoff_factor=0.3,
        )

    @property
    def is_logged_in(self):
        response = self._session.get(self.base_url)
        return "logout" in response.text

    def create(self, name, description):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')
        url = self.base_url + '/new'
        response = self._session.get(url)
        if not bool(response):
            raise PagureException("Couldn't get form to get "
                                  "csrf token %r" % response)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        data = dict(
            csrf_token=soup.find(id='csrf_token').attrs['value'],
            name=name,
            description=description,
        )

        response = self._session.post(url, data=data)

        if not bool(response):
            del data['csrf_token']
            raise PagureException('Bad status code from pagure when '
                                  'creating project: %r.  Sent %r' % (
                                      response, data))
        return repo_url(name)

    def create_issue(self, repo, title, description, private=False):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')

        url = self.base_url + '/' + repo + '/new_issue'
        response = self._session.get(url)
        if not bool(response):
            raise PagureException("Couldn't get form to get "
                                  "csrf token %r" % response)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        data = {
            'csrf_token' : soup.find(id='csrf_token').attrs['value'],
            'title': title,
            'issue_content': description,
            'private': private
        }

        response = self._session.post(url, data=data)
        if not bool(response):
            del data['csrf_token']
            raise PagureException('Bad status code from pagure when '
                                  'forking project: %r.  Sent %r' % (
                                      response, data))

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        response_title = soup.title.string
        match = re.match(r'Issue #(?P<issue_id>\d+):.*', response_title)
        issue_id = match.group('issue_id')
        issue_url = self.base_url + '/' + repo + '/issue/' + issue_id
        return issue_url

    def upload(self, repo, filepath):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')

        url = self.base_url + '/' + repo + '/upload'
        response = self._session.get(url)
        if not bool(response):
            raise PagureException("Couldn't get form to get "
                                  "csrf token %r" % response)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        data = {
            'csrf_token': soup.find(id='csrf_token').attrs['value'],
        }
        files = {
            'filestream': open(filepath, 'rb')
        }
        response = self._session.post(url, data=data, files=files)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        alert = soup.find(class_="alert")
        if 'alert-info' in alert.attrs['class']:
            # Not an error -> the upload was successful.
            return None
        # Filter out only text elements from the alert (throwing away the close
        # button).
        text = ''.join(str(c) for c in alert.children
                       if isinstance(c, bs4.element.NavigableString))
        return text.strip()

    def fork(self, name):
        if not self.is_logged_in:
            raise PagureException('Not logged in.')

        url = self.base_url + '/' + name
        response = self._session.get(url)
        if not bool(response):
            raise PagureException("Couldn't get form to get "
                                  "csrf token %r" % response)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        data = dict(
            csrf_token=soup.find(id='csrf_token').attrs['value'],
        )

        url = self.base_url + '/do_fork/' + name
        response = self._session.post(url, data=data)

        if not bool(response):
            del data['csrf_token']
            raise PagureException('Bad status code from pagure when '
                                  'forking project: %r.  Sent %r' % (
                                      response, data))
        return repo_url(name)

    def submit_pull_request(self, name, base, head, title, comment):
        url = 'https://pagure.io/{name}/diff/{base}..{head}'
        url = url.format(name=name, base=base, head=head)

        response = self._session.get(url)
        if not bool(response):
            raise PagureException("Couldn't get form to get "
                                  "csrf token %r" % response)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        data = dict(
            csrf_token=soup.find(id='csrf_token').attrs['value'],
            branch_to=base,
            title=title,
            initial_comment=comment,
        )
        response = self._session.post(url, data=data)

        if not bool(response):
            del data['csrf_token']
            raise PagureException('Bad status code from pagure when '
                                  'creating pull request: %r.  Sent %r' % (
                                      response, data))

        return response.url


client = Pagure()
