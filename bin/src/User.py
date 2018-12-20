class User:
    def __init__(self,_id,name,book,book_star,url):
        self.id=_id
        self.name=name
        self.book=book
        self.book_star=book_star
        self.url=url

    def to_tuple(self):
        data=(self.id,self.name,self.book,self.book_star,self.url)
        return(data)
    



