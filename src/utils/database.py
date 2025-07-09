from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified
from pprint import pprint

Base = declarative_base()

class PerformanceSheet(Base):
    __tablename__ = 'performance_sheets'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    referenceNumber = Column(String(255))
    data = Column(JSON)
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Database:
    def __init__(self, host, database, user, password):
        engine = create_engine(f'postgresql://{user}:{password}@{host}/{database}')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def create(self, reference_number, data):
        try:
            existing = self.get_by_reference_number(reference_number)
            if existing:
                record_id = existing['id']
                record = self.session.query(PerformanceSheet).filter_by(id=record_id).first()
                updated = False
                for k, v in data.items():
                    if k not in record.data or record.data[k] != v:
                        record.data[k] = v
                        updated = True
                if updated:
                    flag_modified(record, "data")
                    self.session.commit()
                return record_id
            else:
                record = PerformanceSheet(referenceNumber=reference_number, data=data)
                self.session.add(record)
                self.session.commit()
                return str(record.id)
        except Exception as e:
            self.session.rollback()
            raise e
    
    def delete(self, record_id):
        try:
            record = self.session.query(PerformanceSheet).filter_by(id=record_id).first()
            if record:
                self.session.delete(record)
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update(self, record_id, data_updates):
        try:
            record = self.session.query(PerformanceSheet).filter_by(id=record_id).first()
            if record:
                updated = False
                for k, v in data_updates.items():
                    if k not in record.data or record.data[k] != v:
                        record.data[k] = v
                        updated = True
                if updated:
                    flag_modified(record, "data")
                    self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def add_field(self, record_id, field_name, field_value):
        try:
            record = self.session.query(PerformanceSheet).filter_by(id=record_id).first()
            if record:
                record.data[field_name] = field_value
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def remove_field(self, record_id, field_name):
        try:
            record = self.session.query(PerformanceSheet).filter_by(id=record_id).first()
            if record and field_name in record.data:
                del record.data[field_name]
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_all(self):
        records = self.session.query(PerformanceSheet).all()
        return [
            {
                'id': str(record.id),
                'referenceNumber': record.referenceNumber,
                'data': record.data
            }
            for record in records
        ]
    
    def get_by_id(self, record_id):
        record = self.session.query(PerformanceSheet).filter_by(id=record_id).first()
        if record:
            return {
                'id': str(record.id),
                'referenceNumber': record.referenceNumber,
                'data': record.data
            }
        return None
    
    def get_by_reference_number(self, reference_number):
        record = self.session.query(PerformanceSheet).filter(PerformanceSheet.referenceNumber == reference_number).first()
        if record:
            return {
                'id': str(record.id),
                'referenceNumber': record.referenceNumber,
                'data': record.data
            }
        return None

_db_instance = None

def get_default_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(
            host="10.231.200.65:5432",
            database="coesco_test",
            user="cpec",
            password="password"
        )
    return _db_instance