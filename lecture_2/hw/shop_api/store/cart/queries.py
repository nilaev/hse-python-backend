from typing import Iterable

from .models import (CartInfo, CartEntity, CartItem)
from ..item import ItemEntity

_data = dict[int, CartEntity]()


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


_id_generator = int_id_generator()


def add(info: CartInfo) -> CartEntity:
    _id = next(_id_generator)
    _data[_id] = CartEntity(_id, info)
    return _data[_id]


def get_one(id: int) -> CartEntity | None:
    if id not in _data:
        return None
    return _data[id]


def get_many(offset: int = 0,
             limit: int = 10,
             min_price: float | None = None,
             max_price: float | None = None,
             min_quantity: int | None = None,
             max_quantity: int | None = None) -> list[CartEntity]:
    filtered_entities = []

    for id, item in _data.items():
        info = item.info
        # Проверка на фильтрацию по цене
        if (min_price is not None and info.price < min_price) or (max_price is not None and info.price > max_price):
            continue

        # Проверка на фильтрацию по количеству
        total_quantity = sum(item.quantity for item in info.items)
        if (min_quantity is not None and total_quantity < min_quantity) or (
                max_quantity is not None and total_quantity > max_quantity):
            continue

        # Если корзина проходит все фильтры, добавляем её
        filtered_entities.append(CartEntity(id, info))
    return filtered_entities[offset: offset + limit]


def add_item(id: int, item: ItemEntity) -> CartEntity:
    _data[id].info.items.append(CartItem(item.id, item.info.name, 1, True))
    _data[id].info.price += item.info.price
    return _data[id]


def increment_item_quantity(id: int, item: ItemEntity) -> CartEntity:
    cart_item = next((ci for ci in _data[id].info.items if ci.id == item.id), None)
    if cart_item:
        cart_item.quantity += 1
        _data[id].info.price += item.info.price
    return _data[id]
