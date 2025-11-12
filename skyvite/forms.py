from django import forms
from .models import School, Session, SchoolClass, Section, Student, Circular, Notice, FeeAccountMaster


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            "name", "school_code", "board", "address", "city", "state", "pincode",
            "principal_name", "mobile_no", "email",
            "photo", "school_logo", "principal_signature"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter School Name"}),
            "school_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter School Code"}),
            "board": forms.Select(attrs={"class": "form-control"}),  # ✅ fixed
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter Address"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter City"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter State"}),
            "pincode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Pincode"}),
            "principal_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Principal Name"}),
            "mobile_no": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Mobile Number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter Email"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "school_logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "principal_signature": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

        
class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 2025-26"}),
        }


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ["name", "session"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Class Name"}),
            "session": forms.Select(attrs={"class": "form-control"}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["name", "school_class"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Section Name"}),
            "school_class": forms.Select(attrs={"class": "form-control"}),
        }

from django import forms
from .models import Student, Session, SchoolClass, Section


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            # Basic Info
            "admission_number", "admission_date", "first_name", "surname", "gender", "dob",
            "blood_group", "house", "religion", "category", "contact_no", "email",

            # Session & Class
            "session", "student_class", "section", "roll_no", "status",

            # Profile Pic
            "profilepic",

            # Parents Info
            "father_name", "father_phone", "father_email", "father_occupation",
            "mother_name", "mother_phone", "mother_email", "mother_occupation",

            # Previous School
            "previous_school_name", "previous_school_address",

            # Address
            "address", "state", "pincode",

            # Transport
            "transport_route", "vehicle_no", "pickup_point",

            # Bank
            "bank_name", "account_no", "branch", "ifsc_code",

            # Documents
            "aadhar", "pan", "marksheet", "tc", "character_certificate",
        ]

        widgets = {
            "dob": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "admission_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "session": forms.Select(attrs={"class": "form-control"}),
            "student_class": forms.Select(attrs={"class": "form-control"}),
            "section": forms.Select(attrs={"class": "form-control"}),
            "state": forms.Select(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "previous_school_address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        school = kwargs.pop("school", None)
        super().__init__(*args, **kwargs)

        # If user (dashboard form)
        if user:
            self.fields["session"].queryset = Session.objects.filter(created_by=user)
            self.fields["student_class"].queryset = SchoolClass.objects.filter(created_by=user)
            self.fields["section"].queryset = Section.objects.filter(created_by=user)

        # If school (public registration)
        elif school:
            self.fields["session"].queryset = Session.objects.filter(created_by=school.created_by)
            self.fields["student_class"].queryset = SchoolClass.objects.filter(created_by=school.created_by)
            self.fields["section"].queryset = Section.objects.filter(created_by=school.created_by)

        # If neither (default empty)
        else:
            self.fields["session"].queryset = Session.objects.none()
            self.fields["student_class"].queryset = SchoolClass.objects.none()
            self.fields["section"].queryset = Section.objects.none()


class CircularForm(forms.ModelForm):
    class Meta:
        model = Circular
        fields = ['title', 'description', 'posted_date', 'valid_upto', 'is_published']
        widgets = {
            'posted_date': forms.DateInput(attrs={'type': 'date'}),
            'valid_upto': forms.DateInput(attrs={'type': 'date'}),
        }


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "description", "for_class", "target_group"]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter notice title",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter notice description",
                    "rows": 4,
                    "required": True,
                }
            ),
            "for_class": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter class (optional)",
                }
            ),
            "target_group": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True,
                }
            ),
        }


    # FEE MANAGEMENT SYSTEM
    # 1. ACCOUNT MASTER

class FeeAccountMasterForm(forms.ModelForm):
    class Meta:
        model = FeeAccountMaster
        fields = [
            "account_name",
            "account_type",
            "report_header_name",
            "receipt_logo",
            "receipt_address",
            "description",
        ]

        widgets = {
            "account_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Account Name"
            }),
            "account_type": forms.Select(attrs={
                "class": "form-control",
            }),
            "report_header_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Report Header Name"
            }),
            "receipt_logo": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "receipt_address": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter Receipt Address",
                "rows": 2
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter Description (optional)",
                "rows": 3
            }),
        }

    def clean_account_name(self):
        name = self.cleaned_data["account_name"].strip()
        if FeeAccountMaster.objects.filter(account_name__iexact=name).exists():
            raise forms.ValidationError("An account with this name already exists.")
        return name