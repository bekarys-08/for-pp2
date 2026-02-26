class Product():
     total=0
     def __init__(self,name,price):
         Product.total+=1
         self.name=name 
         self.price=price

     def Getinfo(self):
          return f"Name:{self.name} price:{self.price}"
     def TotalProduct(self):
          
          return Product.total
          


class DigitalProduct(Product):
     def __init__(self,name,price,filesize):
          super().__init__(name,price)
          self.filesize=filesize
     def digitalGetinfo(self):
          return f"{super().Getinfo()},size:{self.filesize}"
          

class PhysycalProduct(Product):
     def __init__(self,name,price,weight):
          super().__init__(name,price)
          self.weight=weight
     def physycalGetinfo(self):
          return f"{super().Getinfo()},weight:{self.weight}"
     
product=Product("ball",1000)
digital=DigitalProduct("beka",100,3)
physycal=PhysycalProduct("milk",600,1000)

print(product.Getinfo())
print(digital.digitalGetinfo())
print(physycal.physycalGetinfo())
print(product.TotalProduct(