from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions

class WebpayService:
    @staticmethod
    def _get_transaction():
        ambiente = getattr(settings, 'TRANSBANK_AMBIENTE', 'TEST')
        
        if ambiente == 'LIVE':
            options = WebpayOptions(
                commerce_code=settings.TRANSBANK_COMMERCE_CODE,
                api_key=settings.TRANSBANK_API_KEY,
                integration_type=IntegrationType.LIVE
            )
        else:
            # Usa directamente las credenciales oficiales embebidas en el SDK para evitar errores de tipeo
            options = WebpayOptions(
                commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
                api_key=IntegrationApiKeys.WEBPAY,
                integration_type=IntegrationType.TEST
            )
        return Transaction(options)

    @classmethod
    def crear_transaccion(cls, buy_order, session_id, amount, return_url):
        tx = cls._get_transaction()
        return tx.create(buy_order, session_id, amount, return_url)

    @classmethod
    def confirmar_transaccion(cls, token_ws):
        tx = cls._get_transaction()
        return tx.commit(token_ws)