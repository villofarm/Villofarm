from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .models import Session, SchoolClass, Section, Student, School, Circular, Notice, FeeAccountMaster
from django.contrib import messages
from .forms import SessionForm, SchoolClassForm, SectionForm, StudentForm, SchoolForm, CircularForm, NoticeForm, FeeAccountMasterForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CircularSerializer
from django.utils.timezone import now
import os
from django.template.loader import render_to_string
from datetime import date
import pdfkit
import textwrap
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from .models import School
from .forms import SchoolForm
from django.views.decorators.csrf import csrf_exempt
import hashlib
import random
import string
from django.shortcuts import render, redirect
from django.http import HttpResponse
# ---------------- AUTH VIEWS ----------------
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match ❌')
            return render(request, 'signup.html', {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists ❌')
            return render(request, 'signup.html', {'email': email, 'first_name': first_name, 'last_name': last_name})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered ❌')
            return render(request, 'signup.html', {'username': username, 'first_name': first_name, 'last_name': last_name})

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()
        messages.success(request, 'Account created successfully 🎉 Please sign in.')
        return redirect('signin')

    return render(request, 'signup.html')

def signin_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials ❌')
            return redirect('signin')

    return render(request, 'signin.html')


@login_required(login_url='signin')
def dashboard_view(request):
    # Fetch all records created by the logged-in user
    students = Student.objects.filter(created_by=request.user)
    classes = SchoolClass.objects.filter(created_by=request.user)
    sections = Section.objects.filter(created_by=request.user)
    school = School.objects.filter(created_by=request.user).first()
    if not school:
        messages.warning(request, "Please create your school to access the dashboard.")
        return redirect("add_school")  # redirect to add school
    # 🎂 Today's date
    today = timezone.now().date()

    # 🎉 Filter students whose DOB matches today's month and day
    todays_birthdays = students.filter(
        dob__month=today.month,
        dob__day=today.day
    )

    # Dashboard data
    context = {
        "total_students": students.count(),
        "total_classes": classes.count(),
        "total_sections": sections.count(),
        "school": school,
        "todays_birthdays": todays_birthdays,  # 👈 Added this
    }

    return render(request, "dashboard.html", context)


@login_required(login_url='signin')
def signout_view(request):
    logout(request)
    return redirect('signin')


# ---------------- CLASS & SECTION MANAGEMENT ----------------
@login_required(login_url='signin')
def class_section_view(request):
    session_form = SessionForm()
    class_form = SchoolClassForm()
    section_form = SectionForm()

    if request.method == "POST":
        if "session_submit" in request.POST:
            session_form = SessionForm(request.POST)
            if session_form.is_valid():
                session = session_form.save(commit=False)
                session.created_by = request.user
                session.save()
                messages.success(request, "Session added successfully ✅")
                return redirect("class_section")

        elif "class_submit" in request.POST:
            class_form = SchoolClassForm(request.POST)
            if class_form.is_valid():
                school_class = class_form.save(commit=False)
                school_class.created_by = request.user
                school_class.save()
                messages.success(request, "Class added successfully ✅")
                return redirect("class_section")

        elif "section_submit" in request.POST:
            section_form = SectionForm(request.POST)
            if section_form.is_valid():
                section = section_form.save(commit=False)
                section.created_by = request.user
                section.save()
                messages.success(request, "Section added successfully ✅")
                return redirect("class_section")

    context = {
        "session_form": session_form,
        "class_form": class_form,
        "section_form": section_form,
        "sessions": Session.objects.filter(created_by=request.user),
        "classes": SchoolClass.objects.filter(created_by=request.user),
        "sections": Section.objects.filter(created_by=request.user),
    }
    return render(request, "class_section.html", context)


# AJAX Master to add Session, Class, Section without page reload
@login_required
def ajax_add_session(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if not name:
            return JsonResponse({"success": False, "error": "Session name required"})
        session = Session.objects.create(name=name, created_by=request.user)
        return JsonResponse({
            "success": True,
            "id": session.id,
            "name": session.name,
            "delete_url": f"/delete-session/{session.id}/"
        })


@login_required
def ajax_add_class(request):
    if request.method == "POST":
        name = request.POST.get("name")
        session_id = request.POST.get("session")
        if not name or not session_id:
            return JsonResponse({"success": False, "error": "All fields required"})
        session = Session.objects.get(id=session_id)
        school_class = SchoolClass.objects.create(name=name, session=session, created_by=request.user)
        return JsonResponse({
            "success": True,
            "id": school_class.id,
            "name": school_class.name,
            "delete_url": f"/delete-class/{school_class.id}/"
        })


@login_required
def ajax_add_section(request):
    if request.method == "POST":
        name = request.POST.get("name")
        class_id = request.POST.get("school_class")
        if not name or not class_id:
            return JsonResponse({"success": False, "error": "All fields required"})
        school_class = SchoolClass.objects.get(id=class_id)
        section = Section.objects.create(name=name, school_class=school_class, created_by=request.user)
        return JsonResponse({
            "success": True,
            "id": section.id,
            "name": str(section),
            "delete_url": f"/delete-section/{section.id}/"
        })
    
@login_required
@csrf_exempt
def ajax_delete_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("id")
        item_type = data.get("type")

        try:
            if item_type == "session":
                Session.objects.get(id=item_id, created_by=request.user).delete()
            elif item_type == "class":
                SchoolClass.objects.get(id=item_id, created_by=request.user).delete()
            elif item_type == "section":
                Section.objects.get(id=item_id, created_by=request.user).delete()
            else:
                return JsonResponse({"success": False, "error": "Invalid type"})
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
        



# ---------------- DELETE VIEWS ----------------
@login_required(login_url='signin')
def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, created_by=request.user)
    session.delete()
    messages.success(request, "Session deleted successfully 🗑️")
    return redirect("class_section")


@login_required(login_url='signin')
def delete_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id, created_by=request.user)
    school_class.delete()
    messages.success(request, "Class deleted successfully 🗑️")
    return redirect("class_section")


@login_required(login_url='signin')
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id, created_by=request.user)
    section.delete()
    messages.success(request, "Section deleted successfully 🗑️")
    return redirect("class_section")


# ---------------- STUDENT MANAGEMENT ----------------
@login_required(login_url='signin')
def add_student_view(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            student = form.save(commit=False)
            student.created_by = request.user
            student.save()
            messages.success(request, "Student added successfully ✅")
            return redirect("student_list")
        else:
            print(form.errors)  # <-- DEBUG: shows what is wrong
            messages.error(request, "Error adding student ❌")
    else:
        form = StudentForm(user=request.user)

    return render(request, "add_student.html", {"form": form})




@login_required(login_url='signin')
def student_list_view(request):
    students = Student.objects.filter(created_by=request.user).order_by('-id')
    total_students = Student.objects.filter(created_by=request.user).count()
    total_classes = SchoolClass.objects.filter(created_by=request.user).count()
    total_sections = Section.objects.filter(created_by=request.user).count()
    school = School.objects.get(created_by=request.user)  # if you have a School model

    context = {
        "students": students,
        "total_students": total_students,
    }

    return render(request, "student_list.html", context)

    


@login_required(login_url='signin')
def view_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id, created_by=request.user)
    return render(request, 'view_student.html', {'student': student})


@login_required(login_url='signin')
def edit_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id, created_by=request.user)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student, user=request.user)
        if form.is_valid():
            student = form.save(commit=False)
            student.created_by = request.user
            student.save()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": True})
            return redirect("student_list")
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = StudentForm(instance=student, user=request.user)

    return render(request, "partials/student_form.html", {"form": form})



@login_required(login_url='signin')
def delete_student_view(request, student_id):
    if request.method == "POST":
        student = get_object_or_404(Student, id=student_id, created_by=request.user)
        student.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

# Gender wise count
@login_required(login_url='signin')
def gender_data(request):
    students = Student.objects.filter(created_by=request.user)
    male_count = students.filter(gender__iexact='Male').count()
    female_count = students.filter(gender__iexact='Female').count()
    # other_count = students.filter(gender__iexact='Other').count()
    
    data = {
        'labels': ['Male', 'Female',],
        'counts': [male_count, female_count],
    }
    return JsonResponse(data)




# ---------------- AJAX DROPDOWNS ----------------
@login_required(login_url='signin')
def get_classes(request, session_id):
    classes = SchoolClass.objects.filter(created_by=request.user, session_id=session_id)
    data = [{"id": c.id, "name": c.name} for c in classes]
    return JsonResponse(data, safe=False)


@login_required(login_url='signin')
def get_sections(request, class_id):
    sections = Section.objects.filter(created_by=request.user, school_class_id=class_id)
    data = [{"id": s.id, "name": s.name} for s in sections]
    return JsonResponse(data, safe=False)




@login_required(login_url="signin")
def add_school_view(request):
    # ✅ Prevent multiple schools per user
    if School.objects.filter(created_by=request.user).exists():
        messages.warning(request, "You already created a school. You cannot add another one ❌")
        return redirect('dashboard')

    if request.method == "POST":
        # ✅ Collect data from multi-step form manually
        data = {
            'board': request.POST.get('board'),
            'name': request.POST.get('name'),
            'address': request.POST.get('address'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'pincode': request.POST.get('pincode'),
            'principal_name': request.POST.get('principal_name'),
            'mobile_no': request.POST.get('mobile_no'),
            'email': request.POST.get('email'),
            'school_code': request.POST.get('school_code'),  # ✅ fixed here
        }
        files = {
            'photo': request.FILES.get('photo'),
            'school_logo': request.FILES.get('school_logo'),
            'principal_signature': request.FILES.get('signature'),
        }

        form = SchoolForm(data, files)
        if form.is_valid():
            school = form.save(commit=False)
            school.created_by = request.user
            school.save()
            messages.success(request, "🎉 School added successfully!")
            return redirect('dashboard')
        else:
            print("❌ Form errors:", form.errors)  # ✅ Debug
            messages.error(request, "Please correct the errors below ❌")
    else:
        form = SchoolForm()

    return render(request, 'add_school.html', {'form': form})


@login_required
def school_detail_view(request):
    school = get_object_or_404(School, created_by=request.user)
    form = SchoolForm(instance=school)
    return render(request, "school_detail.html", {"school": school, "form": form})


@login_required
def update_school_ajax(request):
    """Handles AJAX school update from the modal."""
    if request.method == "POST":
        school = get_object_or_404(School, created_by=request.user)
        form = SchoolForm(request.POST, request.FILES, instance=school)

        if form.is_valid():
            updated_school = form.save()

            return JsonResponse({
                "success": True,
                "data": {
                    "name": updated_school.name,
                    "school_code": updated_school.school_code,
                    "board": updated_school.board,
                    "address": updated_school.address,
                    "city": updated_school.city,
                    "state": updated_school.state,
                    "pincode": updated_school.pincode,
                    "principal_name": updated_school.principal_name,
                    "mobile_no": updated_school.mobile_no,
                    "email": updated_school.email,
                    "photo_url": updated_school.photo.url if updated_school.photo else None,
                    "logo_url": updated_school.school_logo.url if updated_school.school_logo else None,
                    "signature_url": updated_school.principal_signature.url if updated_school.principal_signature else None,
                }
            })

        return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


@user_passes_test(lambda u: u.is_superuser)
def delete_school_view(request, school_id):
    school = get_object_or_404(School, id=school_id)
    school.delete()
    messages.success(request, "School deleted successfully ✅")
    return redirect("dashboard")

# ---------------- CERTIFICATES ----------------
def certificate_panel(request):
    action = request.GET.get('action')

    # -----------------------------
    # 🔹 FETCH STUDENTS FOR FILTER
    # -----------------------------
    if action == 'get_students':
        class_id = request.GET.get('class_id')
        section_id = request.GET.get('section_id')
        admission_no = request.GET.get('admission_no')

        students = Student.objects.all().order_by('first_name')

        if class_id:
            students = students.filter(student_class_id=class_id)
        if section_id:
            students = students.filter(section_id=section_id)
        if admission_no:
            students = students.filter(admission_number__icontains=admission_no)

        data = [
            {
                "id": s.id,
                "name": f"{s.first_name} {s.surname or ''}".strip(),
                "admission_no": s.admission_number,
            }
            for s in students
        ]
        return JsonResponse(data, safe=False)

    # -----------------------------
    # 🔹 GET CERTIFICATE PREVIEW
    # -----------------------------
    if action == 'get_certificate':
        student_id = request.GET.get('student_id')
        cert_type = request.GET.get('cert_type')
        student = get_object_or_404(Student, id=student_id)
        school = School.objects.filter(created_by=request.user).first()

        html = render_to_string(
            f'certificates/{cert_type}.html',
            {
                'student': student,
                'school': school,
                'logo_url': school.school_logo.url if school and school.school_logo else '',
            }
        )
        return JsonResponse({"html": html})

    # -----------------------------
    # 🔹 DEFAULT PAGE RENDER
    # -----------------------------
    classes = SchoolClass.objects.all()
    sections = Section.objects.all()
    return render(request, 'certificate_panel.html', {'classes': classes, 'sections': sections})

def print_certificate(request, student_id, cert_type):
    student = get_object_or_404(Student, id=student_id)
    school = School.objects.first()  # Or however you're fetching the current school

    context = {
        'student': student,
        'school': school,
        'today': date.today().strftime('%d/%m/%Y'),
    }

    return render(request, f'certificates/{cert_type}.html', context)


@login_required(login_url='signin')
def student_list_print(request):
    students = Student.objects.filter(created_by=request.user)
    total_students = students.count()

    try:
        school = School.objects.get(created_by=request.user)
    except School.DoesNotExist:
        school = None

    return render(request, 'student_list_print.html', {
        'students': students,
        'total_students': total_students,
        'school': school,
    })

# Admission Form
@login_required(login_url='signin')
def admission_form_view(request):
    school = School.objects.filter(created_by=request.user).first()

    html = render_to_string(
        'admission_form.html',
        {
            'school': school,
            'logo_url': school.school_logo.url if school and school.school_logo else '',
        }
    )
    return JsonResponse({"html": html})





@login_required(login_url='signin')
def manage_circulars(request):
    # Newest first
    circulars = Circular.objects.filter(user=request.user).order_by('-posted_date')

    if request.method == 'POST':
        title = request.POST.get("title")
        description = request.POST.get("description")
        posted_date = request.POST.get("posted_date")
        valid_upto = request.POST.get("valid_upto")
        is_published = request.POST.get("is_published") == "on"

        # ✅ Generate circular_id per user
        last_circular = Circular.objects.filter(user=request.user).order_by('-circular_id').first()
        next_id = last_circular.circular_id + 1 if last_circular else 1

        Circular.objects.create(
            user=request.user,
            circular_id=next_id,
            title=title,
            description=description,
            posted_date=posted_date,
            valid_upto=valid_upto,
            is_published=is_published
        )

        messages.success(request, f"Circular #{next_id} added successfully ✅")
        return redirect("manage-circular")

    return render(request, "manage_circular.html", {
        "circulars": circulars,
    })


@api_view(['GET'])
def circular_list_api(request, user_id):
    circulars = Circular.objects.filter(
        user_id=user_id,
        is_published=True,
        valid_upto__gte=now()
    ).order_by('-posted_date')
    serializer = CircularSerializer(circulars, many=True)
    return Response(serializer.data)

def enter_school_code(request):
    """Step 1 — Ask for school code and redirect to registration form"""
    if request.method == "POST":
        school_code = request.POST.get("school_code", "").strip().upper()

        if not school_code:
            messages.error(request, "Please enter your school code.")
            return redirect("enter_school_code")

        if not School.objects.filter(school_code__iexact=school_code).exists():
            messages.error(request, "Invalid school code. Please try again.")
            return redirect("enter_school_code")

        return redirect("public_student_registration", school_code=school_code)

    return render(request, "enter_school_code.html")


@csrf_exempt
def public_student_registration(request, school_code):
    try:
        school = School.objects.get(school_code__iexact=school_code)
    except School.DoesNotExist:
        if request.is_ajax():
            return JsonResponse({"success": False, "errors": {"school_code": ["Invalid school code."]}})
        messages.error(request, "Invalid school code.")
        return redirect("enter_school_code")

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, school=school)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = school
            student.created_by = school.created_by
            student.save()
            if request.is_ajax():
                return JsonResponse({"success": True})
            messages.success(request, "Registration submitted successfully!")
            return redirect("public_student_registration", school_code=school_code)
        else:
            print("Form errors:", form.errors)
            if request.is_ajax():
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
            messages.error(request, "Please fix the errors in the form.")
    else:
        form = StudentForm(school=school)

    return render(request, "student_registration.html", {
        "form": form,
        "school": school
    })






















#Fee Payment Testing Views

# PayU credentials and URLs
PAYU_BASE_URL = "https://secure.payu.in/_payment"   # For testing; change to https://secure.payu.in/_payment in production
MERCHANT_KEY = "Y7dA02"
MERCHANT_SALT = "CiFwzWBbusjKD2jz520Ljn9FsjAt8BRY"

def payment_form(request):
    """Display amount input form."""
    return render(request, 'payment_form.html')


def process_payment(request):
    """Handle payment form submission and redirect to PayU."""
    if request.method == "POST":
        amount = request.POST.get("amount")

        # Generate unique transaction ID
        txnid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

        productinfo = "My Product"
        firstname = "Customer"
        email = "customer@example.com"
        phone = "9999999999"

        surl = request.build_absolute_uri('/payment/success/')
        furl = request.build_absolute_uri('/payment/failure/')

        # Prepare hash string
        hash_string = f"{MERCHANT_KEY}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|||||||||||{MERCHANT_SALT}"
        hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()

        context = {
            "action": PAYU_BASE_URL,
            "key": MERCHANT_KEY,
            "txnid": txnid,
            "amount": amount,
            "productinfo": productinfo,
            "firstname": firstname,
            "email": email,
            "phone": phone,
            "surl": surl,
            "furl": furl,
            "hashh": hashh,
            "service_provider": "payu_paisa",
        }

        return render(request, "redirect_to_payu.html", context)
    else:
        return redirect('payment_form')
    
    
def payment_success(request):
    return render(request, "payment_success.html")

def payment_failure(request):
    return render(request, "payment_failure.html")

# Notice Management Views
@login_required(login_url='signin')
def manage_notice(request):
    notices = Notice.objects.filter(created_by=request.user).order_by('-created_at')

    if request.method == "POST":
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            messages.success(request, "Notice added successfully ✅")
            return redirect('manage-notice')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NoticeForm()

    return render(request, "manage_notice.html", {"form": form, "notices": notices})




    #FEE MANAGEMENT SYSTEM


    # 1. ACCOUNT MASTER
    # ✅ List all Fee Account Masters
@login_required(login_url='signin')
def fee_account_master_list(request):
    accounts = FeeAccountMaster.objects.filter(created_by=request.user).order_by('-id')
    return render(request, 'fee_account_master_list.html', {'accounts': accounts})


# ✅ Save (Add/Edit) Fee Account Master via AJAX
@login_required(login_url='signin')
def fee_account_master_save_ajax(request):
    if request.method == "POST":
        acc_id = request.POST.get("id")

        # If updating existing account
        if acc_id:
            account = get_object_or_404(FeeAccountMaster, id=acc_id, created_by=request.user)
            form = FeeAccountMasterForm(request.POST, request.FILES, instance=account)
        else:
            form = FeeAccountMasterForm(request.POST, request.FILES)

        if form.is_valid():
            account = form.save(commit=False)
            account.created_by = request.user
            account.save()

            data = {
                "id": account.id,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "report_header_name": account.report_header_name or "",
                "receipt_address": account.receipt_address or "",
                "receipt_logo": account.receipt_logo.url if account.receipt_logo else "",
                "description": account.description or "",
                "created_at": timezone.localtime(account.created_at).strftime("%d %b %Y, %I:%M %p"),
            }
            return JsonResponse({"success": True, "account": data})
        else:
            errors = form.errors.as_json()
            return JsonResponse({"success": False, "error": errors})

    return JsonResponse({"success": False, "error": "Invalid request"})


# ✅ Delete Fee Account Master via AJAX
@login_required(login_url='signin')
def fee_account_master_delete_ajax(request, pk):
    if request.method == "POST":
        try:
            account = FeeAccountMaster.objects.get(id=pk, created_by=request.user)
            account.delete()
            return JsonResponse({"success": True})
        except FeeAccountMaster.DoesNotExist:
            return JsonResponse({"success": False, "error": "Record not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})