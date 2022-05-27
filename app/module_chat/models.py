# Librerias
from datetime import datetime, timedelta
#from dotenv import load_dotenv, find_dotenv
from sqlalchemy.dialects.postgresql import UUID
from app import db

# Settings
# app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Defueine the chat model
class Chat(db.Model):
    '''
    Table Chat
    '''

    __tablename__ = 'chat'

    #id del Chat
    id = db.Column(UUID(as_uuid = True), primary_key = True)

    #id del event
    event_id = db.Column(UUID(as_uuid = True), nullable = False)

    #id del creador del event
    creador_id = db.Column(UUID(as_uuid = True), nullable = False)

    #id del usuari participant
    participant_id = db.Column(UUID(as_uuid = True), nullable = False)

    #To create a instance of a Chat
    def __init__(self, id, event_id, creador_id, participant_id):
        self.id = id
        self.event_id = event_id
        self.creador_id = creador_id
        self.participant_id = participant_id

    def __repr__(self):
        return '''Chat(id: ' str(self.id) + ' , event_id: ' str(self.event_id) + ' , creador_id: ' str(self.creador_id) + ' , participant_id ' str(self.participant_id) ').''' 

    #To delete a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # To save a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    #To convert a Chat object in a dictionary
    def toJSON(self):
        return{
            "id": self.id,
            "event_id": self.event_id,
            "creador_id": self.creador_id,
            "participant_id": self.participant_id
        }

#Define the message model
class Message(db.Model):
    '''
    Table message
    '''
    __tablename__ = 'message'

    #id del missatge
    id = db.Column(UUID(as_uuid = True), primary_key=True)

    #id del usuari que ho envia
    sender_id = db.Column(UUID(as_uuid=True) , nullable = False)   

    #id del chat al que pertany
    chat_id = db.Column(UUID(as_uuid=True) , db.ForeignKey('chat.id') , nullable=False)

    #contingut del missatge
    text = db.Column(db.Text)

    #date when the missage was sent
    created_at = db.Column(db.DateTime, nullable=False, default =  datetime.now() + timedelta(hours=2))

    # To create a instance of Message
    def __init__(self, id, sender_id, chat_id, text):
        self.id = id
        self.sender_id = sender_id
        self.chat_id = chat_id
        self.text = text

    def __repr__(self):
        return '''Message(id: ' + str(self.id) + ' , sender_id: ' + str(self.sender_id) + ' , chat_id: ' + str(self.chat_id) + 
                ' , text: ' + Text(self.text) + ' , created_at: ' + str(self.created_at) ').'''

    # To delete a row from the table
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # To save a row from the table
    def save(self):
        db.session.add(self)
        db.session.commit()

    # To convert a Message object in a dictionary
    def toJSON(self):
        return{
            "id": self.id,
            "sender_id": self.sender_id,
            "chat_id": self.chat_id,
            "text": self.text,
            "created_ad": self.created_at
        }


#if __name__ == "__main__":
    #manager.run()

