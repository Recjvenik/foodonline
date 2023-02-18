from datetime import datetime
from vendor.models import Vendor
import simplejson as json

def generate_order_number(pk):
    current_date_time = datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = "-".join((current_date_time, str(pk)))
    return order_number


def order_total_by_vendor(order, vendor_id):
        grand_total = 0
        subtotal = 0
        tax = 0
        tax_dict = {}
        if order.total_data:
            total_data = json.loads(order.total_data)
            data = total_data.get(str(vendor_id))

            
            tax_dict = {}
            for key, val in data.items():
                subtotal += float(key)
                val = val.replace("'",'"')
                val = json.loads(val)
                tax_dict.update(val)

                for i in val:
                    for j in val[i]:
                        tax += float(val[i][j])
        grand_total = float(subtotal)+ float(tax)
        context = {
            'grand_total': grand_total,
            'tax': tax,
            'subtotal': subtotal,
            'tax_data': tax_dict,
        }
        return context