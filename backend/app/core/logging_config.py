import logging
import json
import time
from fastapi import Request

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        # Add extra attributes from the record
        for key, val in record.__dict__.items():
            if key not in [
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "levelname", "levelno", "lineno", "module", "msecs",
                "message", "msg", "name", "pathname", "process", "processName",
                "relativeCreated", "stack_info", "thread", "threadName"
            ]:
                log_record[key] = val
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to avoid duplicate logs in some environments
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

api_logger = logging.getLogger("api")

async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        api_logger.info(
            f"Request {request.method} {request.url.path} completed in {duration:.4f}s with status {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": duration
            }
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        api_logger.error(
            f"Request {request.method} {request.url.path} failed: {str(e)}",
            exc_info=True,
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_seconds": duration
            }
        )
        raise e
