from __future__ import annotations

import argparse
from typing import List, Dict

from app.db.db_storage import DBStorage
from app.models.order import Order


DEFAULT_ORDERS: List[Dict[str, str]] = [
    {"order_id": "ORD-123ABC", "customer_email": "nuru@example.com", "status": "completed"},
    {"order_id": "ORD-456DEF", "customer_email": "bob@example.com", "status": "completed"},
    {"order_id": "ORD-789GHI", "customer_email": "carol@example.com", "status": "completed"},
    {"order_id": "INV-001-XYZ", "customer_email": "dave@example.com", "status": "completed"},
    {"order_id": "A1B2C3D4", "customer_email": "eve@example.com", "status": "completed"},
]


def upsert_order(db: DBStorage, data: Dict[str, str]) -> bool:
    existing = db.query(Order).filter(Order.order_id == data["order_id"]).first()
    if existing:
        mutated = False
        if data.get("customer_email") and existing.customer_email != data["customer_email"]:
            existing.customer_email = data["customer_email"]
            mutated = True
        if data.get("status") and existing.status != data["status"]:
            existing.status = data["status"]
            mutated = True
        if mutated:
            db.update(existing)
        return False
    db.add(Order(order_id=data["order_id"], customer_email=data.get("customer_email"), status=data.get("status", "completed")))
    return True


def main():
    parser = argparse.ArgumentParser(description="Seed demo orders into the database")
    parser.add_argument("--only", nargs="*", help="Specific order IDs to seed (otherwise defaults are used)")
    args = parser.parse_args()

    db = DBStorage()
    db.setup_db()
    try:
        to_seed: List[Dict[str, str]]
        if args.only:
            to_seed = [{"order_id": oid, "customer_email": f"{oid.lower()}@example.com", "status": "completed"} for oid in args.only]
        else:
            to_seed = DEFAULT_ORDERS

        created = 0
        updated = 0
        for data in to_seed:
            existed = not upsert_order(db, data)
            if existed:
                updated += 1
            else:
                created += 1

        print(f"Seed complete: created={created}, updated={updated}, total={created + updated}")
    finally:
        db.close()


if __name__ == "__main__":
    main()


