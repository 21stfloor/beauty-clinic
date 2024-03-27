from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment, CustomUser, Order
import mysql.connector
from datetime import datetime
from django.conf import settings

@receiver(post_save, sender=Order)
def update_dataset(sender, instance, created, **kwargs):
    if not created:  # Check if the instance is not being created
        if instance.ordered and not instance.checkedout:
            update_dataset_with_raw_sql(instance.product.name, instance.quantity,
                                        instance.product.price, 0, instance.date)
            instance.checkedout = True
            instance.save()

def update_dataset_with_raw_sql(product_name, quantity, price, discount, date):
    connection = mysql.connector.connect(
        host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        database=settings.DATABASES['default']['NAME']
    )

    cursor = connection.cursor()

    # Calculate total revenue
    total_revenue = price * quantity

    try:
        formatted_date = datetime.strftime(date, "%m/%d/%Y")
        cursor.execute("INSERT INTO `dataset` (Product, Units_Sold, Total_Revenue, Unit_Price, Order_Date) VALUES (%s, %s, %s, %s, %s)",
                        (product_name, quantity, total_revenue, price, formatted_date))

        # Commit changes
        connection.commit()

    except mysql.connector.Error as error:
        print("Error updating dataset:", error)

    finally:
        cursor.close()
        connection.close()