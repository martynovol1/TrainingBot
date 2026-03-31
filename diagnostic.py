import socket
import ssl
import asyncio
import traceback

BOT_TOKEN = "8674086302:AAEjyxagk8ItImEvqREgq7Uy-k1NAQh-hnQ"


def test_dns():
    print("\n[1] Проверка DNS...")
    try:
        ip = socket.gethostbyname("api.telegram.org")
        print(f"OK: api.telegram.org -> {ip}")
    except Exception as e:
        print("DNS ОШИБКА:", repr(e))


def test_ssl():
    print("\n[2] Проверка SSL-соединения...")
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("api.telegram.org", 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="api.telegram.org") as ssock:
                print("OK: SSL handshake выполнен")
                print("TLS version:", ssock.version())
    except Exception as e:
        print("SSL ОШИБКА:", repr(e))
        traceback.print_exc()


def test_requests():
    print("\n[3] Проверка requests...")
    try:
        import requests

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        r = requests.get(url, timeout=15)
        print("HTTP status:", r.status_code)
        print("Ответ:", r.text[:500])
    except Exception as e:
        print("REQUESTS ОШИБКА:", repr(e))
        traceback.print_exc()


async def test_aiohttp():
    print("\n[4] Проверка aiohttp...")
    try:
        import aiohttp

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                print("HTTP status:", resp.status)
                text = await resp.text()
                print("Ответ:", text[:500])
    except Exception as e:
        print("AIOHTTP ОШИБКА:", repr(e))
        traceback.print_exc()


def test_proxy_env():
    print("\n[5] Проверка переменных прокси...")
    import os

    proxy_vars = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
        "NO_PROXY",
        "no_proxy",
    ]

    found = False
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            found = True
            print(f"{var} = {value}")

    if not found:
        print("OK: proxy-переменные не найдены")


async def main():
    print("=== Диагностика Telegram API ===")
    test_dns()
    test_ssl()
    test_proxy_env()
    test_requests()
    await test_aiohttp()
    print("\n=== Диагностика завершена ===")


if __name__ == "__main__":
    asyncio.run(main())