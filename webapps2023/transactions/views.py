from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from functools import partial
from register.decorators import allow_customer_redirect_admin
from register.models import CustomUser
from .models import Balance, BalanceTransfer, Notification, PaymentRequest
import transactions.constants as constants
from .utils import convert_currency, get_notifications
from .forms import BalanceTransferForm, PaymentRequestForm, PaymentRequestUpdateForm


def create_transfer_and_request_update_notifications(sender, recipient, transfer_obj, request_obj):
    Notification.objects.create(user=sender, type=constants.NotificationType.SND, transfer=transfer_obj)
    Notification.objects.create(user=recipient, type=constants.NotificationType.REC, transfer=transfer_obj)
    Notification.objects.create(user=recipient, type=constants.NotificationType.RQU, request=request_obj)


def create_transfer_notifications(sender, recipient, transfer_obj):
    Notification.objects.create(user=sender, type=constants.NotificationType.SND, transfer=transfer_obj)
    Notification.objects.create(user=recipient, type=constants.NotificationType.REC, transfer=transfer_obj)


def create_request_notification(recipient, notification_type, request_obj):
    Notification.objects.create(user=recipient, type=notification_type, request=request_obj)


def process_transfer(request, form):
    # This block makes no connection/changes to the db, if it fails, simply return an error

    # Fetch sender data and calculate the transaction amount to subtract
    sender_user = request.user
    sender_currency = sender_user.currency

    # Fetch the recipient's data
    recipient_email = form.cleaned_data.get("recipient_email")
    recipient_user = CustomUser.objects.get(email=recipient_email)
    recipient_currency = recipient_user.currency

    # Calculate the amounts to subtract/add in the transaction
    transfer_amount = form.cleaned_data.get("amount")
    transfer_currency = form.cleaned_data.get('currency')

    # Calculate the amount to subtract from the sender's account
    # Convert currencies if needed, otherwise sub_amount = transfer_amount

    sub_amount, conversion_success = convert_currency(transfer_currency, sender_currency, transfer_amount)

    # Handle conversion error
    if not conversion_success:
        messages.error(request,
                       'We encountered some problems with completing your transfer, please try again later.')
        return False

    # Calculate the amount to subtract from the sender's account
    # Convert currencies if needed, otherwise add_amount = transfer_amount

    add_amount, conversion_success = convert_currency(transfer_currency, recipient_currency, transfer_amount)

    # Handle conversion error
    if not conversion_success:
        messages.error(request,
                       'We encountered some problems with completing your transfer, please try again later.')
        return False

    # Obtain qs that'll lock the sender's and recipient's balance record for the time of update
    sender_balance = Balance.objects.select_for_update().get(user=sender_user)
    recipient_balance = Balance.objects.select_for_update().get(user__email=recipient_email)

    # Run this block in transaction, so either the whole transfer is completed,
    # or fully rolled back to maintain integrity
    try:
        with transaction.atomic():

            if sender_balance.amount < sub_amount:
                raise ValueError('Insufficient funds to complete the transfer.')

            sender_balance.amount = sender_balance.amount - sub_amount
            sender_balance.save()

            if (recipient_balance.amount + add_amount) > constants.MAX_AMOUNT:
                raise ValueError(
                    'The amounts involved in this transaction exceed our limits. ' +
                    'Please contact our technical support')
            recipient_balance.amount = recipient_balance.amount + add_amount
            recipient_balance.save()

            bt = form.save()

            # Send out the notifications to the users involved in the transaction
            transaction.on_commit(
                partial(create_transfer_notifications, sender=sender_user, recipient=recipient_user,
                        transfer_obj=bt))

    except IntegrityError:
        # In case the transaction fails at any point, send an error message
        messages.error(request,
                       'We encountered some problems with completing your transfer, please try again later.')
        return False
    except ValueError as e:
        messages.error(request, str(e))
        return False

    return True


def process_request_accepted(request, payment_request_id, sender, recipient, transfer_currency, transfer_amount,
                             description):
    # Calculate the amount to subtract from the sender's account
    # Convert currencies if needed, otherwise sub_amount = transfer_amount

    sub_amount, conversion_success = convert_currency(transfer_currency, sender.currency, transfer_amount)

    # Handle conversion error
    if not conversion_success:
        messages.error(request,
                       'We encountered some problems with completing your transfer, please try again later.')
        return False

    # Calculate the amount to add to the recipient's account
    # Convert currencies if needed, otherwise sub_amount = transfer_amount

    add_amount, conversion_success = convert_currency(transfer_currency, recipient.currency, transfer_amount)

    # Handle conversion error
    if not conversion_success:
        messages.error(request,
                       'We encountered some problems with completing your transfer, please try again later.')
        return False

    # Create the transfer object to store later in the database
    transfer_obj = BalanceTransfer(sender_email=sender.email, recipient_email=recipient.email,
                                   currency=transfer_currency, amount=transfer_amount,
                                   description=description)

    # Obtain qs that'll lock the sender's and recipient's balance record for the time of update
    sender_balance = Balance.objects.select_for_update().get(user=sender)
    recipient_balance = Balance.objects.select_for_update().get(user=recipient)

    # Get the payment request for updates
    pay_request = PaymentRequest.objects.select_for_update().get(id=payment_request_id)

    # Run this block in transaction, so either the whole transfer is completed,
    # or fully rolled back to maintain integrity
    try:
        with transaction.atomic():

            if sender_balance.amount < sub_amount:
                raise ValueError('Insufficient funds to complete the transfer.')

            sender_balance.amount = sender_balance.amount - sub_amount
            sender_balance.save()

            if (recipient_balance.amount + add_amount) > constants.MAX_AMOUNT:
                raise ValueError(
                    'The amounts involved in this transaction exceed our limits. ' +
                    'Please contact our technical support')
            recipient_balance.amount = recipient_balance.amount + add_amount
            recipient_balance.save()

            # Store the transfer object in the database
            transfer_obj.save()

            # Update request status to accepted
            pay_request.status = constants.RequestStatus.ACC
            pay_request.closed_date = timezone.now()
            pay_request.save()

            # Send out the notifications to the users involved in the transaction
            transaction.on_commit(
                partial(create_transfer_and_request_update_notifications, sender=sender,
                        recipient=recipient,
                        transfer_obj=transfer_obj,
                        request_obj=pay_request))

    except IntegrityError:
        # In case the transaction fails at any point, send an error message
        messages.error(request,
                       'We encountered some problems with completing your transfer, please try again later.')
        return False
    except ValueError as e:
        messages.error(request, str(e))
        return False

    return True


@login_required
@allow_customer_redirect_admin
@csrf_protect
def balance_transfer(request):
    if request.method == 'POST':
        form = BalanceTransferForm(request.POST, request=request)

        if form.is_valid():

            if process_transfer(request, form):
                return render(request, "transactions/transfer_success.html",
                              {"user": request.user, "notifications": get_notifications(request.user)})

    else:
        form = BalanceTransferForm(request=request)

    return render(request, "transactions/balance_transfer.html",
                  {"form": form, "user": request.user, "notifications": get_notifications(request.user)})


@login_required
@allow_customer_redirect_admin
@csrf_protect
def payment_request(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST, request=request)

        if form.is_valid():

            # Get the recipient user object
            recipient_email = form.cleaned_data.get('recipient_email')
            recipient = CustomUser.objects.get(email=recipient_email)

            # A flag to check if transaction was successful
            success = False

            # Run this block in a transaction to make sure we only send notification if the request was created.
            try:
                with transaction.atomic():

                    # Create the payment request
                    pr = form.save()

                    success = True

                    # Create a Notification for the target user
                    transaction.on_commit(partial(create_request_notification, recipient=recipient,
                                                  notification_type=constants.NotificationType.REQ,
                                                  request_obj=pr))

            except IntegrityError:
                # In case the transaction fails at any point, send an error message
                messages.error(request,
                               'We encountered some problems with making this request, please try again later.')

            if success:
                return render(request, "transactions/request_success.html",
                              {"user": request.user, "notifications": get_notifications(request.user)})

    else:
        form = PaymentRequestForm(request=request)

    return render(request, "transactions/payment_request.html",
                  {"form": form, "user": request.user, "notifications": get_notifications(request.user)})


@login_required
@allow_customer_redirect_admin
def transactions_list(request):
    user = request.user

    transactions = BalanceTransfer.objects.filter(
        Q(sender_email=user.email) | Q(recipient_email=user.email)).order_by('-created_at')

    transactions_processed = []

    for t in transactions:

        if t.sender_email == user.email:
            other_user_email = t.recipient_email
            sign = False
        else:
            other_user_email = t.sender_email
            sign = True

        tp = {'date': t.created_at.date(),
              'user_email': other_user_email,
              'description': t.description,
              'currency': t.currency,
              'amount': t.amount,
              'sign': sign}

        transactions_processed.append(tp)

    return render(request, 'transactions/transactions_list.html',
                  context={"user": user, "notifications": get_notifications(user),
                           "transactions": transactions_processed})


@login_required
@allow_customer_redirect_admin
def requests_list(request):
    user = request.user

    requests = PaymentRequest.objects.filter(
        Q(sender_email=user.email) | Q(recipient_email=user.email)).order_by('-start_date')

    requests_history = []
    requests_pending = []

    for r in requests:

        if r.sender_email == user.email:  # Request made by the user
            other_user_email = r.recipient_email
            sign = True  # Indicates whether the money is coming in or out
        else:  # Request made to the user
            other_user_email = r.sender_email
            sign = False

        status = constants.RequestStatus(r.status)

        tp = {'pk': r.id,
              'date': r.start_date.date(),
              'user_email': other_user_email,
              'description': r.description,
              'currency': r.currency,
              'amount': r.amount,
              'sign': sign,
              'status': status.label}

        # Check if the request requires users' action
        if not sign and status == constants.RequestStatus.PND:
            requests_pending.append(tp)
        else:
            requests_history.append(tp)

    return render(request, 'transactions/requests_list.html',
                  context={"user": user, "notifications": get_notifications(user), "requests_history": requests_history,
                           "requests_pending": requests_pending})


@login_required
@allow_customer_redirect_admin
@csrf_protect
def request_update_status(request, pk=0):
    user = request.user

    qs = PaymentRequest.objects.filter(id=pk, recipient_email=user.email, closed_date=None)

    if not qs.exists():
        return HttpResponseRedirect(reverse('requests'))

    pr = qs.get(id=pk)

    if request.method == 'POST':

        form = PaymentRequestUpdateForm(request.POST, request=request, payment_request=pr)

        # Check if user has sufficient funds to accept the transfer
        if form.is_valid():

            # NOTICE! We flip the sender and recipient as we're handling the request other way around now

            # Fetch sender and recipient data
            sender_user = request.user

            # Fetch the recipient's data
            recipient_email = pr.sender_email
            recipient_user = CustomUser.objects.get(email=recipient_email)

            if 'request_accept' in request.POST:  # Payment Request Accepted

                # Process the accepted request transaction
                # ff transaction was completed, show success message
                if process_request_accepted(request, payment_request_id=pr.id, sender=request.user,
                                            recipient=recipient_user,
                                            transfer_currency=pr.currency, transfer_amount=pr.amount,
                                            description=pr.description):
                    return render(request, "transactions/transfer_success.html",
                                  {"user": request.user, "notifications": get_notifications(user)})

            elif 'request_decline' in request.POST:  # Payment Request Declined

                # Get the payment request for updates
                pay_request = PaymentRequest.objects.select_for_update().get(id=pr.id)

                # A flag for transaction completed successfully
                success = False

                # Run this block in a transaction to make sure the notification
                # is sent only if the update was successful
                try:
                    with transaction.atomic():
                        # Update request status to declined
                        pay_request.status = constants.RequestStatus.DEC
                        pay_request.closed_date = timezone.now()
                        pay_request.save()

                        success = True

                        # Send out a request update notification to the users who made the request
                        transaction.on_commit(partial(create_request_notification, recipient=recipient_user,
                                                      notification_type=constants.NotificationType.RQU,
                                                      request_obj=pay_request))

                except IntegrityError:
                    # In case the transaction fails at any point, send an error message
                    messages.error(request,
                                   'We encountered some problems with declining this request, please try again later.')

                if success:
                    return render(request, "transactions/request_declined.html",
                                  {"user": request.user, "notifications": get_notifications(user)})

    else:
        form = PaymentRequestUpdateForm(request=request, payment_request=pr)

    return render(request, 'transactions/request_update_status.html',
                  context={"user": user, "notifications": get_notifications(user), "form": form})
