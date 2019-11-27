"""
...
"""

# standard library
import json
from typing import Any, Dict, List, Tuple, Union

# third-party
# from channels.auth import get_user, login
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

# Django
from django.utils import timezone
# from django.contrib.auth.models import AnonymousUser, User

# local Django
from chat.models import Room
from chat.serializers import RequestSerializer, RoomSerializer

from user.decorators import user_active, token_required

class RoomConsumer(AsyncWebsocketConsumer):
    """
    ...
    """
    room_group_name: str = 'rooms'

    async def connect(self):
        """
        Join room group
        """
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # print(self.scope["headers"])
        await self.accept()

    async def disconnect(self, close_code):
        """
        Leave room group
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @token_required
    async def receive(self, text_data: str):
        """
        Receive message from WebSocket
        """
        request: Dict[str, Any] = self.validate_request(text_data)
        if 'errors' in request:
            await self.send(text_data=json.dumps(request))
        else:
            if request['method'] == 'c' or request['method'] == 'u':
                room: Any = await self.update_room(request['values'])
                # print(room)
                if isinstance(room, dict):
                    # print(request)
                    await self.send(text_data=json.dumps(room))
                else:
                    serializer = RoomSerializer(room)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'room_event',
                            'method': request['method'],
                            'room': serializer.data,
                        }
                    )
            elif request['method'] == 'd':
                result: Union[Dict[str, str], Tuple[Any]] = await self.delete_room(
                    request['values']
                )
                if isinstance(result, dict):
                    # print(result)
                    await self.send(text_data=json.dumps(result))
                else:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'room_remove',
                            'method': request['method'],
                            'details': result,
                        }
                    )
            else:
                rooms: List[Tuple[Any]] = await self.list_room()
                if isinstance(rooms, dict):
                    # print(result)
                    await self.send(text_data=json.dumps(rooms))
                else:
                    await self.send(text_data=json.dumps({
                        'method': request['method'],
                        'data': rooms,
                    }))
                    # await self.channel_layer.group_send(
                    #     self.room_group_name,
                    #     {
                    #         'type': 'room_list',
                    #         'method': 'r',
                    #         'list': rooms,
                    #     }
                    # )

    @user_active
    async def room_list(self, event: Dict[str, Any]):
        """
        Receive message from room group
        """
        # print(event['type'])

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'method': event['method'],
            'data': event['list'],
        }))

    @user_active
    async def room_event(self, event: Dict[str, Any]):
        """
        Receive message from room group
        """
        print(event)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'method': event['method'],
            'room': event['room'],
        }))

    @user_active
    async def room_remove(self, event: Dict[str, Any]):
        """
        Receive message from room group
        """
        # print(event['type'])

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'method': event['method'],
            'details': event['details'],
        }))

    @database_sync_to_async
    def list_room(self) -> Union[Dict[str, str], Room]:
        """
        listar room
        """
        try:
            return tuple(Room.objects.all().order_by('id').values('id', 'name'))
        except Exception as e:
            return {'errors': {'exception': str(e)}}

    @database_sync_to_async
    def update_room(self, values: Dict[str, Any]) -> Union[Dict[str, str], Room]:
        """
        Crear room o retornar error
        """
        try:
            room, created = Room.objects.update_or_create(
                name=values['name'],
                defaults={'updated': timezone.now()},
            )
            return room
        except Exception as e:
            return {'errors': {'exception': str(e)}}

    @database_sync_to_async
    def delete_room(self, values: Dict[str, Any]) -> Tuple[Any]:
        """
        eliminar room o retornar error
        retorna (numoro eliminados, dict tipos eliminados)
        """
        try:
            return Room.objects.filter(
                pk__in=values['pk_list'],
            ).delete()
        except Exception as e:
            return {'errors': {'exception': str(e)}}

    def validate_request(self, text_data: str) -> Dict[str, Any]:
        """
        validar contenido solicitud
        """
        try:
            text_data_json: Dict['str', Any] = json.loads(text_data)
            # print(text_data_json)
            # validar propiedades
            serializer = RequestSerializer(data=text_data_json)
            if serializer.is_valid():
                return serializer.data

            return response.errors
            
        except Exception as e:
            return {'errors': {'invalid_json': str(e)}}
