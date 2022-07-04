from models.mongua import Mongua


class Score(Mongua):
    __fields__ = Mongua.__fields__ + [
        ('grade', int, 0),
        ('topic_id', int, -1),
        ('user_id', int, -1)
    ]

    def user(self):
        from .user import User
        u = User.find(self.user_id)
        return u

    def set_user_id(self, user_id):
        self.user_id = user_id
        self.save()