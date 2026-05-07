from typing import List

from sqlalchemy import select, or_, func, and_
from datetime import date, timedelta

from src.database.models import Contact, User
from src.schemas.contacts import ContactModel, ContactUpdate


class ContactRepository:
    def __init__(self, session):
        self.db = session

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        user: User,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> List[Contact]:
        stmt = select(Contact).where(Contact.user_id == user.id)

        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
        today = date.today()
        seven_days_later = today + timedelta(days=7)

        today_str = today.strftime("%m-%d")
        end_date_str = seven_days_later.strftime("%m-%d")

        db_month_day = func.to_char(Contact.birth_date, "MM-DD")

        if today_str <= end_date_str:
            stmt = select(Contact).where(
                and_(Contact.user_id == user.id, db_month_day >= today_str, db_month_day <= end_date_str)
            )
        else:
            stmt = select(Contact).where(
                and_(Contact.user_id == user.id, or_(db_month_day >= today_str, db_month_day <= end_date_str))
            )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        stmt = select(Contact).where(and_(Contact.id == contact_id, Contact.user_id == user.id))
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contact_by_email_or_phone(
        self, email: str, phone: str, user: User
    ) -> Contact | None:
        stmt = select(Contact).where(
            and_(Contact.user_id == user.id, or_(Contact.email == email, Contact.phone == phone))
        )
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        contact_obj = await self.get_contact_by_id(contact_id, user)

        if not contact_obj:
            return None

        update_data = body.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(contact_obj, key, value)

        await self.db.commit()
        await self.db.refresh(contact_obj)

        return contact_obj

    async def delete_contact(self, contact_id: int, user: User) -> Contact | None:
        contact_obj = await self.get_contact_by_id(contact_id, user)

        if contact_obj:
            await self.db.delete(contact_obj)
            await self.db.commit()

        return contact_obj
