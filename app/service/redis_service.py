# redis_service.py
import redis
import json
import time
import threading
import uuid
from typing import Any, Dict, Optional
from app.config import CONFIG

redis_config = CONFIG.get('redis_config')
host = redis_config.get('host')
port = redis_config.get('port')
username = redis_config.get('username')
password = redis_config.get('password')
db = redis_config.get('db')

class RedisService:
    _instance = None      # 单例实例
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        
        # 已实例化过就不重复初始化 client
        if hasattr(self, "client"):
            return
        
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.password = password
        self.decode_responses = True
        self.reconnect_retry = 3

        self._create_client()

    # ------------------------------------------------------------
    # 创建 Redis Pool + Client
    # ------------------------------------------------------------
    def _create_client(self):
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=self.decode_responses,
            max_connections=50,
        )
        self.client = redis.Redis(connection_pool=self.pool)

    # ------------------------------------------------------------
    # 自动重连装饰器
    # ------------------------------------------------------------
    def _auto_reconnect(func):
        def wrapper(self, *args, **kwargs):
            for _ in range(self.reconnect_retry):
                try:
                    return func(self, *args, **kwargs)
                except redis.ConnectionError:
                    time.sleep(2)
                    self._create_client()
            raise
        return wrapper

    # ------------------------------------------------------------
    # JSON 序列化/反序列化
    # ------------------------------------------------------------
    def _dumps(self, value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _loads(self, value: Optional[str]):
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return value

    # ------------------------------------------------------------
    # 基础操作
    # ------------------------------------------------------------
    @_auto_reconnect
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        return self.client.set(key, self._dumps(value), ex=expire)

    @_auto_reconnect
    def get(self, key: str):
        return self._loads(self.client.get(key))

    @_auto_reconnect
    def delete(self, key: str):
        return self.client.delete(key)

    @_auto_reconnect
    def exists(self, key: str) -> bool:
        return self.client.exists(key) == 1

    @_auto_reconnect
    def incr(self, key: str, amount: int = 1):
        return self.client.incr(key, amount)

    # ------------------------------------------------------------
    # Hash 操作
    # ------------------------------------------------------------
    @_auto_reconnect
    def hset(self, name: str, key: str, value: Any):
        return self.client.hset(name, key, self._dumps(value))

    @_auto_reconnect
    def hget(self, name: str, key: str):
        return self._loads(self.client.hget(name, key))

    @_auto_reconnect
    def hgetall(self, name: str) -> Dict[str, Any]:
        raw = self.client.hgetall(name)
        return {k: self._loads(v) for k, v in raw.items()}

    # ------------------------------------------------------------
    # ----------------  RedLock 分布式锁  -------------------------
    # ------------------------------------------------------------
    class RedisLock:
        """
        RedLock 分布式锁（支持自动续期）
        """

        def __init__(self, service, key: str, ttl: int = 5000, auto_renew: bool = True):
            self.service = service
            self.key = key
            self.ttl = ttl  # 毫秒
            self.auto_renew = auto_renew
            self.value = uuid.uuid4().hex
            self._renew_thread = None
            self._stop = False

        def acquire(self) -> bool:
            result = self.service.client.set(
                self.key, 
                self.value, 
                px=self.ttl,
                nx=True
            )
            if result:
                if self.auto_renew:
                    self._start_auto_renew()
                return True
            return False

        def release(self):
            # Lua 脚本保证释放锁的 "原子性"
            script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                else
                    return 0
                end
            """
            self.service.client.eval(script, 1, self.key, self.value)
            self._stop = True

        def _start_auto_renew(self):
            def renew():
                while not self._stop:
                    time.sleep(self.ttl / 2000)  # 每半 TTL 续期一次
                    try:
                        self.service.client.pexpire(self.key, self.ttl)
                    except redis.ConnectionError:
                        pass

            self._renew_thread = threading.Thread(target=renew, daemon=True)
            self._renew_thread.start()

    def lock(self, key: str, ttl: int = 5000, auto_renew: bool = True):
        """
        获取分布式锁对象
        """
        return RedisService.RedisLock(self, key, ttl, auto_renew)
