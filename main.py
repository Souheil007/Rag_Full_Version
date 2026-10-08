"""Entry point for running the RAG application service."""

import uvicorn
from src.api.routes import create_app
from src.utils.helpers import get_logger, load_config

logger = get_logger(__name__)

config = load_config("config.yaml")
app = create_app(config)

if __name__ == "__main__":
    api_cfg = config.get("api", {})
    host = api_cfg.get("host", "0.0.0.0")
    port = api_cfg.get("port", 8000)
    reload = api_cfg.get("reload", True)

    logger.info(f"Starting RAG API server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=reload)
