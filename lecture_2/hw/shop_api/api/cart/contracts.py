from __future__ import annotations

from pydantic import BaseModel

from ...store.cart.models import CartEntity, CartItem


class CartItemResponse(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

    @staticmethod
    def from_entity(entity: CartItem) -> CartItemResponse:
        return CartItemResponse(
            id=entity.id,
            name=entity.name,
            quantity=entity.quantity,
            available=entity.available,
        )


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    price: float

    @staticmethod
    def from_entity(entity: CartEntity) -> CartResponse:
        return CartResponse(
            id=entity.id,
            items=[CartItemResponse.from_entity(item) for item in entity.info.items],
            price=entity.info.price,
        )
