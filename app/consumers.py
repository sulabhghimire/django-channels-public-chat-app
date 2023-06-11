from channels.consumer import SyncConsumer,  AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync  import async_to_sync
from channels.db import database_sync_to_async
import asyncio
from . import models
import json

class MySyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        print('Websocket connected ..', event)
        print("Channel layer ...", self.channel_layer)# get default channel layer from a project
        print("Channel name ...", self.channel_name)# get channel name
        self.group_name = (self.scope['url_route']['kwargs']['group_name']).lower()
        print("User is .... ", self.scope['user'])
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,      # Group name    
            self.channel_name   # Channel name
        ) 
        #tyo group_add asynchronous hunxa tehi bhayera sync ma convert gareko
        #add a channel to new or existing group

        self.send({
            'type' : 'websocket.accept',
            'text' : 'Connected',
        })

    def websocket_receive(self, event):
        print('Message recieved from client ..', event['text']) 
        print('Type of message recieved from client ..', type(event['text']))      
        data = json.loads(event['text'])
        group = models.Group.objects.get(name=self.group_name)
        if self.scope['user'].is_authenticated:
            chat = models.Chat(group=group, content=data['msg'])
            chat.save()
            data['user'] = self.scope['user'].username
            async_to_sync(self.channel_layer.group_send)(
                self.group_name, {
                'type' : 'chat.message',
                'message' : json.dumps(data),
                }
            )
        else:
            self.send({
                'type' : 'websocket.send',
                'text' : json.dumps({'msg' : 'Login Required', 'user' : 'unknown'}),
                }
            )      

    def chat_message(self, event):
        print('Event ... ', event)
        print('Data ... ', event['message'])
        print('Data ... ', type(event['message']))
        self.send({
            'type' : 'websocket.send',
            'text' : event['message'],
        })

    def websocket_disconnect(self, event):
        print('Websocket disconnected ..', event)
        print("Channel layer ...", self.channel_layer)# get default channel layer from a project
        print("Channel name ...", self.channel_name)# get channel name
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, 
            self.channel_name
        )
        raise StopConsumer()


class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print('Websocket connected ..', event)
        print("Channel layer ...", self.channel_layer)# get default channel layer from a project
        print("Channel name ...", self.channel_name)# get channel name
        self.group_name = (self.scope['url_route']['kwargs']['group_name']).lower()
        await self.channel_layer.group_add(
            self.group_name,      # Group name    
            self.channel_name   # Channel name
        ) 

        await self.send({
            'type' : 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('Message recieved from client ..', event['text']) 
        print('Type of message recieved from client ..', type(event['text']))    
        data = json.loads(event['text'])
        group = await database_sync_to_async(models.Group.objects.get)(name=self.group_name)
        if self.scope['user'].is_authenticated:
            chat = models.Chat(group=group, content=data['msg'])
            await database_sync_to_async(chat.save)()  
            data['user'] = self.scope['user'].username
            await self.channel_layer.group_send(
                self.group_name, {
                'type' : 'chat.message',
                'message' : json.dumps(data),
                }
            )  
        else:
            await self.send({
                'type' : 'websocket.send',
                'text' : json.dumps({'msg' : 'Login Required', 'user' :'guest'}),
                }
            )   

    async def chat_message(self, event):
        print('Event ... ', event)
        print('Data ... ', event['message'])
        print('Data ... ', type(event['message']))
        await self.send({
            'type' : 'websocket.send',
            'text' : event['message'],
        })

    async def websocket_disconnect(self, event):
        print('Websocket disconnected ..', event)
        print("Channel layer ...", self.channel_layer)# get default channel layer from a project
        print("Channel name ...", self.channel_name)# get channel name
        await self.channel_layer.group_discard(
            self.group_name, 
            self.channel_name
        )
        raise StopConsumer()
