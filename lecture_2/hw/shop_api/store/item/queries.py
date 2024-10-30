from typing import Iterable

from .models import (ItemInfo, ItemEntity, PatchItemInfo)

_data = dict[int, ItemEntity]()


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


_id_generator = int_id_generator()


def add(info: ItemInfo) -> ItemEntity:
    _id = next(_id_generator)
    _data[_id] = ItemEntity(_id, info)
    return _data[_id]


def delete(id: int) -> ItemEntity | None:
    if id not in _data:
        return None
    _data[id].info.deleted = True
    return _data[id]


def get_one(id: int) -> ItemEntity | None:
    if id not in _data or _data[id].info.deleted:
        return None
    return _data[id]


def get_many(offset: int = 0,
             limit: int = 10,
             min_price: float | None = None,
             max_price: float | None = None,
             show_deleted: bool | None = False) -> list[ItemEntity]:
    filtered_entities = []

    for id, item in _data.items():
        info = item.info
        # Проверка на фильтрацию по цене
        if (min_price is not None and info.price < min_price) or (max_price is not None and info.price > max_price):
            continue

        # Проверка на фильтрацию удаленных товаров
        if show_deleted or not info.deleted:
            continue

        # Если корзина проходит все фильтры, добавляем её
        filtered_entities.append(ItemEntity(id, info))
    return filtered_entities[offset: offset + limit]


def update(id: int, info: ItemInfo) -> ItemEntity | None:
    if id not in _data:
        return None
    _data[id].info = info
    return _data[id]


def patch(id: int, patch_info: PatchItemInfo) -> ItemEntity | None:
    if id not in _data or _data[id].info.deleted:
        return None

    if patch_info.name is not None:
        _data[id].info.name = patch_info.name

    if patch_info.price is not None:
        _data[id].info.price = patch_info.price

    return _data[id]
