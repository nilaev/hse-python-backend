from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ...store.item.models import ItemEntity, ItemInfo, PatchItemInfo


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def from_entity(entity: ItemEntity) -> ItemResponse:
        return ItemResponse(
            id=entity.id,
            name=entity.info.name,
            price=entity.info.price,
            deleted=entity.info.deleted,
        )


class ItemRequest(BaseModel):
    name: str | None
    deleted: bool = False
    price: float

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(name=self.name, price=self.price, deleted=self.deleted)

    def as_dict(self) -> dict:
        res = {}
        if self.name:
            res['name'] = self.name
        if self.price:
            res['price'] = self.price
        return res


class PatchItemRequest(BaseModel):
    name: str | None = None
    price: float | None = None

    model_config = ConfigDict(extra="forbid")

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)
