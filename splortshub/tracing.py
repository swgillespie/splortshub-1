import beeline
from starlette.exceptions import HTTPException
from starlette.datastructures import Headers


# Thanks to https://gist.github.com/jcrist/b34f240d443b7902dc5b4e046fdf0c37
# for this code
class HoneycombMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Don't trace non http/websocket types
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        trace = beeline.start_trace(context=self.get_context(scope))

        status_code = None

        async def wrapper(response):
            nonlocal status_code
            if response["type"] == "http.response.start":
                status_code = response["status"]
            return await send(response)

        try:
            await self.app(scope, receive, wrapper)
        except HTTPException as exc:
            status_code = exc.status_code
            raise
        except Exception:
            status_code = 500
            raise
        finally:
            trace.add_context_field("response.status_code", status_code)
            beeline.finish_trace(trace)

    def get_context(self, scope):
        request_method = scope.get("method")
        if request_method:
            trace_name = f"starlette_http_{request_method.lower()}"
        else:
            trace_name = "starlette_http"

        headers = Headers(scope=scope)

        return {
            "name": trace_name,
            "type": "http_server",
            "request.host": headers.get("host"),
            "request.method": request_method,
            "request.path": scope.get("path"),
            "request.content_length": int(headers.get("content-length", 0)),
            "request.user_agent": headers.get("user-agent"),
            "request.scheme": scope.get("scheme"),
            "request.query": scope.get("query_string").decode("ascii"),
        }
