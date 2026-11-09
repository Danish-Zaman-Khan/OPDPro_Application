from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from datetime import date, timedelta
import json

from .models import Invoice, InvoiceItem, Payment
from patients.models import Patient
from appointment.models import Appointment
from settings.models import ClinicSettings, FeeItem


def generate_invoice_number():
    cfg = ClinicSettings.get_settings()
    prefix = cfg.invoice_prefix
    last = Invoice.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"{prefix}-{date.today().strftime('%Y%m')}-{next_id:04d}"


def detect_first_visit(patient):
    return not Invoice.objects.filter(patient=patient).exists()


@login_required
def billing_dashboard(request):
    today = date.today()
    month_start = today.replace(day=1)
    invoices = Invoice.objects.select_related('patient', 'appointment').all()
    context = {
        'total_today':        invoices.filter(invoice_date=today).aggregate(s=Sum('total_amount'))['s'] or 0,
        'total_month':        invoices.filter(invoice_date__gte=month_start).aggregate(s=Sum('total_amount'))['s'] or 0,
        'unpaid_count':       invoices.filter(payment_status='unpaid').count(),
        'unpaid_amount':      invoices.filter(payment_status='unpaid').aggregate(s=Sum('total_amount'))['s'] or 0,
        'recent_invoices':    invoices[:20],
        'fee_items':          FeeItem.objects.filter(is_active=True),
    }
    return render(request, 'billing/dashboard.html', context)


@login_required
def invoice_list(request):
    qs = Invoice.objects.select_related('patient').all()
    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()
    if status: qs = qs.filter(payment_status=status)
    if q:      qs = qs.filter(Q(patient__first_name__icontains=q) | Q(patient__last_name__icontains=q) | Q(invoice_number__icontains=q))
    return render(request, 'billing/invoice_list.html', {'invoices': qs, 'status': status, 'q': q})


@login_required
def create_invoice(request, patient_id=None, appointment_id=None):
    cfg = ClinicSettings.get_settings()
    fee_items = FeeItem.objects.filter(is_active=True)
    patient = get_object_or_404(Patient, pk=patient_id) if patient_id else None
    appointment = get_object_or_404(Appointment, pk=appointment_id) if appointment_id else None
    if appointment and not patient:
        patient = appointment.patient

    is_first = detect_first_visit(patient) if patient else False
    default_fee = cfg.opd_consultation_fee if is_first else cfg.revisit_fee

    if request.method == 'POST':
        data = request.POST
        inv = Invoice.objects.create(
            invoice_number = generate_invoice_number(),
            patient        = get_object_or_404(Patient, pk=data['patient_id']),
            appointment    = Appointment.objects.filter(pk=data.get('appointment_id')).first() if data.get('appointment_id') else None,
            created_by     = request.user,
            invoice_date   = data.get('invoice_date', date.today()),
            discount_amount= data.get('discount', 0) or 0,
            notes          = data.get('notes', ''),
            is_first_visit = is_first,
        )
        # Build line items
        descs = request.POST.getlist('item_desc[]')
        cats  = request.POST.getlist('item_cat[]')
        qtys  = request.POST.getlist('item_qty[]')
        rates = request.POST.getlist('item_rate[]')
        subtotal = 0
        for d, c, q, r in zip(descs, cats, qtys, rates):
            if d and r:
                qty = float(q or 1)
                rate = float(r)
                item = InvoiceItem.objects.create(
                    invoice=inv, description=d, category=c,
                    quantity=qty, unit_rate=rate, amount=qty*rate
                )
                subtotal += item.amount

        inv.subtotal = subtotal
        inv.total_amount = subtotal - float(inv.discount_amount) + float(inv.tax_amount)
        # Record payment if made now
        paid_now = float(data.get('paid_now', 0) or 0)
        if paid_now > 0:
            Payment.objects.create(
                invoice=inv, amount=paid_now,
                mode=data.get('payment_mode', 'cash'),
                reference=data.get('payment_ref', ''),
                received_by=request.user
            )
            inv.amount_paid = paid_now
            if paid_now >= inv.total_amount:
                inv.payment_status = 'paid'
                inv.payment_date = timezone.now()
                inv.payment_mode = data.get('payment_mode', 'cash')
            else:
                inv.payment_status = 'partially_paid'
        inv.save()
        messages.success(request, f"Invoice {inv.invoice_number} created.")
        return redirect('billing:invoice_detail', pk=inv.pk)

    return render(request, 'billing/create_invoice.html', {
        'patient': patient, 'appointment': appointment,
        'cfg': cfg, 'fee_items': fee_items,
        'is_first': is_first, 'default_fee': default_fee,
        'patients': Patient.objects.all().order_by('first_name'),
        'payment_modes': Invoice.PAYMENT_MODE,
    })


@login_required
def invoice_detail(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    return render(request, 'billing/invoice_detail.html', {'invoice': inv})


@login_required
def record_payment(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        mode   = request.POST.get('mode', 'cash')
        ref    = request.POST.get('reference', '')
        Payment.objects.create(invoice=inv, amount=amount, mode=mode, reference=ref, received_by=request.user)
        inv.amount_paid = float(inv.amount_paid) + amount
        if inv.amount_paid >= float(inv.total_amount):
            inv.payment_status = 'paid'
            inv.payment_date = timezone.now()
            inv.payment_mode = mode
        else:
            inv.payment_status = 'partially_paid'
        inv.save()
        messages.success(request, f"Payment of ₹{amount} recorded.")
    return redirect('billing:invoice_detail', pk=pk)


@login_required
def invoice_print(request, pk):
    inv = get_object_or_404(Invoice, pk=pk)
    cfg = ClinicSettings.get_settings()
    return render(request, 'billing/invoice_print.html', {'invoice': inv, 'cfg': cfg})


@login_required
def fee_settings(request):
    if not (request.user.is_staff or request.user.staff_role == 'admin'):
        messages.error(request, "Access denied.")
        return redirect('billing:dashboard')
    cfg = ClinicSettings.get_settings()
    fee_items = FeeItem.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_cfg':
            for field in ['opd_consultation_fee','revisit_fee','emergency_fee','revisit_days','invoice_prefix']:
                setattr(cfg, field, request.POST.get(field, getattr(cfg, field)))
            cfg.invoice_footer_note = request.POST.get('invoice_footer_note', cfg.invoice_footer_note)
            cfg.save()
            messages.success(request, "Fee settings updated.")
        elif action == 'add_fee':
            FeeItem.objects.create(
                name=request.POST['name'], category=request.POST['category'],
                default_rate=request.POST['default_rate'], unit=request.POST.get('unit','per visit'),
                description=request.POST.get('description','')
            )
            messages.success(request, "Fee item added.")
        elif action == 'delete_fee':
            FeeItem.objects.filter(pk=request.POST.get('fee_id')).delete()
            messages.success(request, "Fee item removed.")
        return redirect('billing:fee_settings')
    return render(request, 'billing/fee_settings.html', {'cfg': cfg, 'fee_items': fee_items})
