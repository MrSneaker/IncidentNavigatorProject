from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import datetime
from uuid import uuid4
from typing import List

from ... import db

def get_uuid():
    return uuid4().hex


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    message_id = db.Column(db.String(32), db.ForeignKey('messages.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    # Content
    accident_id = db.Column(db.Integer, nullable=False)
    event_type = db.Column(db.String(32), nullable=False)
    industry_type = db.Column(db.String(32), nullable=False)
    title = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(7), nullable=False)  # hex color
    
    def __repr__(self):
        return f'<Ticket {self.ticket_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'created_at': self.created_at,
            'accident_id': self.accident_id,
            'event_type': self.event_type,
            'industry_type': self.industry_type,
            'title': self.title,
            'url': self.url,
            'color': self.color
        }

    def save(self):
        db.session.add(self)
        db.session.commit()


class Message(db.Model):
    # Source values
    SOURCE_MODEL = False
    SOURCE_USER = True
    
    # Status values
    STATUS_ERROR = -1
    STATUS_PENDING = 0
    STATUS_SUCCESS = 1
    
    # Table
    __tablename__ = 'messages'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.String(32), db.ForeignKey('chats.id'), nullable=False)
    source = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    tickets = db.relationship('Ticket', backref='message', lazy=True)
    status = db.Column(db.Integer, default=0, nullable=False)
    
    def list_tickets(self) -> List[Ticket]:
        return Ticket.query.filter_by(message_id=self.id).all()
        
    def __repr__(self):
        return f'<Message {self.message}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'source': self.source,
            'message': self.message,
            'status': self.status,
            'tickets': [ticket.to_dict() for ticket in self.list_tickets()],
            'created_at': self.created_at
        }
    
    
    def save(self):
        db.session.add(self)
        db.session.commit()


class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.Text, nullable=False, default='New Chat')
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def __repr__(self):
        return f'<Chat {self.message}>'
    
    @staticmethod
    def create(user_id: str, name: str) -> 'Chat | None':
        if not user_id:
            return None
        if not name:
            name = 'New Chat'
        chat = Chat(user_id=user_id, name=name)
        db.session.add(chat)
        db.session.commit()
        return chat

    def delete(self) -> bool:
        messages = Message.query.filter_by(chat_id=self.id).all()
        for message in messages:
            db.session.delete(message)
        db.session.delete(self)
        db.session.commit()
        return True

    @staticmethod
    def list(user_id: str) -> List['Chat']:
        return Chat.query.filter_by(user_id=user_id).all() if user_id else []

    @staticmethod
    def get(user_id: str, chat_id: str) -> 'Chat | None':
        return Chat.query.filter_by(user_id=user_id, id=chat_id).first() if user_id and chat_id else None

    def rename(self, name) -> bool:
        if not name:
            return False
        self.name = name
        self.updated_at = datetime.datetime.now()
        db.session.commit()
        return True
    
    def messages(self) -> List[Message]:
        return Message.query.filter_by(user_id=self.user_id, chat_id=self.id).all()
    
    def add_message(self, msg: Message | dict) -> bool:
        if isinstance(msg, dict):
            msg = Message(**msg)
            
        if msg.chat_id != self.id:
            return False
        msg.chat_id = self.id
        msg.user_id = self.user_id
        db.session.add(msg)
        db.session.commit()
        return True
    
    def remove_message(self, msg: Message | str) -> bool:
        if isinstance(msg, str):
            msg = Message.query.get(msg)
        if msg.chat_id != self.id:
            return False
        
        db.session.delete(msg)
        db.session.commit()
        return True
    
    def history(self):
        return [
            {'role': 'user' if message.source else 'model', 'parts': message.message}
            for message in self.messages()
        ]
        
    def last_updated(self):
        msgs = self.messages()
        last_updated = self.updated_at
        for msg in msgs:
            if msg.created_at > last_updated:
                last_updated = msg.created_at
        return last_updated

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': int(self.created_at.timestamp() * 1000),
            'modified_at': int(self.last_updated().timestamp() * 1000),
        }
