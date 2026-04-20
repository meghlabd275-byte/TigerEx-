#!/usr/bin/env python3
"""
FIX Protocol Implementation for TigerEx
Supports institutional trading with FIX 4.4 standard
Enables high-frequency trading and algorithmic trading integration
"""

import asyncio
import logging
import socket
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
import json
import ssl

# @file main.py
# @author TigerEx Development Team
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FIX Message Types
class MsgType(str, Enum):
    HEARTBEAT = "0"
    TEST_REQUEST = "1"
    RESEND_REQUEST = "2"
    REJECT = "3"
    SEQUENCE_RESET = "4"
    LOGOUT = "5"
    EXECUTION_REPORT = "8"
    ORDER_CANCEL_REJECT = "9"
    LOGON = "A"
    NEWS = "B"
    EMAIL = "C"
    NEW_ORDER_SINGLE = "D"
    NEW_ORDER_LIST = "E"
    ORDER_CANCEL_REQUEST = "F"
    ORDER_CANCEL_REPLACE_REQUEST = "G"
    ORDER_STATUS_REQUEST = "H"
    ALLOCATION = "J"
    LIST_CANCEL_REQUEST = "K"
    LIST_EXECUTE = "L"
    LIST_STATUS_REQUEST = "M"
    LIST_STATUS = "N"
    ALLOCATION_ACK = "P"
    DONT_KNOW_TRADE = "Q"
    QUOTE_REQUEST = "R"
    QUOTE = "S"
    SETTLEMENT_INSTRUCTIONS = "T"
    MARKET_DATA_REQUEST = "V"
    MARKET_DATA_SNAPSHOT_FULL_REFRESH = "W"
    MARKET_DATA_INCREMENTAL_REFRESH = "X"
    MARKET_DATA_REQUEST_REJECT = "Y"
    QUOTE_CANCEL = "Z"
    QUOTE_STATUS_REQUEST = "a"
    MASS_QUOTE = "i"
    BUSINESS_MESSAGE_REJECT = "j"
    QUOTE_RESPONSE = "AJ"

# FIX Tag Numbers
class Tag(int, Enum):
    ACCOUNT = 1
    AVG_PX = 6
    BEGIN_SEQ_NO = 7
    BEGIN_STRING = 8
    BODY_LENGTH = 9
    CHECK_SUM = 10
    CUM_QTY = 14
    CURRENCY = 15
    END_SEQ_NO = 16
    EXEC_ID = 17
    EXEC_INST = 18
    EXEC_TRAN_TYPE = 20
    LAST_PX = 31
    LAST_QTY = 32
    LAST_CAP_PX = 631
    MSG_SEQ_NUM = 34
    MSG_TYPE = 35
    NEW_SEQ_NO = 36
    ORDER_ID = 37
    ORDER_QTY = 38
    ORDER_STATUS = 39
    ORD_TYPE = 40
    ORIG_CL_ORD_ID = 41
    POSS_DUP_FLAG = 43
    PRICE = 44
    REF_SEQ_NUM = 45
    SECURITY_ID = 48
    SENDER_COMP_ID = 49
    SENDING_TIME = 52
    SIDE = 54
    SYMBOL = 55
    TARGET_COMP_ID = 56
    TEXT = 58
    TIME_IN_FORCE = 59
    TRANSACT_TIME = 60
    TRADE_DATE = 75
    CL_ORD_ID = 11
    ENCRYPT_METHOD = 98
    HEART_BT_INT = 108
    GAP_FILL_FLAG = 123
    NO_RSP_TYPES = 384
    RSP_REQ_ID = 460
    MD_ENTRY_PX = 270
    MD_ENTRY_SIZE = 271
    MD_ENTRY_TYPE = 269
    MD_REQ_ID = 262
    MARKET_DEPTH = 264
    SUBSCRIPTION_REQ_TYPE = 263
    NO_MD_ENTRIES = 268
    APPL_VER_ID = 1128
    CXL_REJ_REASON = 102
    ORD_REJ_REASON = 103
    EXEC_TYPE = 150
    LEAVES_QTY = 151
    ENCODED_TEXT = 355
    ENCODED_TEXT_LEN = 354

# Order Types (Tag 40)
class OrdType(str, Enum):
    MARKET = "1"
    LIMIT = "2"
    STOP = "3"
    STOP_LIMIT = "4"
    MARKET_ON_CLOSE = "5"
    WITH_OR_WITHOUT = "6"
    LIMIT_OR_BETTER = "7"
    LIMIT_WITH_OR_WITHOUT = "8"
    ON_BASIS = "9"
    ON_CLOSE = "A"
    LIMIT_ON_CLOSE = "B"
    FOREX = "C"
    PREVIOUSLY_QUOTED = "D"
    PREVIOUSLY_INDICATED = "E"
    FOREX_LIMIT = "F"
    FOREX_SWAP = "G"
    GOOD_TILL_CANCEL = "H"
    GOOD_TILL_DATE = "I"
    AT_OPENING = "K"

# Order Side (Tag 54)
class Side(str, Enum):
    BUY = "1"
    SELL = "2"
    BUY_MINUS = "3"
    SELL_PLUS = "4"
    SELL_SHORT = "5"
    SELL_SHORT_EXEMPT = "6"
    UNDISCLOSED = "7"
    CROSS = "8"
    CROSS_SHORT = "9"

# Time in Force (Tag 59)
class TimeInForce(str, Enum):
    DAY = "0"
    GOOD_TILL_CANCEL = "1"
    AT_OPENING = "2"
    IMMEDIATE_OR_CANCEL = "3"
    FILL_OR_KILL = "4"
    GOOD_TILL_CROSSING = "5"
    GOOD_TILL_DATE = "6"
    AT_CLOSE = "7"

# Order Status (Tag 39)
class OrdStatus(str, Enum):
    NEW = "0"
    PARTIALLY_FILLED = "1"
    FILLED = "2"
    DONE_FOR_DAY = "3"
    CANCELLED = "4"
    REPLACED = "5"
    PENDING_CANCEL = "6"
    STOPPED = "7"
    REJECTED = "8"
    SUSPENDED = "9"
    PENDING_NEW = "A"
    CALCULATED = "B"
    EXPIRED = "C"
    ACCEPTED_FOR_BIDDING = "D"
    PENDING_REPLACE = "E"

# Execution Type (Tag 150)
class ExecType(str, Enum):
    NEW = "0"
    PARTIAL_FILL = "1"
    FILL = "2"
    DONE_FOR_DAY = "3"
    CANCELLED = "4"
    REPLACED = "5"
    PENDING_CANCEL = "6"
    STOPPED = "7"
    REJECTED = "8"
    SUSPENDED = "9"
    PENDING_NEW = "A"
    CALCULATED = "B"
    EXPIRED = "C"
    RESTATE = "D"
    PENDING_REPLACE = "E"
    TRADE = "F"
    TRADE_CORRECT = "G"
    TRADE_CANCEL = "H"
    ORDER_STATUS = "I"

@dataclass
class FIXMessage:
    """FIX Protocol Message"""
    msg_type: str
    sender_comp_id: str
    target_comp_id: str
    msg_seq_num: int
    sending_time: str
    fields: Dict[int, Any] = field(default_factory=dict)
    
    def add_field(self, tag: int, value: Any) -> 'FIXMessage':
        """Add a field to the message"""
        self.fields[tag] = value
        return self
    
    def get_field(self, tag: int) -> Optional[Any]:
        """Get a field value"""
        return self.fields.get(tag)
    
    def encode(self) -> str:
        """Encode message to FIX format"""
        parts = []
        
        # Header
        parts.append(f"8=FIX.4.4")
        
        # Body
        body_parts = []
        body_parts.append(f"35={self.msg_type}")
        body_parts.append(f"49={self.sender_comp_id}")
        body_parts.append(f"56={self.target_comp_id}")
        body_parts.append(f"34={self.msg_seq_num}")
        body_parts.append(f"52={self.sending_time}")
        
        for tag, value in sorted(self.fields.items()):
            body_parts.append(f"{tag}={value}")
        
        body = chr(1).join(body_parts)
        
        # Calculate body length
        body_length = len(body)
        
        # Construct full message
        message = f"8=FIX.4.4{chr(1)}9={body_length}{chr(1)}{body}"
        
        # Calculate checksum
        checksum = sum(ord(c) for c in message) % 256
        message += f"{chr(1)}10={checksum:03d}{chr(1)}"
        
        return message
    
    @classmethod
    def decode(cls, raw: str) -> 'FIXMessage':
        """Decode FIX message from raw string"""
        fields = {}
        parts = raw.split(chr(1))
        
        for part in parts:
            if '=' in part:
                tag_str, value = part.split('=', 1)
                try:
                    tag = int(tag_str)
                    fields[tag] = value
                except ValueError:
                    continue
        
        return cls(
            msg_type=fields.get(Tag.MSG_TYPE, ""),
            sender_comp_id=fields.get(Tag.SENDER_COMP_ID, ""),
            target_comp_id=fields.get(Tag.TARGET_COMP_ID, ""),
            msg_seq_num=int(fields.get(Tag.MSG_SEQ_NUM, 0)),
            sending_time=fields.get(Tag.SENDING_TIME, ""),
            fields=fields
        )


class FIXSession:
    """FIX Protocol Session Manager"""
    
    def __init__(self, sender_comp_id: str, target_comp_id: str,
                 socket: socket.socket, seq_num: int = 1):
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.socket = socket
        self.seq_num = seq_num
        self.last_recv_seq_num = 0
        self.heartbeat_interval = 30
        self.is_active = False
        self.last_heartbeat = datetime.utcnow()
        
        # Message handlers
        self.handlers: Dict[str, List[Callable]] = {
            MsgType.NEW_ORDER_SINGLE: [],
            MsgType.ORDER_CANCEL_REQUEST: [],
            MsgType.ORDER_CANCEL_REPLACE_REQUEST: [],
            MsgType.ORDER_STATUS_REQUEST: [],
            MsgType.MARKET_DATA_REQUEST: [],
            MsgType.LOGON: [],
            MsgType.LOGOUT: [],
            MsgType.HEARTBEAT: [],
            MsgType.TEST_REQUEST: [],
        }
        
        # Order management
        self.orders: Dict[str, Dict] = {}  # ClOrdID -> Order
        self.executions: Dict[str, List[Dict]] = {}  # OrderID -> Executions
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register a message handler"""
        if msg_type in self.handlers:
            self.handlers[msg_type].append(handler)
    
    def send_message(self, msg_type: str, fields: Dict[int, Any] = None) -> bool:
        """Send a FIX message"""
        try:
            message = FIXMessage(
                msg_type=msg_type,
                sender_comp_id=self.sender_comp_id,
                target_comp_id=self.target_comp_id,
                msg_seq_num=self.seq_num,
                sending_time=datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:21],
                fields=fields or {}
            )
            
            raw = message.encode()
            self.socket.send(raw.encode())
            self.seq_num += 1
            
            logger.debug(f"Sent FIX message: {msg_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def process_message(self, message: FIXMessage):
        """Process incoming FIX message"""
        self.last_recv_seq_num = message.msg_seq_num
        
        msg_type = message.msg_type
        
        # Handle standard messages
        if msg_type == MsgType.LOGON:
            self._handle_logon(message)
        elif msg_type == MsgType.LOGOUT:
            self._handle_logout(message)
        elif msg_type == MsgType.HEARTBEAT:
            self.last_heartbeat = datetime.utcnow()
        elif msg_type == MsgType.TEST_REQUEST:
            self.send_message(MsgType.HEARTBEAT)
        else:
            # Call registered handlers
            for handler in self.handlers.get(msg_type, []):
                try:
                    handler(message)
                except Exception as e:
                    logger.error(f"Handler error: {e}")
    
    def _handle_logon(self, message: FIXMessage):
        """Handle LOGON message"""
        self.is_active = True
        self.heartbeat_interval = int(message.get_field(Tag.HEART_BT_INT) or 30)
        logger.info(f"FIX session logged on: {self.sender_comp_id}")
    
    def _handle_logout(self, message: FIXMessage):
        """Handle LOGOUT message"""
        self.is_active = False
        logger.info(f"FIX session logged out: {self.sender_comp_id}")
    
    def send_execution_report(self, cl_ord_id: str, order_id: str,
                              exec_type: str, ord_status: str,
                              symbol: str, side: str, order_qty: float,
                              price: float, cum_qty: float = 0,
                              avg_px: float = 0, leaves_qty: float = 0,
                              last_qty: float = 0, last_px: float = 0,
                              text: str = "") -> bool:
        """Send Execution Report (MsgType=8)"""
        fields = {
            Tag.CL_ORD_ID: cl_ord_id,
            Tag.ORDER_ID: order_id,
            Tag.EXEC_TYPE: exec_type,
            Tag.ORDER_STATUS: ord_status,
            Tag.SYMBOL: symbol,
            Tag.SIDE: side,
            Tag.ORDER_QTY: str(order_qty),
            Tag.PRICE: str(price),
            Tag.CUM_QTY: str(cum_qty),
            Tag.AVG_PX: str(avg_px),
            Tag.LEAVES_QTY: str(leaves_qty),
            Tag.TRANSACT_TIME: datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:21]
        }
        
        if last_qty > 0:
            fields[Tag.LAST_QTY] = str(last_qty)
            fields[Tag.LAST_PX] = str(last_px)
        
        if text:
            fields[Tag.TEXT] = text
        
        return self.send_message(MsgType.EXECUTION_REPORT, fields)
    
    def send_order_cancel_reject(self, cl_ord_id: str, orig_cl_ord_id: str,
                                 order_id: str, cxl_rej_reason: str = "1",
                                 text: str = "") -> bool:
        """Send Order Cancel Reject (MsgType=9)"""
        fields = {
            Tag.CL_ORD_ID: cl_ord_id,
            Tag.ORIG_CL_ORD_ID: orig_cl_ord_id,
            Tag.ORDER_ID: order_id,
            Tag.CXL_REJ_REASON: cxl_rej_reason
        }
        
        if text:
            fields[Tag.TEXT] = text
        
        return self.send_message(MsgType.ORDER_CANCEL_REJECT, fields)


class FIXServer:
    """FIX Protocol Server for TigerEx"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 9876,
                 use_ssl: bool = True, ssl_cert: str = None, ssl_key: str = None):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        
        self.sessions: Dict[str, FIXSession] = {}
        self.running = False
        self.server_socket = None
        
        # Callbacks for order events
        self.on_new_order: Optional[Callable] = None
        self.on_cancel_order: Optional[Callable] = None
        self.on_replace_order: Optional[Callable] = None
        self.on_market_data_request: Optional[Callable] = None
    
    def start(self):
        """Start the FIX server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.running = True
        
        logger.info(f"FIX Server started on {self.host}:{self.port}")
        
        # Start accept thread
        accept_thread = threading.Thread(target=self._accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(target=self._heartbeat_check)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
    
    def stop(self):
        """Stop the FIX server"""
        self.running = False
        
        for session in self.sessions.values():
            session.send_message(MsgType.LOGOUT)
            session.is_active = False
        
        if self.server_socket:
            self.server_socket.close()
        
        logger.info("FIX Server stopped")
    
    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"New connection from {address}")
                
                # Wrap with SSL if enabled
                if self.use_ssl and self.ssl_cert and self.ssl_key:
                    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                    context.load_cert_chain(self.ssl_cert, self.ssl_key)
                    client_socket = context.wrap_socket(client_socket, server_side=True)
                
                # Start session handler thread
                session_thread = threading.Thread(
                    target=self._handle_session,
                    args=(client_socket, address)
                )
                session_thread.daemon = True
                session_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def _handle_session(self, client_socket: socket.socket, address):
        """Handle a FIX session"""
        session_id = str(uuid.uuid4())
        session = None
        buffer = ""
        
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                buffer += data.decode()
                
                # Parse complete messages
                while chr(1) + "10=" in buffer:
                    # Find message end
                    end_idx = buffer.find(chr(1) + "10=")
                    end_idx = buffer.find(chr(1), end_idx + 4) + 1
                    
                    if end_idx > 0:
                        raw_msg = buffer[:end_idx]
                        buffer = buffer[end_idx:]
                        
                        try:
                            message = FIXMessage.decode(raw_msg)
                            
                            # Create session on LOGON
                            if message.msg_type == MsgType.LOGON:
                                sender_comp_id = message.sender_comp_id
                                target_comp_id = message.target_comp_id
                                
                                session = FIXSession(
                                    sender_comp_id=target_comp_id,  # We are the target
                                    target_comp_id=sender_comp_id,  # They are the target
                                    socket=client_socket
                                )
                                self.sessions[session_id] = session
                                
                                # Register handlers
                                session.register_handler(
                                    MsgType.NEW_ORDER_SINGLE,
                                    lambda msg: self._handle_new_order(session, msg)
                                )
                                session.register_handler(
                                    MsgType.ORDER_CANCEL_REQUEST,
                                    lambda msg: self._handle_cancel_order(session, msg)
                                )
                                session.register_handler(
                                    MsgType.MARKET_DATA_REQUEST,
                                    lambda msg: self._handle_market_data(session, msg)
                                )
                                
                                # Send LOGON response
                                session.send_message(
                                    MsgType.LOGON,
                                    {Tag.HEART_BT_INT: 30}
                                )
                            
                            # Process message
                            if session:
                                session.process_message(message)
                                
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                
        except Exception as e:
            logger.error(f"Session error: {e}")
        
        finally:
            if session_id in self.sessions:
                del self.sessions[session_id]
            client_socket.close()
            logger.info(f"Session {session_id} closed")
    
    def _handle_new_order(self, session: FIXSession, message: FIXMessage):
        """Handle New Order Single (MsgType=D)"""
        cl_ord_id = message.get_field(Tag.CL_ORD_ID)
        symbol = message.get_field(Tag.SYMBOL)
        side = message.get_field(Tag.SIDE)
        order_qty = float(message.get_field(Tag.ORDER_QTY) or 0)
        ord_type = message.get_field(Tag.ORD_TYPE)
        price = float(message.get_field(Tag.PRICE) or 0)
        time_in_force = message.get_field(Tag.TIME_IN_FORCE)
        
        logger.info(f"New Order: {cl_ord_id} {symbol} {side} {order_qty} @ {price}")
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Store order
        session.orders[cl_ord_id] = {
            "order_id": order_id,
            "cl_ord_id": cl_ord_id,
            "symbol": symbol,
            "side": side,
            "quantity": order_qty,
            "price": price,
            "order_type": ord_type,
            "time_in_force": time_in_force,
            "status": OrdStatus.NEW,
            "filled_quantity": 0,
            "average_price": 0
        }
        
        # Send acknowledgment
        session.send_execution_report(
            cl_ord_id=cl_ord_id,
            order_id=order_id,
            exec_type=ExecType.NEW,
            ord_status=OrdStatus.NEW,
            symbol=symbol,
            side=side,
            order_qty=order_qty,
            price=price,
            leaves_qty=order_qty
        )
        
        # Call external handler if registered
        if self.on_new_order:
            self.on_new_order(session, session.orders[cl_ord_id])
    
    def _handle_cancel_order(self, session: FIXSession, message: FIXMessage):
        """Handle Order Cancel Request (MsgType=F)"""
        cl_ord_id = message.get_field(Tag.CL_ORD_ID)
        orig_cl_ord_id = message.get_field(Tag.ORIG_CL_ORD_ID)
        symbol = message.get_field(Tag.SYMBOL)
        
        logger.info(f"Cancel Order: {orig_cl_ord_id}")
        
        # Find original order
        if orig_cl_ord_id not in session.orders:
            session.send_order_cancel_reject(
                cl_ord_id=cl_ord_id,
                orig_cl_ord_id=orig_cl_ord_id,
                order_id="UNKNOWN",
                cxl_rej_reason="1",
                text="Unknown order"
            )
            return
        
        order = session.orders[orig_cl_ord_id]
        
        if order["status"] in [OrdStatus.FILLED, OrdStatus.CANCELLED]:
            session.send_order_cancel_reject(
                cl_ord_id=cl_ord_id,
                orig_cl_ord_id=orig_cl_ord_id,
                order_id=order["order_id"],
                cxl_rej_reason="3",
                text="Order already terminal"
            )
            return
        
        # Cancel the order
        order["status"] = OrdStatus.CANCELLED
        
        session.send_execution_report(
            cl_ord_id=cl_ord_id,
            order_id=order["order_id"],
            exec_type=ExecType.CANCELLED,
            ord_status=OrdStatus.CANCELLED,
            symbol=order["symbol"],
            side=order["side"],
            order_qty=order["quantity"],
            price=order["price"],
            cum_qty=order["filled_quantity"],
            avg_px=order["average_price"],
            leaves_qty=0,
            text="Order cancelled"
        )
        
        if self.on_cancel_order:
            self.on_cancel_order(session, order)
    
    def _handle_market_data(self, session: FIXSession, message: FIXMessage):
        """Handle Market Data Request (MsgType=V)"""
        md_req_id = message.get_field(Tag.MD_REQ_ID)
        subscription_type = message.get_field(Tag.SUBSCRIPTION_REQ_TYPE)
        market_depth = int(message.get_field(Tag.MARKET_DEPTH) or 1)
        
        logger.info(f"Market Data Request: {md_req_id}")
        
        if self.on_market_data_request:
            self.on_market_data_request(session, {
                "md_req_id": md_req_id,
                "subscription_type": subscription_type,
                "market_depth": market_depth
            })
    
    def send_market_data_snapshot(self, session: FIXSession, md_req_id: str,
                                   symbol: str, bids: List[tuple], asks: List[tuple]):
        """Send Market Data Snapshot (MsgType=W)"""
        fields = {
            Tag.MD_REQ_ID: md_req_id,
            Tag.SYMBOL: symbol
        }
        
        # Add MD entries
        entries = []
        for price, size in bids:
            entries.append(f"269=0{chr(1)}270={price}{chr(1)}271={size}")
        for price, size in asks:
            entries.append(f"269=1{chr(1)}270={price}{chr(1)}271={size}")
        
        fields[Tag.NO_MD_ENTRIES] = str(len(entries))
        # Note: Actual implementation would need proper repeating groups
        
        session.send_message(MsgType.MARKET_DATA_SNAPSHOT_FULL_REFRESH, fields)
    
    def _heartbeat_check(self):
        """Check for session heartbeats"""
        while self.running:
            for session_id, session in list(self.sessions.items()):
                if session.is_active:
                    elapsed = (datetime.utcnow() - session.last_heartbeat).total_seconds()
                    if elapsed > session.heartbeat_interval * 2:
                        logger.warning(f"Session {session_id} heartbeat timeout")
                        session.is_active = False
                    elif elapsed > session.heartbeat_interval:
                        session.send_message(MsgType.TEST_REQUEST)
            
            time.sleep(10)


# Initialize FIX Server
fix_server = FIXServer()


if __name__ == "__main__":
    # Example usage
    fix_server.on_new_order = lambda session, order: print(f"New order received: {order}")
    fix_server.on_cancel_order = lambda session, order: print(f"Cancel order: {order}")
    
    fix_server.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        fix_server.stop()