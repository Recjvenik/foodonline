from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import date, datetime
# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name

    def is_open(self):
        today = date.today().isoweekday()
        current_business_hour = BusinessHour.objects.filter(vendor=self.id, day=today)
    
        current_time = datetime.now().strftime("%H:%M:%S")
        is_open = False

        for hour in current_business_hour:
            if not hour.is_closed:
                start_hour = str(datetime.strptime(hour.from_hour, "%I:%M %p").time())
                end_hour = str(datetime.strptime(hour.to_hour, "%I:%M %p").time())
                if current_time > start_hour and current_time < end_hour:
                    is_open = True
                    break
        
        return is_open
    
    def save(self, *args, **kwargs):
        if self.id is not None:
            original = Vendor.objects.get(id=self.id)
            if original.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved
                }
                if self.is_approved:
                    mail_subject = 'Congretulations!!! Your resturant has been approved'
                    
                    send_notification(mail_subject, mail_template, context)
                else:
                    mail_subject = 'We are sorry!!! Your resturant has been delisted'
                    
                    send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)
    

DAYS = [
    ('', 'Select Day'),
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
    (7, 'Sunday'),
]

HOURS_OF_DAY = [('', 'Select Hour'), ('12:00 AM', '12:00 AM'), ('12:30 AM', '12:30 AM'), ('01:00 AM', '01:00 AM'), ('01:30 AM', '01:30 AM'), ('02:00 AM', '02:00 AM'), ('02:30 AM', '02:30 AM'), ('03:00 AM', '03:00 AM'), ('03:30 AM', '03:30 AM'), ('04:00 AM', '04:00 AM'), ('04:30 AM', '04:30 AM'), ('05:00 AM', '05:00 AM'), ('05:30 AM', '05:30 AM'), ('06:00 AM', '06:00 AM'), ('06:30 AM', '06:30 AM'), ('07:00 AM', '07:00 AM'), ('07:30 AM', '07:30 AM'), ('08:00 AM', '08:00 AM'), ('08:30 AM', '08:30 AM'), ('09:00 AM', '09:00 AM'), ('09:30 AM', '09:30 AM'), ('10:00 AM', '10:00 AM'), ('10:30 AM', '10:30 AM'), ('11:00 AM', '11:00 AM'), ('11:30 AM', '11:30 AM'), ('12:00 PM', '12:00 PM'), ('12:30 PM', '12:30 PM'), ('01:00 PM', '01:00 PM'), ('01:30 PM', '01:30 PM'), ('02:00 PM', '02:00 PM'), ('02:30 PM', '02:30 PM'), ('03:00 PM', '03:00 PM'), ('03:30 PM', '03:30 PM'), ('04:00 PM', '04:00 PM'), ('04:30 PM', '04:30 PM'), ('05:00 PM', '05:00 PM'), ('05:30 PM', '05:30 PM'), ('06:00 PM', '06:00 PM'), ('06:30 PM', '06:30 PM'), ('07:00 PM', '07:00 PM'), ('07:30 PM', '07:30 PM'), ('08:00 PM', '08:00 PM'), ('08:30 PM', '08:30 PM'), ('09:00 PM', '09:00 PM'), ('09:30 PM', '09:30 PM'), ('10:00 PM', '10:00 PM'), ('10:30 PM', '10:30 PM'), ('11:00 PM', '11:00 PM'), ('11:30 PM', '11:30 PM')]

# HOURS_OF_DAY = [(time(h,m).strftime('%I:%M %p'), time(h,m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

class BusinessHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(max_length=10, choices=HOURS_OF_DAY, blank=True)
    to_hour = models.CharField(max_length=10, choices=HOURS_OF_DAY, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', 'from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()