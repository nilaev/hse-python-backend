from dataclasses import dataclass


@dataclass(slots=True)
class CartItem:
    id: int
    name: str
    quantity: int
    available: bool


@dataclass(slots=True)
class CartInfo:
    items: list[CartItem]
    price: float


@dataclass(slots=True)
class CartEntity:
    id: int
    info: CartInfo
