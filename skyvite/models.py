from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# ----------------------------
# School Model
# ----------------------------
class School(models.Model):
    BOARD_CHOICES = [
        ("CBSE", "CBSE"),
        ("ICSE", "ICSE"),
        ("IB", "IB"),
        ("STATE", "Other State Board"),
    ]

    # Step 1 — Basic School Info
    board = models.CharField(max_length=50, choices=BOARD_CHOICES)
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    school_code = models.CharField(max_length=20, unique=True)

    # Step 2 — Principal Details
    principal_name = models.CharField(max_length=150)
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField()

    # Step 3 — Media Uploads
    photo = models.ImageField(upload_to="schools/photos/", blank=True, null=True)
    school_logo = models.ImageField(upload_to="schools/logos/", blank=True, null=True)
    principal_signature = models.ImageField(upload_to="schools/signatures/", blank=True, null=True)

    # Ownership
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="schools",
        help_text="The user who created this school record."
    )

    # Meta Info
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "School"
        verbose_name_plural = "Schools"

    def __str__(self):
        return f"{self.name} ({self.board})"

    def save(self, *args, **kwargs):
        # Auto uppercase school code for consistency
        if self.school_code:
            self.school_code = self.school_code.upper()
        super().save(*args, **kwargs)

# ----------------------------
# Session Model
# ----------------------------
class Session(models.Model):
    name = models.CharField(max_length=100)  # e.g., "2025-26"
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "created_by")

    def __str__(self):
        return self.name


# ----------------------------
# SchoolClass Model
# ----------------------------
class SchoolClass(models.Model):
    name = models.CharField(max_length=200)  # e.g., "Class VI"
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="classes")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "session", "created_by")

    def __str__(self):
        return f"{self.name} ({self.session.name})"


# ----------------------------
# Section Model
# ----------------------------
class Section(models.Model):
    name = models.CharField(max_length=50)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="sections")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "school_class", "created_by")

    def __str__(self):
        return f"{self.school_class.name}-{self.name} ({self.school_class.session.name})"


# ----------------------------
# Student Model
# ----------------------------

STATE_CHOICES = [
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Delhi', 'Delhi'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Maharashtra', 'Maharashtra'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    ('Mizoram', 'Mizoram'),
    ('Nagaland', 'Nagaland'),
    ('Odisha', 'Odisha'),
    ('Punjab', 'Punjab'),
    ('Rajasthan', 'Rajasthan'),
    ('Sikkim', 'Sikkim'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Telangana', 'Telangana'),
    ('Tripura', 'Tripura'),
    ('Uttar Pradesh', 'Uttar Pradesh'),
    ('Uttarakhand', 'Uttarakhand'),
    ('West Bengal', 'West Bengal'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
]


class Student(models.Model):
    registration_no = models.CharField(max_length=50, unique=True, editable=False, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    admission_number = models.CharField(max_length=20, unique=True, blank=False, null=False)
    roll_no = models.CharField(max_length=20, blank=True, null=True)
    admission_date = models.DateField(blank=True, null=True)
    admission_status = models.CharField(
        max_length=20,
        choices=[('Registered', 'Registered'), ('Admitted', 'Admitted')],
        default='Registered'
    )
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)




    # Contact and Address
    contact_no = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    # Other Info
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    house = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)

    # Parent Info
    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    father_email = models.EmailField(blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)

    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_email = models.EmailField(blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)

    # Last School Info
    previous_school_name = models.CharField(max_length=255, blank=True, null=True)
    previous_school_address = models.TextField(blank=True, null=True)

    # Transport
    transport_route = models.CharField(max_length=200, blank=True, null=True)
    vehicle_no = models.CharField(max_length=50, blank=True, null=True)
    pickup_point = models.CharField(max_length=200, blank=True, null=True)

    # Bank details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_no = models.CharField(max_length=50, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    # Documents
    aadhar = models.FileField(upload_to="documents/aadhar/", blank=True, null=True)
    pan = models.FileField(upload_to="documents/pan/", blank=True, null=True)
    marksheet = models.FileField(upload_to="documents/marksheet/", blank=True, null=True)
    tc = models.FileField(upload_to="documents/tc/", blank=True, null=True)
    character_certificate = models.FileField(upload_to="documents/character_certificate/", blank=True, null=True)

    # Profile picture
    profilepic = models.FileField(upload_to="profilepics/", blank=True, null=True)

    # Status (Active / Inactive)
    status = models.CharField(
        max_length=20,
        choices=(('active', 'Active'), ('inactive', 'Inactive')),
        default='active'
    )

    # Foreign keys
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    student_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





    def __str__(self):
        return f"{self.first_name} {self.surname}"

    @property
    def has_image(self):
        return bool(self.profilepic and hasattr(self.profilepic, 'url'))


class Circular(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    circular_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_date = models.DateField()
    valid_upto = models.DateField()
    is_published = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "circular_id")  # each user has their own sequence

    def __str__(self):
        return f"{self.user.username} - Circular {self.circular_id}"


class Notice(models.Model):
    ROLE_CHOICES = [
        ('students', 'Students'),
        ('parents', 'Parents'),
        ('teachers', 'Teachers'),
        ('admin', 'Admin'),
        ('specific_students', 'Specific Students'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    for_class = models.CharField(max_length=50, blank=True, null=True)
    target_group = models.CharField(max_length=50, choices=ROLE_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

        #FEE MANAGEMENT SYSTEM


    # 1. ACCOUNT MASTER  // main acc details for fee collection


class FeeAccountMaster(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("Income", "Income"),
        ("Expense", "Expense"),
    ]

    # Basic Info
    account_name = models.CharField(max_length=150, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)

    # Receipt / Report Details
    report_header_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Name to display on fee receipts"
    )
    receipt_logo = models.ImageField(
        upload_to="fee_receipts/logos/", 
        blank=True, 
        null=True, 
        help_text="Logo for receipts"
    )
    receipt_address = models.TextField(
        blank=True, 
        null=True, 
        help_text="Address to show on receipt footer"
    )

    # System fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.account_name} ({self.account_type})"



