# Railway entry point - imports from app package
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
