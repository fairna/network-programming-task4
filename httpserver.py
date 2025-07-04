import os
import uuid
from glob import glob
from datetime import datetime
import urllib.parse
import base64  
class HttpServer:
    def __init__(self):
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html'
        }

    def response(self, code=404, message='Not Found', message_body=bytes(), headers={}):
        date = datetime.now().strftime('%c')
        resp = [
            f"HTTP/1.0 {code} {message}\r\n",
            f"Date: {date}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(message_body)}\r\n"
        ]
        for key, value in headers.items():
            resp.append(f"{key}: {value}\r\n")
        resp.append("\r\n")

        response_headers = ''.join(resp)
        if not isinstance(message_body, bytes):
            message_body = message_body.encode()
        return response_headers.encode() + message_body

    def proses(self, data):
        lines = data.split("\r\n")
        request_line = lines[0]
        headers = [line for line in lines[1:] if line]
        method, path, *_ = request_line.split()

        if method == "GET":
            return self.http_get(path, headers)
        elif method == "POST":
            return self.http_post(path, headers, data)
        elif method == "DELETE":
            return self.http_delete(path)
        else:
            return self.response(405, "Method Not Allowed", "Only GET, POST, DELETE allowed.")

    def http_get(self, path, headers):
        directory = './'

        if path == '/':
            return self.response(200, 'OK', 'Welcome to the test web server', {})
        elif path == '/list':
            files = os.listdir(directory)
            return self.response(200, 'OK', '\n'.join(files), {'Content-Type': 'text/plain'})
        elif path == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})
        elif path == '/santai':
            return self.response(200, 'OK', 'Just relax!', {})

        filename = path.lstrip('/')
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            return self.response(404, 'Not Found', f"{filename} not found.")

        with open(file_path, 'rb') as f:
            content = f.read()

        ext = os.path.splitext(filename)[1]
        content_type = self.types.get(ext, 'application/octet-stream')
        return self.response(200, 'OK', content, {'Content-Type': content_type})


    def http_post(self, path, headers, data):
        if path != '/upload':
            return self.response(404, 'Not Found', 'Endpoint not found.')
    
        filename = None
        for h in headers:
            if h.lower().startswith("x-file-name:"):
                filename = h.split(":", 1)[1].strip()
    
        if not filename:
            return self.response(400, 'Bad Request', 'Filename header is required.')
    
        try:
            body_start = data.find("\r\n\r\n") + 4
            body = data[body_start:]
    
            # Decode base64 ke bytes
            file_bytes = base64.b64decode(body.encode('utf-8'))
    
            with open(filename, 'wb') as f:
                f.write(file_bytes)
    
            return self.response(200, 'OK', f"File '{filename}' uploaded successfully.")
        except Exception as e:
            return self.response(500, 'Internal Server Error', f"Error writing file: {e}")


    def http_delete(self, path):
        parsed = urllib.parse.urlparse(path)
        query = urllib.parse.parse_qs(parsed.query)
        filename = query.get('filename', [None])[0]

        if not filename:
            return self.response(400, 'Bad Request', 'No filename specified.')

        file_path = './' + filename
        if not os.path.exists(file_path):
            return self.response(404, 'Not Found', f"{filename} not found.")
        try:
            os.remove(file_path)
            return self.response(200, 'OK', f"{filename} deleted successfully.")
        except Exception as e:
            return self.response(500, 'Internal Server Error', str(e))
