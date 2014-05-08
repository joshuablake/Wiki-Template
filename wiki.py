from cookielib import CookieJar
import json
import logging
import urllib
import urllib2
logger = logging.getLogger(__name__)

class RequestError(Exception):
    pass

class Wiki(object):
    def __init__(self, url, delay):
        self._url = url
        self.delay = delay
        self.logged_in = False
    
    def _build_url(self, action, **params):
        return '{}/w/api.php?action={}&{}'.format(
                self._url, action,
                '&'.join('{}={}'.format(k, v) for k, v in params.iteritems()))
        
    def _make_request(self, action, post=False, **kwargs):
        if post:
            kwargs['format'] = 'json'
            request = urllib2.Request(self._build_url(action), urllib.urlencode(kwargs.items()))
        else:
            request = urllib2.Request(self._build_url(action, format='json', **kwargs))
        logger.debug('Fetching from wiki: '+request.get_full_url())
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            logger.warning('Error code %s for page %s response was %s',
                      e.code, request.get_full_url(), e.read())
            raise
        return json.load(response)
    
    def login(self, username, password, token=''):
        urllib2.install_opener(urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar())))
        response = self._make_request('login', post=True, lgname=username, lgpassword=password)
        if response['login']['result'] == 'NeedToken':
            response = self._make_request('login', post=True, lgname=username, lgpassword=password,
                                          lgtoken=response['login']['token'])
        result = response['login']['result']
        if not result == 'Success':
            raise RequestError('Invalid login: {}'.format(result))
        self._edit_token = False
        self.logged_in = True
    
    def pages_by_category(self, category, get_subcategories):
        """Get pages from wiki in raw wikitext format
    
        Args:
            pages (list): pages to get
            pause (int): seconds to pause between queries to wiki
        Returns:
            (dict): format of {page: content}
        
        """
        if not category.startswith('Category:'):
            category = 'Category:'+category
        cmtype = 'page'
        if get_subcategories:
            cmtype += '|subcat'
        response = self._make_request(
            'query',
            list='categorymembers',
            cmtitle=category,
            cmprop='title|type',
            cmtype=cmtype,
        )
        pages = []
        subcategories = []
        for member in response['query']['categorymembers'].values():
            if member['type'] == 'page':
                pages.append(member['title'])
            elif member['type'] == 'subcat':
                subcategories.append(member['title'])
            else:
                logger.warning('Unknown type %s of name %s',
                               member['type'], member['title']
                )
        return subcategories, pages
