import asyncio
from aiohttp import web
from aiohttp.web import Response
from async_requsts import main  # Импортируем вашу основную функцию
import os

async def handle(request):
    await main(request)
    return Response(text="Data has been inserted successfully!")

def run_app():
    app = web.Application()
    app.router.add_get('/fetch', handle)  # Определяем маршрут для получения данных
    web.run_app(app)

if __name__ == '__main__':
    run_app()