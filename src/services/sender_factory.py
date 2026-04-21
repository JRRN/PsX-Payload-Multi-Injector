from .payload_sender import SocatSender, TCPSender


class SenderFactory:
    def create(self, use_socat):
        return SocatSender() if use_socat else TCPSender()
