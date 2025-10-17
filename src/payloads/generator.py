"""
Gerador de payloads avançados
"""
import random
import base64
import json
from typing import Dict, List, Any

class PayloadGenerator:
    """Gera payloads realistas para diversos protocolos"""
    
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.domains = self._load_domains()
        self.api_endpoints = self._load_api_endpoints()
    
    def _load_user_agents(self) -> List[str]:
        """Carrega lista de user agents realistas"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
    
    def _load_domains(self) -> List[str]:
        """Carrega lista de domínios para referência"""
        return [
            'google.com', 'youtube.com', 'facebook.com', 'amazon.com', 'twitter.com',
            'instagram.com', 'linkedin.com', 'netflix.com', 'microsoft.com', 'apple.com'
        ]
    
    def _load_api_endpoints(self) -> List[str]:
        """Carrega endpoints de API comuns"""
        return [
            '/api/v1/users', '/api/v1/products', '/api/v1/orders',
            '/api/v1/auth/login', '/api/v1/data', '/graphql',
            '/rest/v1/items', '/v2/users', '/oauth/token'
        ]
    
    def generate_http_request(self, target: str) -> bytes:
        """Gera requisição HTTP GET realista"""
        user_agent = random.choice(self.user_agents)
        accept_language = random.choice(['en-US,en;q=0.9', 'pt-BR,pt;q=0.9', 'es-ES,es;q=0.8'])
        
        http_request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: {target}\r\n"
            f"User-Agent: {user_agent}\r\n"
            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
            f"Accept-Language: {accept_language}\r\n"
            f"Accept-Encoding: gzip, deflate, br\r\n"
            f"Connection: keep-alive\r\n"
            f"Upgrade-Insecure-Requests: 1\r\n"
            f"Cache-Control: max-age=0\r\n"
            f"\r\n"
        )
        
        return http_request.encode()
    
    def generate_http_post_request(self, target: str) -> bytes:
        """Gera requisição HTTP POST realista"""
        user_agent = random.choice(self.user_agents)
        
        # Dados POST variados
        post_data_types = [
            f"username=user{random.randint(1000,9999)}&password=pass{random.randint(1000,9999)}",
            f"email=user{random.randint(1000,9999)}@example.com&newsletter=1",
            f"search={random.choice(['product','item','service'])}&category={random.randint(1,10)}",
            json.dumps({
                "username": f"testuser{random.randint(100,999)}",
                "password": "testpass123",
                "remember": random.choice([True, False])
            })
        ]
        
        post_data = random.choice(post_data_types)
        content_type = "application/json" if post_data.startswith('{') else "application/x-www-form-urlencoded"
        
        http_request = (
            f"POST {random.choice(self.api_endpoints)} HTTP/1.1\r\n"
            f"Host: {target}\r\n"
            f"User-Agent: {user_agent}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(post_data)}\r\n"
            f"Connection: keep-alive\r\n"
            f"Accept: application/json, text/plain, */*\r\n"
            f"\r\n"
            f"{post_data}"
        )
        
        return http_request.encode()
    
    def generate_websocket_handshake(self) -> bytes:
        """Gera handshake WebSocket"""
        ws_key = base64.b64encode(random._urandom(16)).decode()
        
        handshake = (
            f"GET /chat HTTP/1.1\r\n"
            f"Host: {random.choice(self.domains)}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {ws_key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"Origin: https://{random.choice(self.domains)}\r\n"
            f"\r\n"
        )
        
        return handshake.encode()
    
    def generate_websocket_frame(self) -> bytes:
        """Gera frame WebSocket"""
        message_types = ["ping", "message", "update"]
        message_type = random.choice(message_types)
        
        messages = {
            "ping": "{\"type\":\"ping\"}",
            "message": f"{{\"type\":\"message\",\"content\":\"Hello {random.randint(1,100)}\"}}",
            "update": f"{{\"type\":\"update\",\"data\":{{\"id\":{random.randint(1,1000)}}}}}"
        }
        
        message = messages[message_type]
        frame = self._create_websocket_frame(message)
        return frame
    
    def _create_websocket_frame(self, message: str) -> bytes:
        """Cria frame WebSocket binário"""
        message_bytes = message.encode()
        frame = bytearray()
        
        # Byte 1: FIN + RSV + Opcode
        frame.append(0x81)  # FIN + texto
        
        # Byte 2: Mask + Payload Length
        if len(message_bytes) < 126:
            frame.append(0x80 | len(message_bytes))  # Masked
        elif len(message_bytes) < 65536:
            frame.append(0x80 | 126)  # Masked + 126
            frame.extend(len(message_bytes).to_bytes(2, byteorder='big'))
        else:
            frame.append(0x80 | 127)  # Masked + 127
            frame.extend(len(message_bytes).to_bytes(8, byteorder='big'))
        
        # Masking Key (4 bytes random)
        mask_key = random._urandom(4)
        frame.extend(mask_key)
        
        # Payload mascarado
        masked_payload = bytearray()
        for i, byte in enumerate(message_bytes):
            masked_payload.append(byte ^ mask_key[i % 4])
        
        frame.extend(masked_payload)
        return bytes(frame)
    
    def generate_api_json_request(self) -> bytes:
        """Gera requisição API JSON realista"""
        user_agent = random.choice(self.user_agents)
        
        api_actions = [
            {"action": "get_user", "user_id": random.randint(1, 1000)},
            {"action": "create_order", "product_id": random.randint(1, 100), "quantity": random.randint(1, 5)},
            {"action": "update_profile", "name": f"User{random.randint(100,999)}", "email": f"user{random.randint(100,999)}@example.com"},
            {"action": "search", "query": random.choice(["laptop", "phone", "book", "course"]), "limit": 10},
            {"action": "analytics", "metric": random.choice(["users", "sales", "traffic"]), "period": "daily"}
        ]
        
        json_data = random.choice(api_actions)
        json_str = json.dumps(json_data)
        
        api_request = (
            f"POST {random.choice(self.api_endpoints)} HTTP/1.1\r\n"
            f"Host: api.{random.choice(self.domains)}\r\n"
            f"User-Agent: {user_agent}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(json_str)}\r\n"
            f"Authorization: Bearer {base64.b64encode(random._urandom(20)).decode()}\r\n"
            f"Accept: application/json\r\n"
            f"Connection: keep-alive\r\n"
            f"\r\n"
            f"{json_str}"
        )
        
        return api_request.encode()
    
    def generate_xml_rpc_payload(self) -> bytes:
        """Gera payload XML-RPC"""
        methods = ["system.listMethods", "system.getCapabilities", "wp.getUsers", "metaWeblog.getRecentPosts"]
        
        xml_data = f"""<?xml version="1.0"?>
<methodCall>
    <methodName>{random.choice(methods)}</methodName>
    <params>
        <param><value><string>blog_id</string></value></param>
        <param><value><string>username</string></value></param>
        <param><value><string>password</string></value></param>
    </params>
</methodCall>"""
        
        return xml_data.encode()