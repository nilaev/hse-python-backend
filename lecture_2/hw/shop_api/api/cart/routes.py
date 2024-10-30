from http import HTTPStatus
from typing import Annotated
from urllib.request import Request

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, NonNegativeFloat, PositiveInt

from ...store.cart import CartInfo
from ....shop_api.store import cart as store_cart
from ....shop_api.store import item as store_item
from .contracts import (CartResponse)

router = APIRouter(prefix="/cart")


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_cart(response: Response):
    entity = store_cart.add(CartInfo([], 0))
    response.headers["location"] = f"/cart/{entity.id}"
    return CartResponse.from_entity(entity)


@router.get("/{id}", responses={
    HTTPStatus.OK: {"description": "Успешно вернули корзину по id"},
    HTTPStatus.NOT_FOUND: {"description": "Корзина не найдена"}
})
async def get_cart_by_id(id: int) -> CartResponse:
    entity = store_cart.get_one(id)
    if not entity:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Данные по запросу /cart/{id} не найдены")
    return CartResponse.from_entity(entity)


@router.get("/", responses={
    HTTPStatus.OK: {"description": "Успешно вернули список корзин"},
})
async def get_cart_list(
        offset: Annotated[NonNegativeInt, Query()] = 0,
        limit: Annotated[PositiveInt, Query(lt=25)] = 10,
        min_price: Annotated[NonNegativeFloat, Query()] = None,
        max_price: Annotated[NonNegativeFloat, Query()] = None,
        min_quantity: Annotated[NonNegativeInt, Query()] = None,
        max_quantity: Annotated[NonNegativeInt, Query()] = None,
) -> list[CartResponse]:
    return [CartResponse.from_entity(e) for e in
            store_cart.get_many(offset, limit, min_price, max_price, min_quantity, max_quantity)]


@router.post('/{cart_id}/add/{item_id}', responses={
    HTTPStatus.OK: {"description": "Товар успешно добавлен в корзину"},
    HTTPStatus.NOT_FOUND: {"description": "Не удалось найти элементы"}
})
async def add_cart_item(cart_id: int, item_id: int):
    cart = store_cart.get_one(cart_id)
    if not cart:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Не удалось найти /cart/{cart_id}")
    item = store_item.get_one(item_id)
    if not item:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Не удалось найти /item/{item_id}")
    if item_id not in map(lambda x: x.id, cart.info.items):
        entity = store_cart.add_item(cart_id, item)
        return CartResponse.from_entity(entity)
    entity = store_cart.increment_item_quantity(cart_id, item)
    return CartResponse.from_entity(entity)
