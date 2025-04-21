class User:
    def __init__(self, username, password, email=None, user_id=None, created_at=None):
        self.id = user_id
        self.username = username
        self.password = password  # In a real app, this should be hashed
        self.email = email
        self.created_at = created_at

    def __str__(self):
        return f"User: {self.username} (ID: {self.id})"

    @classmethod
    def from_db_row(cls, row):
        """Create a User object from a database row"""
        if row:
            return cls(
                user_id=row[0], 
                username=row[1], 
                password=row[2], 
                email=row[3], 
                created_at=row[4]
            )
        return None 