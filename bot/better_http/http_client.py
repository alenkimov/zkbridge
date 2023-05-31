import asyncio
from typing import Any, Optional, Union
from urllib.parse import quote as _uriquote

import aiohttp

from bot.logger import logger
from bot.utils import to_json
from .exceptions import HTTPException, Forbidden, NotFound, ServerError, Unauthorized


class RouteCreator:
    def __init__(self, base: str):
        self.base = base

    def __call__(self, method: str, path: str, **parameters: Any):
        return Route(method, self.base, path, **parameters)

    def __repr__(self):
        return f'<RouteCreator(base={self.base})>'


class Route:
    def __init__(self, method: str, base: str, path: str, **parameters: Any) -> None:
        self.base = base
        self.path: str = path
        self.method: str = method
        url = self.base + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url: str = url

    def __repr__(self):
        return f'<Route(method={self.method}, url={self.url})>'


class HTTPClient:
    """Represents an HTTP client sending HTTP requests."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        *,
        proxy: Optional[str] = None,
        proxy_auth: Optional[aiohttp.BasicAuth] = None,
    ) -> None:
        self._session = session
        self.proxy: Optional[str] = proxy
        self.proxy_auth: Optional[aiohttp.BasicAuth] = proxy_auth

    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url
        headers: dict[str, str] = dict()

        # some checking if it's a JSON request
        if 'json' in kwargs:
            headers['content-type'] = 'application/json'
            kwargs['data'] = to_json(kwargs.pop('json'))

        if 'headers' in kwargs:
            headers.update(kwargs['headers'])

        kwargs['headers'] = headers

        # Proxy support
        if self.proxy is not None:
            kwargs['proxy'] = self.proxy
        if self.proxy_auth is not None:
            kwargs['proxy_auth'] = self.proxy_auth

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[dict[str, Any], str]] = None
        for tries in range(5):
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    logger.debug(f'{method} {url} with {kwargs.get("data")} has returned {response.status}')

                    # even errors have text involved in them so this is safe to call
                    try:
                        data = await response.json(encoding='utf-8')
                    except aiohttp.ContentTypeError:
                        data = await response.text(encoding='utf-8')

                    # the request was successful so just return the text/json
                    if 300 > response.status >= 200:
                        logger.debug(f'{method} {url} has received {data}')
                        return data

                    # we've received a 500, 502, 504, or 524, unconditional retry
                    if response.status in {500, 502, 504, 524}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    # the usual error cases
                    if response.status == 401:
                        raise Unauthorized(response, data)
                    elif response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        raise NotFound(response, data)
                    elif response.status >= 500:
                        raise ServerError(response, data)
                    else:
                        raise HTTPException(response, data)

            # This is handling exceptions from the request
            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise

        if response is not None:
            # We've run out of retries, raise.
            if response.status >= 500:
                raise ServerError(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')
