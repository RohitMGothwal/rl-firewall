import sys
sys.path.insert(0, '.')
import uvicorn
from src.dashboard.app_complete import app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
