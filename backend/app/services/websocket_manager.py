import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {
            "weather_updates": set(),
            "alerts": set(),
            "predictions": set(),
            "blockchain_events": set(),
            "emergency_events": set()
        }
        self.running = False
    
    async def start(self):
        """Start the WebSocket manager"""
        self.running = True
        print("WebSocket manager started")
    
    async def stop(self):
        """Stop the WebSocket manager"""
        self.running = False
        # Close all connections
        for connection in self.active_connections.values():
            await connection.close()
        self.active_connections.clear()
        for subscription_set in self.subscriptions.values():
            subscription_set.clear()
        print("WebSocket manager stopped")
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "message": "Connected to WeatherGuard WebSocket",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        print(f"Client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove from all subscriptions
        for subscription_set in self.subscriptions.values():
            subscription_set.discard(client_id)
        
        print(f"Client {client_id} disconnected")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_subscribers(self, message: dict, subscription_type: str):
        """Broadcast a message to all subscribers of a specific type"""
        if subscription_type in self.subscriptions:
            subscribers = self.subscriptions[subscription_type].copy()
            
            # Add message metadata
            message.update({
                "subscription_type": subscription_type,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Send to all subscribers
            for client_id in subscribers:
                await self.send_personal_message(message, client_id)
    
    async def subscribe(self, client_id: str, subscription_type: str):
        """Subscribe a client to a specific message type"""
        if subscription_type in self.subscriptions:
            self.subscriptions[subscription_type].add(client_id)
            
            await self.send_personal_message({
                "type": "subscription",
                "message": f"Subscribed to {subscription_type}",
                "subscription_type": subscription_type
            }, client_id)
            
            print(f"Client {client_id} subscribed to {subscription_type}")
            return True
        return False
    
    async def unsubscribe(self, client_id: str, subscription_type: str):
        """Unsubscribe a client from a specific message type"""
        if subscription_type in self.subscriptions:
            self.subscriptions[subscription_type].discard(client_id)
            
            await self.send_personal_message({
                "type": "unsubscription",
                "message": f"Unsubscribed from {subscription_type}",
                "subscription_type": subscription_type
            }, client_id)
            
            print(f"Client {client_id} unsubscribed from {subscription_type}")
            return True
        return False
    
    async def handle_message(self, message: dict, client_id: str):
        """Handle incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            
            if message_type == "subscribe":
                subscription_type = message.get("subscription_type")
                if subscription_type:
                    await self.subscribe(client_id, subscription_type)
            
            elif message_type == "unsubscribe":
                subscription_type = message.get("subscription_type")
                if subscription_type:
                    await self.unsubscribe(client_id, subscription_type)
            
            elif message_type == "ping":
                await self.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, client_id)
            
            elif message_type == "get_status":
                await self.send_personal_message({
                    "type": "status",
                    "active_connections": len(self.active_connections),
                    "subscriptions": {
                        sub_type: len(subscribers) 
                        for sub_type, subscribers in self.subscriptions.items()
                    }
                }, client_id)
            
            else:
                await self.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, client_id)
        
        except Exception as e:
            await self.send_personal_message({
                "type": "error",
                "message": f"Error processing message: {str(e)}"
            }, client_id)
    
    # Broadcast methods for different event types
    async def broadcast_weather_update(self, weather_data: dict):
        """Broadcast weather update to subscribers"""
        await self.broadcast_to_subscribers({
            "type": "weather_update",
            "data": weather_data
        }, "weather_updates")
    
    async def broadcast_alert(self, alert_data: dict):
        """Broadcast weather alert to subscribers"""
        await self.broadcast_to_subscribers({
            "type": "alert",
            "data": alert_data,
            "priority": alert_data.get("severity", "medium")
        }, "alerts")
    
    async def broadcast_prediction(self, prediction_data: dict):
        """Broadcast weather prediction to subscribers"""
        await self.broadcast_to_subscribers({
            "type": "prediction",
            "data": prediction_data
        }, "predictions")
    
    async def broadcast_blockchain_event(self, event_data: dict):
        """Broadcast blockchain event to subscribers"""
        await self.broadcast_to_subscribers({
            "type": "blockchain_event",
            "data": event_data
        }, "blockchain_events")
    
    async def broadcast_emergency_event(self, emergency_data: dict):
        """Broadcast emergency event to subscribers"""
        await self.broadcast_to_subscribers({
            "type": "emergency_event",
            "data": emergency_data,
            "priority": "high"
        }, "emergency_events")
    
    def get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "subscriptions": {
                sub_type: len(subscribers) 
                for sub_type, subscribers in self.subscriptions.items()
            },
            "active_clients": list(self.active_connections.keys())
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
