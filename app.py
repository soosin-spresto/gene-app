import os

import uvicorn

DEBUG = bool(os.getenv('DEBUG', False))

if __name__ == '__main__':
    reload = DEBUG
    uvicorn.run('api.main:app', host='0.0.0.0', port=8000, reload=reload)
