from core.models import PrimaryUUIDTimeStampedModel
from django.db import models

from businesses.constants import CATEGORY_CHOICES, ORDER_STATUS_CHOICES


class Business(PrimaryUUIDTimeStampedModel):
    name = models.CharField(max_length=255)

    gstin = models.CharField(max_length=15, null=True, blank=True)

    category = models.CharField(
        max_length=12, choices=CATEGORY_CHOICES, default="laboratory"
    )

    owner = models.OneToOneField(
        "users.EmailUser",
        related_name="business",
        on_delete=models.CASCADE,
    )

    is_active = models.BooleanField(default=True)

    connected_businesses = models.ManyToManyField(
        "businesses.Business",
        related_name="business",
        blank=True,
        through="BusinessConnect",
    )

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        verbose_name = "Business"
        verbose_name_plural = "Businesses"


class BusinessEmployee(PrimaryUUIDTimeStampedModel):

    business = models.ForeignKey(
        "businesses.Business",
        related_name="employees",
        on_delete=models.CASCADE,
    )
    employee = models.OneToOneField(
        "users.EmailUser",
        related_name="employer",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.business} - {self.employee}"

    class Meta:
        verbose_name = "Business Employee"
        verbose_name_plural = "Business Employees"


class BusinessContact(PrimaryUUIDTimeStampedModel):
    contact_type_choices = (
        ("mobile", "mobile"),
        ("landline", "landline"),
        ("email", "email"),
    )

    business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="contacts"
    )

    contact = models.CharField(max_length=255)
    contact_type = models.CharField(
        max_length=255, choices=contact_type_choices, default="mobile"
    )

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.business} - {self.contact}"

    class Meta:
        verbose_name = "Business Contact"
        verbose_name_plural = "Business Contacts"


class BusinessAddress(PrimaryUUIDTimeStampedModel):
    ADDRESS_CHOICES = [
        ("headquarters", "headquarters"),
        ("branch", "branch"),
    ]
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)
    address_type = models.CharField(
        max_length=12, choices=ADDRESS_CHOICES, default="headquarters"
    )

    business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="addresses"
    )

    state = models.ForeignKey(
        "core.State", on_delete=models.PROTECT, related_name="addresses"
    )

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.business} - {self.address_type}"

    class Meta:
        verbose_name = "Business Address"
        verbose_name_plural = "Business Addresses"
        ordering = ["business", "address_type"]


class BusinessAccount(PrimaryUUIDTimeStampedModel):

    BANK_ACCOUNT_TYPE_CHOICES = [
        ("current", "current"),
        ("savings", "savings"),
    ]
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=11)
    account_type = models.CharField(
        max_length=255, default="current", choices=BANK_ACCOUNT_TYPE_CHOICES
    )

    business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="accounts"
    )

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.business} - {self.account_type}"

    class Meta:
        verbose_name = "Business Account"
        verbose_name_plural = "Business Accounts"


class BusinessConnect(PrimaryUUIDTimeStampedModel):
    dentist = models.ForeignKey(
        "businesses.Business", related_name="dentists", on_delete=models.CASCADE
    )
    laboratory = models.ForeignKey(
        "businesses.Business",
        related_name="laboratories",
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.business} - {self.account_type}"

    class Meta:
        verbose_name = "Business Connect"
        verbose_name_plural = "Business Connects"


class OrderStatus(PrimaryUUIDTimeStampedModel):

    status = models.CharField(
        max_length=255, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    order = models.ForeignKey(
        "businesses.Order", on_delete=models.CASCADE, related_name="order_statuses"
    )
    user = models.ForeignKey(
        "users.EmailUser", on_delete=models.CASCADE, related_name="order_statuses"
    )

    def __str__(self):
        return f"{self.order} - {self.status}"

    class Meta:
        verbose_name = "Order Status"
        verbose_name_plural = "Order Statuses"


class Order(PrimaryUUIDTimeStampedModel):
    # work field needs to be added to this model
    # Need to ask mahendra - what is tooth shade??

    doctor_name = models.CharField(max_length=255)

    patient_name = models.CharField(max_length=255)
    patient_age = models.PositiveIntegerField()

    referrer = models.CharField(max_length=255, null=True, blank=True)

    delivery_date = models.DateTimeField()

    notes = models.TextField(null=True, blank=True)

    options = models.ManyToManyField("core.OrderOption", related_name="orders")

    is_urgent = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    teeth = models.JSONField()
    # upper_left_1 = models.BooleanField(default=False, verbose_name="UL1")
    # upper_right_1 = models.BooleanField(default=False, verbose_name="UR1")
    # lower_left_1 = models.BooleanField(default=False, verbose_name="LL1")
    # lower_right_1 = models.BooleanField(default=False, verbose_name="LR1")

    latest_status = models.CharField(
        max_length=255, choices=ORDER_STATUS_CHOICES, default="pending"
    )

    from_business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="orders_created"
    )

    from_user = models.ForeignKey(
        "users.EmailUser", on_delete=models.CASCADE, related_name="orders_created"
    )

    to_business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="orders_received"
    )

    to_user = models.ForeignKey(
        "users.EmailUser", on_delete=models.CASCADE, related_name="orders_received"
    )

    def __str__(self):
        return f"Order - {self.id}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
