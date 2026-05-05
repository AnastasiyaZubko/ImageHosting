from base_handler import BaseHandler
import multipart


class ImageHostingHandler(BaseHandler):


    def do_GET(self):
        if self.path == '/':
            self.template_response('index.html')
        elif self.path == '/upload':
            self.template_response('upload.html')
        elif self.path == '/images':
            self.template_response('images.html')
        elif any((self.path.endswith(ext) for ext in ['.css', '.js', '.png'])):
            self.send_file(self.path)
        else:
            self.html_response('Not Found', 400)

    def do_POST(self):
        if self.path == '/api/upload':
            self.upload_file()
        else:
            self.html_response('Not Found', 400)





