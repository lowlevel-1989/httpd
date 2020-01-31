import json
import uuid

from http import server
from http import HTTPStatus


class SimpleHttpRequestHandler(server.BaseHTTPRequestHandler):

    def __init__(self, resource, *args, **kwargs):
        self.resource = str(resource)

        super().__init__(*args, **kwargs)

    def has_resource_permission(self):

        resource = self.path[1:]

        if resource[-1:] == '/':
            resource = resource[:-1]

        return resource == self.resource

    def do_POST(self):
        l = self.headers.get('Content-Length')

        self._json = json.loads(self.rfile.read(int(l)))

        if not self.has_resource_permission():
            return self.send_response(HTTPStatus.UNAUTHORIZED)

        self.send_response(HTTPStatus.OK)
        self.server.shutdown()
        # logic here

    def send_response(self, *args, **kwargs):

        super().send_response(*args, **kwargs)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def log_request(self, code='-', size='-'):
        """Log an accepted request.

        This is called by send_response().

        """
        if isinstance(code, HTTPStatus):
            code = code.value
        self.log_message('"%s" %s %s %s',
                         self.requestline, str(code),
                         str(size), self._json)


class HTTPServer(server.ThreadingHTTPServer):

    def __init__(self, resource, *args, **kwargs):
        self.resource = resource

        super().__init__(*args, **kwargs)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(self.resource, request, client_address, self)


if __name__ == '__main__':
    httpd = HTTPServer(uuid.uuid4(), ('', 8000), SimpleHttpRequestHandler)

    print('server resource: {addr}:{port}/{resource}/'.format(**{
        'addr': httpd.server_name,
        'port': httpd.server_port,
        'resource': httpd.resource}))

    httpd.serve_forever()
