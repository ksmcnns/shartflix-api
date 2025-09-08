import logging
import sys
import requests
from http.client import HTTPConnection

# Loglama ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# HTTP istemci log seviyesini ayarla (isteğe bağlı, daha fazla detay için)
HTTPConnection.debuglevel = 1

# Loglama için özel bir formatter
class HttpFormatter(logging.Formatter):
    def _format_headers(self, d):
        return '\n'.join(f'{k}: {v}' for k, v in d.items())

    def formatMessage(self, record):
        result = super().formatMessage(record)
        if record.name == 'httplogger':
            extra = getattr(record, 'extra', {})
            req = extra.get('req')
            res = extra.get('res')
            if req and res:
                result += f"\n---------------- request ----------------\n{req.method} {req.url}\n{self._format_headers(req.headers)}\n{req.body}\n"
                result += f"---------------- response ----------------\n{res.status_code} {res.reason}\n{res.url}\n{self._format_headers(res.headers)}\n{res.text}"
        return result

# Log handler ve formatter ekle
logger = logging.getLogger('httplogger')
formatter = HttpFormatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Örnek bir sunucu simülasyonu (API endpoint’ini buraya entegre et)
def handle_request():
    session = requests.Session()
    session.hooks['response'].append(lambda r, *args, **kwargs: logger.debug('HTTP roundtrip', extra={'req': r.request, 'res': r}))

    try:
        # Kayıt endpoint’ine örnek istek (Flutter’dan gelen ile eşleşmeli)
        response = session.post(
            'http://your-server-address/api/register',  # Backend URL’nizi buraya koyun
            json={'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'},
            headers={'Authorization': 'Bearer your-token-here'}  # Gerekirse token ekleyin
        )
        response.raise_for_status()  # Hata varsa exception fırlatır
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return False
    return True

if __name__ == "__main__":
    handle_request()