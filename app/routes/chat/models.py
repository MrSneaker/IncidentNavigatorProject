from flask_sqlalchemy import SQLAlchemy
import datetime
from uuid import uuid4

from .. import db

def get_uuid():
    return uuid4().hex


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    chat_id = db.Column(db.String(32), db.ForeignKey('chats.id'), nullable=False)
    source = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    
    def __repr__(self):
        return f'<Message {self.message}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'source': self.source,
            'message': self.message,
            'created_at': self.created_at
        }
    
    def get_chat(self):
        return Chat.query.get(self.chat_id)
    

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
    
    def get_messages(self):
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
    