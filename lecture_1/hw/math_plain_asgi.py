from typing import Any, Awaitable, Callable
import json
import math
from urllib.parse import parse_qs


# Обработка запросов
async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    method = scope["method"]
    path = scope["path"]
    if method != "GET":
        await error(send, 404, "Not Found")
    else:
        if path == "/factorial":
            await factorial(scope, receive, send)
        elif path.startswith("/fibonacci"):
            await fibonacci(scope, receive, send)
        elif path == "/mean":
            await mean(scope, receive, send)
        else:
            await error(send, 404, "Not Found")


# Вывод результата
async def result(send, message):
    await send_response(send, 200, {"result": message})


async def error(send, error_code, message):
    await send_response(send, error_code, {"error": message})


async def send_response(send, code, data):
    await send({
        "type": "http.response.start",
        "status": code,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({
        "type": "http.response.body",
        "body": json.dumps(data).encode(),
    })


# Факториал числа n
def notIsDigit(s):
    if s.startswith("-"):
        s = s[1:]
    return not s.isdigit()


async def factorial(scope, receive, send):
    param = parse_qs(scope["query_string"].decode()).get("n")
    if not param or len(param) < 0 or notIsDigit(param[0]):
        await error(send, 422, param)
        return
    n = int(param[0])
    if n < 0:
        await error(send, 400, "Bad Request")
        return
    await result(send, math.factorial(n))


# N-ое число фибоначчи
def count_fibonacci(n):
    if n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return count_fibonacci(n - 1) + count_fibonacci(n - 2)


async def fibonacci(scope, receive, send):
    path = scope["path"].split("/")
    if notIsDigit(path[-1]):
        await error(send, 422, "Unprocessable Entity")
        return
    n = int(path[-1])
    if n < 0:
        await error(send, 400, "Bad Request")
        return
    await result(send, count_fibonacci(n))


# Среднее массива
async def mean(scope, receive, send):
    request = await receive()
    body = request["body"].decode("utf-8")

    if not body:
        await error(send, 422, "Unprocessable Entity")
        return
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        await error(send, 422, "Unprocessable Entity")
        return

    if not isinstance(data, list):
        await error(send, 422, "Unprocessable Entity")
        return

    if len(data) < 1:
        await error(send, 400, "Bad Request")
        return

    arr_sum = 0
    for x in data:
        if not isinstance(x, float) and not isinstance(x, int):
            await error(send, 422, "Unprocessable Entity")
            return
        arr_sum += x

    await result(send, arr_sum / len(data))
