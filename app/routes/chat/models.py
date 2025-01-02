from flask_sqlalchemy import SQLAlchemy
import datetime
from uuid import uuid4

from .. import db

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

    
    def get_message(self):
        return Message.query.get(self.message_id)
    
    def get_chat(self):
        return self.get_message().get_chat()
    
    def save(self):
        db.session.add(self)
        db.session.commit()


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.String(32), db.ForeignKey('chats.id'), nullable=False)
    source = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    tickets = db.relationship('Ticket', backref='message', lazy=True)
    status = db.Column(db.Integer, default=0, nullable=False)
    
    def list_tickets(self):
        return [ticket.to_dict() for ticket in self.tickets]
    
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
            'created_at': self.created_at
        }
    
    def get_chat(self):
        return Chat.query.get(self.chat_id)
    
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
    
    def rename(self, name):
        self.name = name
        self.updated_at = datetime.datetime.now()
        db.session.commit()
    
    def get_messages(self) -> Message | None:
        return Message.query.filter_by(user_id=self.user_id, chat_id=self.id).all()
    
    def add_message(self, msg: Message):
        msg.chat_id = self.id
        msg.user_id = self.user_id
        db.session.add(msg)
        db.session.commit()
        
    def delete(self):
        messages = Message.query.filter_by(chat_id=self.id).all()
        for message in messages:
            db.session.delete(message)
        db.session.delete(self)
        db.session.commit()
        
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': int(self.created_at.timestamp() * 1000),
            'modified_at': int(self.last_updated().timestamp() * 1000),
        }

    def history(self):
        return [
            {'role': 'user' if message.source else 'model', 'parts': message.message}
            for message in self.get_messages()
        ]
        
    def last_updated(self):
        msgs = self.get_messages()
        last_updated = self.updated_at
        for msg in msgs:
            if msg.created_at > last_updated:
                last_updated = msg.created_at
        return last_updated
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    @staticmethod
    def create(user_id, name):
        chat = Chat(user_id=user_id, name=name)
        db.session.add(chat)
        db.session.commit()
        return chat
