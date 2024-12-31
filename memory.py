import time
import sqlite3
import re

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
    def __init__(self, long_term_memory_db="memory/long_term_memory.db"):
        self.long_term_memory = LongTermMemory(memory_file=long_term_memory_db)
        self.short_term_memory = ShortTermMemory(max_size=2048)

    emoji_pattern = re.compile(
            "["  
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
            "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
            "\U0001F700-\U0001F77F"  # Alchemical Symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # Enclosed Characters
            "]+", 
            flags=re.UNICODE
        )
    
    excessive_punctuation = re.compile(r"^[!?.,]{3,}$")

    def add_memory_entry(self, user_id, data):
        # Add to short-term memory
        self.short_term_memory.add([user_id, data])

        # Example: Filter and decide relevance for long-term memory
        if self.is_relevant(data):
            self.long_term_memory.save_memory(key=f"{user_id}.{int(time.time())}", value=data)

        self.long_term_memory.get_memory(user_id)

    def is_relevant(self, data):
        """
        Advanced relevance logic:
        - Remove messages that are purely emojis or excessive punctuation.
        - Check if data has actual meaningful content.
        - Detect and exclude spam-like or trivial messages.
        """
        # Define patterns to exclude irrelevant content
        trivial_phrases = ["lol", "brb", "spam", "asdf", "hahaha", "lmao"]

        # Strip whitespace and normalize input
        normalized_data = data.strip().lower()

        # Check for irrelevant content
        if not normalized_data:  # Empty message
            return False

        if self.emoji_pattern.fullmatch(normalized_data):  # Purely emojis
            return False

        if self.excessive_punctuation.fullmatch(normalized_data):  # Excessive punctuation
            return False

        if normalized_data in trivial_phrases:  # Trivial phrases
            return False

        # Check if the message has at least one word with alphabetical characters
        meaningful_content = any(word.isalpha() for word in normalized_data.split())
        
        return meaningful_content


# short_term_memory = ShortTermMemory()
# short_term_memory.add("User likes coding.")
# short_term_memory.add("User played Minecraft last night.")

# print(short_term_memory.get_recent())

# long_term_memory = LongTermMemory()
# long_term_memory.save_memory('favorite_game', 'Minecraft')
# print(long_term_memory.get_memory('favorite_game'))