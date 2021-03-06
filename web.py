import tornado.ioloop
import tornado.web
import os

import private.logic as logic
from private.base import Backend, RequestHandler


class QueryHandler(RequestHandler):

    def get(self):
        cells_hash = self.get_argument("cells_hash")
        hashed_obj = self.application.backend._get_cache(cells_hash)
        self.write_json(hashed_obj)


class InitHandler(RequestHandler):

    def get(self):
        cells = logic.randomize_grid()
        cells_hash = self.application.backend.hash_cells(cells)

        self.write_json({
            "grid": cells,
            "cell_hash": cells_hash
        })

        solutions = logic.solve(cells)
        self.application.backend._set_cache(cells_hash, {"solutions": solutions}, expiry=1440)

class Application(tornado.web.Application):

    def __init__(self, path):
        self.backend = Backend.instance()
        tornado.web.Application.__init__(self, [
            (r"/init", InitHandler),
            (r"/solutions", QueryHandler),
            (r'/(.*\..*)', tornado.web.StaticFileHandler, {'path': path})
        ],
        autoreload=True)


def main():
    logic.tests()
    path = os.path.join(os.getcwd(), 'public')
    app = Application(path)
    app.listen(8888)
    Backend.instance().clean_cache(60)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
