from sqlalchemy.orm import Session


class BaseRepository:
    model = None
    def create(self, db: Session, model_class, **kwargs):
        obj = model_class(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj):
        db.delete(obj)
        db.commit()

    def get_all(self, db: Session,model_class, skip: int = 0, limit: int = 100):
        return db.query(model_class).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, model_class, id):
        return db.query(model_class).filter(model_class.id == id).first()

    def delete_by_id(self, db: Session, model_class, id: int):
        obj = self.get_by_id(db, model_class, id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

    def exists_by_field(self, db: Session, model_class, field_name, value) -> bool:
        field = getattr(model_class, field_name)
        return db.query(model_class).filter(field == value).first() is not None

