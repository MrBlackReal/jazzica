import time
import sqlite3

from collections import deque

class ShortTermMemory:
    def __init__(self, memory_duration=3600, max_size=5):
        self.memory_duration = memory_duration
        self.max_size = max_size
        self.memory = deque()

    def add(self, data):
        timestamp = time.time()

        while self.memory and timestamp - self.memory[0][1] > self.memory_duration:
            self.memory.popleft()

        self.memory.append((data, timestamp))

        if len(self.memory) > self.max_size:
            self.memory.popleft()

    def get_recent(self):
        return [item[0] for item in self.memory]


class LongTermMemory:
    def __init__(self, memory_file="memory/long_term_memory.db"):
        self.memory_file = memory_file
        self.conn = sqlite3.connect(self.memory_file)
        self.cursor = self.conn.cursor()
        
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (key TEXT PRIMARY KEY, value TEXT)
            """
        )
        self.conn.commit()

    def save_memory(self, key, value):
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)
            """,
            (key, value)
        )
        self.conn.commit()

    def get_memory(self, key):
        self.cursor.execute('SELECT value FROM memory WHERE key=?', (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def go_to_sleep(self):
        self.conn.close()


class MemoryManager:
    def __init__(self, long_term_memory_db):
        self.long_term_memory_db = long_term_memory_db
        
    def add_memory_entry(self, user_id, channel_id, data):
        


short_term_memory = ShortTermMemory()
short_term_memory.add("User likes coding.")
short_term_memory.add("User played Minecraft last night.")

print(short_term_memory.get_recent())

long_term_memory = LongTermMemory()
long_term_memory.save_memory('favorite_game', 'Minecraft')
print(long_term_memory.get_memory('favorite_game'))