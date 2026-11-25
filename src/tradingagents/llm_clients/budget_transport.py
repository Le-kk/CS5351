"""Meter actual synchronous SDK HTTP attempts, shared by both model tiers.

Bound tools/structured parsers cannot bypass this seam. Async is explicitly
unsupported in this first call-cap profile and fails before network access.
"""
from __future__ import annotations

import asyncio
import importlib
from concurrent.futures import ThreadPoolExecutor

from openai import DefaultHttpxClient

from tradingagents.runapi.budget import BudgetProtocolError

# Use the SDK's public client's native transport family (SDK 2=httpx, 3=httpx2).
_transport_family = next((base.__module__.split(".")[0] for base in DefaultHttpxClient.__mro__
                          if base.__module__.split(".")[0] in {"httpx", "httpx2"}), None)
if _transport_family is None:
    raise RuntimeError("Unsupported SDK HTTP client family for call-cap metering")
http = importlib.import_module(_transport_family)


class BudgetStream(http.SyncByteStream):
    def __init__(self, stream, controller):
        self.stream, self.controller = stream, controller
        self.closed = False

    def __iter__(self):
        yield from self.stream

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                self.stream.close()
            finally:
                self.controller.finish()


class BudgetTransport(http.BaseTransport):
    def __init__(self, controller, transport=None):
        self.controller = controller
        self.transport = transport if transport is not None else http.HTTPTransport(retries=0)

    def handle_request(self, request):
        ticket = self.controller.reserve()
        try:
            self.controller.dispatch(ticket)
        except BaseException:
            self.controller.invalidate(ticket)
            raise
        try:
            response = self.transport.handle_request(request)
            if response.is_closed:
                self.controller.finish()
            else:
                response.stream = BudgetStream(response.stream, self.controller)
            return response
        except BaseException:
            self.controller.finish()
            raise

    def close(self):
        self.transport.close()


class RefuseAsyncTransport(http.AsyncBaseTransport):
    async def handle_async_request(self, request):
        raise BudgetProtocolError("Async model calls are unsupported in call_cap mode")


def budget_http_clients(controller):
    def build():
        sync = http.Client(transport=BudgetTransport(controller), follow_redirects=False,
                           timeout=600.0)
        asynchronous = http.AsyncClient(transport=RefuseAsyncTransport(), follow_redirects=False)

        def close():
            sync.close()
            # This profile's async transport never opens sockets; close on a separate
            # loop even when the synchronous app was called from an event-loop host.
            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(lambda: asyncio.run(asynchronous.aclose())).result()
        return sync, asynchronous, close
    sync, asynchronous, _close = controller.resources(build)
    return sync, asynchronous
