import requests
import re
import settings

# DD-WRT live info API
url = "http://" + settings.ROUTER_IP + "/Info.live.htm"


class DHCPLease(object):
    def __init__(self, name, ip_addr, mac_addr, lease_time, id=0):
        self.name = name
        self.ip_addr = ip_addr
        self.mac_addr = mac_addr
        self.lease_time = lease_time

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.mac_addr == other.mac_addr
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.mac_addr)


class WirelessClient(object):
    def __init__(self, mac_addr, interface, time, tx_rate=0, rx_rate=0, signal=0, noise=0, SNR=0, id=0):
        self.mac_addr = mac_addr
        self.interface = interface
        self.time = time

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.mac_addr == other.mac_addr
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.mac_addr)


class RouterScraper(object):

    @staticmethod
    def _chunks(input_list, chunk_size):
        for i in range(0, len(input_list), chunk_size):
            yield input_list[i:i + chunk_size]

    @staticmethod
    def _get_public_data():
        raw_data = requests.get(url)
        data_dict = dict(re.findall("(\w+)::([^\}]*)", raw_data.text))
        for key in data_dict:
            data_dict[key] = re.findall("'(.+?)'", data_dict[key])
        return data_dict

    @staticmethod
    def get_dhcp_leases():
        public_data = RouterScraper._get_public_data()
        leases_raw = RouterScraper._chunks(public_data["dhcp_leases"], 5)
        dhcp_leases = [DHCPLease(*lease) for lease in leases_raw]
        return dhcp_leases

    @staticmethod
    def get_wireless_clients():
        public_data = RouterScraper._get_public_data()
        clients_raw = RouterScraper._chunks(public_data["active_wireless"], 9)
        clients = [WirelessClient(*client) for client in clients_raw]
        return clients
