class Articles:
    def __init__(self, **kwargs):
        self.Title = kwargs.get("Title", "")
        self.Article = kwargs.get("Article", "")
        self.DateString = kwargs.get("DateString", "")
        self.Image = "/static/images/" + kwargs.get("Image", "")
        self.Id = kwargs.get("Id", "")


class Replys:
    def __init__(self, **kwargs):
        self.Reply = kwargs.get("Reply", "")
        self.DateString = kwargs.get("DateString", "")
        self.IdArticle = kwargs.get("IdArticle", "")
        self.Id = kwargs.get("Id", "")
        self.Ip = kwargs.get("Ip", "")
        self.ListTo = kwargs.get("ListTo", "").split(",")
        self.Replys = []
        self.IdCookie = kwargs.get("IdCookie", "")


class BlockList:
    def __init__(self, **kwargs):
        self.Ip = kwargs.get("Ip", "")
        self.DateFrom = kwargs.get("DateFrom", "")
        self.DateTo = kwargs.get("DateTo", "")
        self.Reply = kwargs.get("Reply", "")
