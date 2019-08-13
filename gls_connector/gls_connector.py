from array import array
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, datetime
import hashlib
from suds.client import Client


# Domain


@dataclass
class PackageSender:
    name: str
    street: str
    city: str
    zip_code: str
    country_code: str
    contact: str
    phone: str
    mail: str


@dataclass
class PackageRecipient:
    name: str

    street: str
    city: str
    zip_code: str
    country_code: str

    contact: str
    phone: str
    mail: str


class LabelTemplate(Enum):
    """A5 format, blank label"""
    A5 = 'A5'
    """A5 format, preprinted label"""
    A5_PP = 'A5_PP'
    """A5 format, printed on A4"""
    A5_ONA4 = 'A5_ONA4'
    """A4 format, 4 labels on layout 2x2"""
    A4_2x2 = 'A4_2x2'
    """A4 format, 4 labels on layout 4x1"""
    A4_4x1 = 'A4_4x1'


class DeliveryService(Enum):
    # T12 = {'code': 'T12'}
    # FDS = {'code': 'FDS', 'info': PackageRecipient.mail}
    FDS = 'FDS'
    FSS = 'FSS'


@dataclass
class PackageOrder:
    sender: PackageSender
    recipient: PackageRecipient
    # Meta data
    pick_up_date: date
    count_of_parcels: int
    client_reference: int
    cod_amount: int
    cod_reference: str
    client_reference: int
    services: array = field(init=False)
    """content of the parcel – info printed on label"""
    content: str = ''
    printer_template: LabelTemplate = LabelTemplate.A4_2x2
    timestamp: date = date.today()
    hash: str = ''
    custom_label: bool = False

    def __post_init__(self):
        self.services = [
            dict(code=DeliveryService.FDS.value, info=self.recipient.mail),
            dict(code=DeliveryService.FSS.value, info=self.recipient.phone)
        ]


# Configuration
@dataclass
class GlsConnectorConfig:
    """Credentials configuration."""
    user_name: str
    password: str
    sender_id: str


# Service


class GlsConnector:
    # TODO: Make it as static constant
    WSDL_URI = 'https://online.gls-slovakia.sk/webservices/soap_server.php?wsdl&ver=18.02.20.01'

    config: GlsConnectorConfig

    def __init__(self, configuration):
        self.config = configuration

    def print_label(self, order: PackageOrder):
        client = Client(self.WSDL_URI)

        sr0 = client.factory.create('svcData')
        sr0['code'] = order.services[0]['code']
        sr0['info'] = order.services[0]['info']

        sr_array = client.factory.create('svcDataArray')
        sr_array._arrayType = 'svcData[1]'
        sr_array['item'] = sr0

        """
        <services SOAP-ENC:arrayType="ns2:svcData[1]" xsi:type="ns2:svcDataArray">
            <item xsi:type="ns2:svcData">
                <code xsi:type="xsd:string">FDS</code>
                <info xsi:type="xsd:string">peter.customer@mail.me</info>
            </item>
        </services>"""
        response = client.service \
            .printlabel(username=self.config.user_name, password=self.config.password,
                        senderid=self.config.sender_id,
                        sender_name=order.sender.name, sender_address=order.sender.street,
                        sender_city=order.sender.city, sender_zipcode=order.sender.zip_code,
                        sender_country=order.sender.country_code,
                        sender_contact=order.sender.contact,
                        sender_phone=order.sender.phone, sender_email=order.sender.mail,
                        consig_name=order.recipient.name, consig_address=order.recipient.street,
                        consig_city=order.recipient.city, consig_zipcode=order.recipient.zip_code,
                        consig_country=order.recipient.country_code,
                        consig_contact=order.recipient.contact,
                        consig_phone=order.recipient.phone, consig_email=order.recipient.mail,
                        pcount=str(order.count_of_parcels),
                        pickupdate=str(order.pick_up_date.isoformat()),
                        content=order.content, clientref=str(order.client_reference),
                        codamount=order.cod_amount,
                        # codref=order.cod_reference, services=order.services,
                        codref=order.cod_reference, services=sr_array,
                        printertemplate=order.printer_template.value,
                        printit=True,
                        timestamp=datetime.now().strftime("%Y%m%d%H%M%S"),
                        hash=self.calculate_hash(self.config, order), customlabel=False,
                        is_autoprint_pdfs=False)

        if hasattr(response, 'successfull') \
                and response.successfull is True \
                and response.pcls.__len__() > 0:

            tracking_code = response['pcls'][0]
            return tracking_code
        else:
            raise Exception("TODO do error handling")

    @staticmethod
    def calculate_hash(config: GlsConnectorConfig, order: PackageOrder):
        base_hash: str = config.user_name \
                         + config.password \
                         + config.sender_id \
                         + order.sender.name \
                         + order.sender.street \
                         + order.sender.city \
                         + order.sender.zip_code \
                         + order.sender.country_code \
                         + order.sender.contact \
                         + order.sender.phone \
                         + order.sender.mail \
                         + order.recipient.name \
                         + order.recipient.street \
                         + order.recipient.city \
                         + order.recipient.zip_code \
                         + order.recipient.country_code \
                         + order.recipient.contact \
                         + order.recipient.phone \
                         + order.recipient.mail \
                         + str(order.count_of_parcels) \
                         + str(order.pick_up_date.isoformat()) \
                         + order.content \
                         + str(order.client_reference) \
                         + str(order.cod_amount) \
                         + order.cod_reference

        return hashlib.sha1(base_hash.encode("utf-8")).hexdigest()
