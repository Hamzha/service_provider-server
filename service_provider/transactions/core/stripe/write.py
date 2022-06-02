import stripe
from configuration import STRIP_API_KEY
import stripe
stripe.api_key=STRIP_API_KEY


def stripe_create_charge(amount,customer_id,payment_method_id,meta_data):
    try:
        result=stripe.PaymentIntent.create(
            amount=(int(amount*100)),
            currency='usd',
            customer=customer_id,
            payment_method=payment_method_id,
            off_session=True,
            confirm=True,
            metadata=meta_data
        )
        return {
            'status':200,
            'data':result,
            'exception':None
        }
    except stripe.error.CardError as e:
        return {
            'status':404,
            'data':None,
            'exception':[e.user_message]
        }
    except BaseException as e:
        return {
            'status':500,
            'data':None,
            'exception':["Transaction failed !!"]
        }  


def stripe_create_payment_method(type,card_number,exp_month,exp_year,cvc):
    try:
        payment_method=stripe.PaymentMethod.create(
            type=type,
            card={
                "number": "4242424242424242", #hardcoded for testing purpose
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc,
            },
        ) 
        return {
            'status':200,
            'data':payment_method,
            'exception':None
        }
    except stripe.error.CardError as e:
        return {
            'status':404,
            'data':None,
            'exception':[e.user_message]
        }
    except BaseException as e:
        return {
            'status':500,
            'data':None,
            'exception':["Something went wrong while creating payment method"]
        }  

def stripe_attach_payment_method(customer_id,payment_method_id):
    try: 
        attached_payment_method=stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id,
        )
        return {
            'status':200,
            'data':attached_payment_method,
            'exception':None
        }
    except BaseException as e:
        return {
            'status':500,
            'data':None,
            'exception':["Something went wrong while creating payment method"]
        }

def stripe_detach_payment_method(payment_method_id):
    try:
        result=stripe.PaymentMethod.detach(
            payment_method_id,
        )
        return {
            'status':200,
            'data':result,
            'exception':None
        }
    except BaseException as e:
        return {
            'status':500,
            'data':None,
            'exception':["Something went wrong while deleting payment method"]
        }

def stripe_update_payment_detail(payment_method_id,exp_month,exp_year):
    try:
        result=stripe.PaymentMethod.modify(
            payment_method_id,
            # metadata={"order_id": "6735"},
            card={'exp_month':exp_month,'exp_year':exp_year}
        )
        return {
            'status':200,
            'data':result,
            'exception':None
        }
    except stripe.error.CardError as e:
        return {
            'status':404,
            'data':None,
            'exception':[e.user_message]
        }        
    except BaseException as e:
        return {
            'status':500,
            'data':None,
            'exception':["Something went wrong while updating payment detail"]
        }
