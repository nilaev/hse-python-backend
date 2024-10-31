from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import NonNegativeInt, NonNegativeFloat, PositiveInt
from ....shop_api.store import item as store
from ...api.item.contracts import ItemRequest, ItemResponse, PatchItemRequest

router = APIRouter(prefix="/item")


@router.post("/", status_code=HTTPStatus.CREATED)
async def create_item(info: ItemRequest) -> ItemResponse:
    entity = store.add(info.as_item_info())
    return ItemResponse.from_entity(entity)


@router.get("/{id}", responses={
    HTTPStatus.OK: {"description": "Успешно вернули товар по id"},
    HTTPStatus.NOT_FOUND: {"description": "Товар не найден"}
})
async def get_item_by_id(id: int) -> ItemResponse:
    entity = store.get_one(id)
    if not entity:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Данные по запросу /item/{id} не найдены")
    return ItemResponse.from_entity(entity)


@router.get("/", responses={
    HTTPStatus.OK: {"description": "Успешно вернули список товаров"},
})
async def get_item_list(
        offset: Annotated[NonNegativeInt, Query()] = 0,
        limit: Annotated[PositiveInt, Query(lt=25)] = 10,
        min_price: Annotated[NonNegativeFloat, Query()] = None,
        max_price: Annotated[NonNegativeFloat, Query()] = None,
        show_deleted: Annotated[bool, Query()] = False,
) -> list[ItemResponse]:
    return [ItemResponse.from_entity(e) for e in
            store.get_many(offset, limit, min_price, max_price, show_deleted)]


@router.put("/{id}", responses={
    HTTPStatus.OK: {"description": "Товар успешно заменен"},
    HTTPStatus.NOT_MODIFIED: {"description": "Ошибка при замене товара"},
})
async def put_item(id: int, info: ItemRequest) -> ItemResponse:
    entity = store.update(id, info.as_item_info())
    if entity is None:
        raise HTTPException(HTTPStatus.NOT_MODIFIED, f"Не удалось найти /item/{id}")
    return ItemResponse.from_entity(entity)


@router.patch("/{id}", responses={
    HTTPStatus.OK: {"description": "Товар успешно частично обновлен"},
    HTTPStatus.NOT_MODIFIED: {"description": "Ошибка при частичном обновлении товара"},
    HTTPStatus.UNPROCESSABLE_ENTITY: {"description": "Некорректные данные"},
})
async def patch_item(id: int, info: PatchItemRequest) -> ItemResponse:
    if set(info.model_dump(exclude_none=True).keys()) - {'name', 'price'}:
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, "У товара должны быть только поля 'name' или 'price'")
    entity = store.patch(id, info.as_patch_item_info())
    if entity is None:
        raise HTTPException(HTTPStatus.NOT_MODIFIED, f"Не удалось найти /item/{id}")
    return ItemResponse.from_entity(entity)


@router.delete("/{id}", responses={
    HTTPStatus.OK: {"description": "Товар успешно частично обновлен"},
    HTTPStatus.NOT_FOUND: {"description": "Не удалось найти товар с таким id"},
})
async def delete_item(id: int) -> ItemResponse:
    entity = store.delete(id)
    if entity is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Не удалось найти /item/{id}")
    return ItemResponse.from_entity(entity)
