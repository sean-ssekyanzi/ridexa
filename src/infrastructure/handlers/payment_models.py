"""
Infrastructure handler layer dataclasses.
These models represent request payloads for the handler layer.
"""


from dataclasses import dataclass


@dataclass
class PayPalConfirm:
    order_id: str


@dataclass
class MomoRequest:
    phone: str
