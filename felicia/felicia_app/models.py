from django.db import models

class category(models.Model):
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to="static/images",default="")
    def __str__(self):
    	return self.category
    
class subcategory(models.Model):
    category = models.ForeignKey(category,on_delete=models.CASCADE)
    subcategory = models.CharField(max_length=100)
    image = models.ImageField(upload_to="static/images",default="")
    def __str__(self):
    	return self.subcategory

class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.ForeignKey(category,on_delete=models.CASCADE)
    subcategory= models.ForeignKey(subcategory,on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='images', default="")

    def __str__(self):
        return self.product_name
        
class Order(models.Model):
    order_id =models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    phone = models.CharField(max_length=100,default="")

    def __iter__(self):
        return [self.order_id,self.items_json,self.amount,self.name,self.email,self.address,self.city,
                self.state,self.zip_code,self.phone]

class OrderUpdate(models.Model):
	update_id = models.AutoField(primary_key=True)
	order_id = models.IntegerField(default="")
	update_desc = models.CharField(max_length=5000)
	timestamp = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.update_desc[0:7] + "..."

class contact(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=50)
    desc = models.CharField(max_length=500)
