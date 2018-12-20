class REVIEW:
    def __init__(self,name,book,book_star,product_name,product_url,\
                 product_star,review,review_len,category1):
        self.name=name
        self.book=book
        self.book_star=book_star
        self.product_name=product_name
        self.product_star=product_star
        self.product_url=product_url

        self.review=review
        self.review_len=review_len
        self.category1=category1

    def to_tuple(self):
        data=(self.name,self.book,self.book_star,self.product_name,self.product_url,\
                 self.product_star,self.review,self.review_len,self.category1)
        return(data)
    



