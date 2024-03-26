import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from .exceptions import (
    FailedToCreateToken, 
    FailedToCancelToken, 
    FailedToVerifyToken, 
    FailedToRefundToken
)


class DPOPay:
    CREATE_TOKEN = 'createToken'
    VERIFY_TOKEN = 'verifyToken'
    CANCEL_TOKEN = 'cancelToken'
    REFUND_TOKEN = 'refundToken'

    def __init__(self) -> None:
        self._end_point = settings.DPO_END_POINT
        self._company_token = settings.DPO_COMPANY_TOKEN
        self._currency = settings.DPO_PAYMENT_CURRENCY
        self._payment_url = settings.DPO_PAYMENT_URL
        self._ptl = settings.DPO_PAYMENT_TIME_LIMIT
        self._service_type = settings.DPO_SERVICE_TYPE
        self._company_ref_unique = 0
        self._back_url = None
        self._redirect_url = None
   

    def _get_current_date(self):
        current_datetime = datetime.now()
        return current_datetime.strftime("%Y/%m/%d %H:%M")


    def _parse_xml(self, xml):

        # Parse the XML string
        root = ET.fromstring(xml)

        class_name = root.tag

        # Initialize an empty dictionary to store the extracted data
        attributes = {}

        # Iterate over all child elements of the root
        for child in root:
            # Extract the tag and text of each child element
            tag = child.tag
            text = child.text
            # Store the tag and text in the data dictionary
            attributes[tag] = text

        # Dynamically create a class using type
        pojo_class = type(class_name, (), attributes)

        # Instantiate the dynamically created class
        pojo_instance = pojo_class()

        return pojo_instance
    

    def set_end_point(self, end_point: str):
        self._end_point = end_point


    def set_payment_url(self, payment_url: str):
        self._payment_url = payment_url


    def set_redirect_url(self, redirect_url: str):
        self._redirect_url = redirect_url


    def set_back_url(self, back_url: str):
        self._back_url = back_url


    def set_company_token(self, company_token: str):
        self._company_token = company_token


    def set_service_type(self, service_type: int):
        self._service_type = service_type


    def set_company_ref_unique(self, ref_unique: bool):
        if ref_unique:
            self._company_ref_unique = 1
        else:
            self._company_ref_unique = 0


    def set_currency(self, currency: str):
        self._currency = currency


    def set_ptl(self, ptl: int):
        self._ptl = ptl
    

    def create_token(self, company_ref: str, amount: float, description:str):
        request = self.CREATE_TOKEN
       
        end_point = self._end_point
        company_token = self._company_token
        currency = self._currency
        company_ref_unique = self._company_ref_unique
        ptl = self._ptl
        service_type = self._service_type
        service_date = self._get_current_date()
        redirect_url = self._redirect_url
        back_url = self._back_url

        HEADERS = {'Content-Type': 'application/xml'}

        xml_payload = f'''
        <?xml version="1.0" encoding="utf-8"?>
        <API3G>
            <CompanyToken>{company_token}</CompanyToken>
            <Request>{request}</Request>
            <Transaction>
                <PaymentAmount>{amount}</PaymentAmount>
                <PaymentCurrency>{currency}</PaymentCurrency>
                <CompanyRef>{company_ref}</CompanyRef>
                <RedirectURL>{redirect_url}</RedirectURL>
                <BackURL>{back_url}</BackURL>
                <CompanyRefUnique>{company_ref_unique}</CompanyRefUnique>
                <PTL>{ptl}</PTL>
            </Transaction>
            <Services>
                <Service>
                    <ServiceType>{service_type}</ServiceType>
                    <ServiceDescription>{description}</ServiceDescription>
                    <ServiceDate>{service_date}</ServiceDate>
                </Service>
            </Services>
            <Additional>
                <BlockPayment>BT</BlockPayment>
                <BlockPayment>PP</BlockPayment>
                <BlockPayment>XP</BlockPayment>
            </Additional>
        </API3G>'''
        r = requests.post(url=end_point, data=xml_payload, headers=HEADERS)
        response = self._parse_xml(r.text)
        if not response.Result == "000":
            raise FailedToCreateToken
        return response


    def cancel_token(self, trans_token: str):
        request = self.CANCEL_TOKEN

        company_token = self._company_token
        end_point = self._end_point

        HEADERS = {'Content-Type': 'application/xml'}

        xml_payload = f'''
        <?xml version="1.0" encoding="utf-8"?>
        <API3G>
            <CompanyToken>{company_token}</CompanyToken>
            <Request>{request}</Request>
            <TransactionToken>{trans_token}</TransactionToken>
        </API3G>'''
        r = requests.post(url=end_point, data=xml_payload, headers=HEADERS)
        response = self._parse_xml(r.text)
        if not response.Result == "000":
            raise FailedToCancelToken
        return response


    def make_payment(self, trans_token: str):
        payment_url = self._payment_url
        url = f"{payment_url}?ID={trans_token}"
        return redirect(url)


    def verify_payment(self, trans_token: str):
        request = self.VERIFY_TOKEN

        company_token = self._company_token
        end_point = self._end_point

        HEADERS = {'Content-Type': 'application/xml'}

        xml_payload = f'''
        <?xml version="1.0" encoding="utf-8"?>
        <API3G>
            <CompanyToken>{company_token}</CompanyToken>
            <Request>{request}</Request>
            <TransactionToken>{trans_token}</TransactionToken>
        </API3G>'''
        r = requests.post(url=end_point, data=xml_payload, headers=HEADERS)
        response = self._parse_xml(r.text)
        if not response.Result == "000":
            raise FailedToVerifyToken
        return response
    

    def refund_payment(self, trans_token: str, refund_amount:float):
        request = self.REFUND_TOKEN

        company_token = self._company_token
        end_point = self._end_point

        HEADERS = {'Content-Type': 'application/xml'}

        xml_payload = f'''
        <?xml version="1.0" encoding="utf-8"?>
        <API3G>
            <Request>{request}</Request>
            <CompanyToken>{company_token}</CompanyToken>
            <TransactionToken>{trans_token}</TransactionToken>
            <refundAmount>{refund_amount}</refundAmount>
            <refundDetails>Refund</refundDetails>
        </API3G>'''
        r = requests.post(url=end_point, data=xml_payload, headers=HEADERS)
        response = self._parse_xml(r.text)
        if not response.Result == "000":
            raise FailedToRefundToken
        return response