from models.user import User
from models.mongua import Mongua


class Topic(Mongua):
    __fields__ = Mongua.__fields__ + [
        ('content', str, ''),
        ('user_id', int, -1),
        ('board_id', str, ''),
        ('views', int, 0),
        ('title', str, ''),
        ('cover', str, ''),
        ('directors', str, ''),
        ('rate', str, ''),
        ('star', str, ''),
        ('url', str, ''),
        ('casts', str, ''),
        ('cover_x', int, 0),
        ('cover_y', int, 0),
    ]

    @classmethod
    def get(cls, id):
        # print('id --------', id)
        m = cls.find_by(id=id)
        m.views += 1
        m.save()
        return m

    def replies(self):
        from .reply import Reply
        ms = Reply.find_all(topic_id=self.id)
        return ms

    def board(self):
        from .board import Board
        bs = []
        for b in self.board_id:
            m = Board.find(b)
            bs.append(m)
        return bs

    def user(self):
        u = User.find(id = self.user_id)
        return u

    def cover_img(self):
        # print('in cover')
        cover_url = self.cover
        name = cover_url.split("/")[-1]
        return name

    # def collect_or_not(self):

    def bouban_rate(self):
        star = 0
        i = int(float(self.rate))
        star_class = 'mybigstar' + str(i)
        return star_class