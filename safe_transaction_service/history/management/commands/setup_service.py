from typing import Dict, List, NamedTuple, Sequence, Tuple

from django.core.management.base import BaseCommand

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from gnosis.eth import EthereumClientProvider
from gnosis.eth.ethereum_client import EthereumNetwork

from ...models import ProxyFactory, SafeMasterCopy


class CeleryTaskConfiguration(NamedTuple):
    name: str
    description: str
    interval: int
    period: str

    def create_task(self) -> Tuple[PeriodicTask, bool]:
        interval, _ = IntervalSchedule.objects.get_or_create(every=self.interval, period=self.period)
        periodic_task, created = PeriodicTask.objects.get_or_create(task=self.name,
                                                                    defaults={
                                                                        'name': self.description,
                                                                        'interval': interval
                                                                    })
        if periodic_task.interval != interval:
            periodic_task.interval = interval
            periodic_task.save(update_fields=['interval'])

        return periodic_task, created


TASKS = [
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_internal_txs_task',
                            'Index Internal Txs', 13, IntervalSchedule.SECONDS),
    #CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_new_proxies_task',
    #                        'Index new Proxies', 15, IntervalSchedule.SECONDS),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.index_erc20_events_task',
                            'Index ERC20 Events', 14, IntervalSchedule.SECONDS),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.process_decoded_internal_txs_task',
                            'Process Internal Txs', 2, IntervalSchedule.MINUTES),
    CeleryTaskConfiguration('safe_transaction_service.history.tasks.check_reorgs_task',
                            'Check Reorgs', 3, IntervalSchedule.MINUTES),
]

MASTER_COPIES: Dict[EthereumNetwork, List[Tuple[str, int, str]]] = {
    EthereumNetwork.MAINNET: [
        ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 10329734, '1.2.0'),
        ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 9084503, '1.1.1'),
        ('0xaE32496491b53841efb51829d6f886387708F99B', 8915728, '1.1.0'),
        ('0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A', 7457553, '1.0.0'),
        ('0x8942595A2dC5181Df0465AF0D7be08c8f23C93af', 6766257, '0.1.0'),
        ('0xAC6072986E985aaBE7804695EC2d8970Cf7541A2', 6569433, '0.0.2'),
    ],
    EthereumNetwork.RINKEBY: [
        ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 6723632, '1.2.0'),
        ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 5590754, '1.1.1'),
        ('0xaE32496491b53841efb51829d6f886387708F99B', 5423491, '1.1.0'),
        ('0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A', 4110083, '1.0.0'),
        ('0x8942595A2dC5181Df0465AF0D7be08c8f23C93af', 3392692, '0.1.0'),
        ('0x2727D69C0BD14B1dDd28371B8D97e808aDc1C2f7', 3055781, '0.0.2'),
    ],
    EthereumNetwork.GOERLI: [
        ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 2930373, '1.2.0'),
        ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 1798663, '1.1.1'),
        ('0xaE32496491b53841efb51829d6f886387708F99B', 1631488, '1.1.0'),
        ('0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A', 319108, '1.0.0'),
        ('0x8942595A2dC5181Df0465AF0D7be08c8f23C93af', 34096, '0.1.0'),
    ],
    EthereumNetwork.KOVAN: [
        ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 19242615, '1.2.0'),
        ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 15366145, '1.1.1'),
        ('0xaE32496491b53841efb51829d6f886387708F99B', 14740724, '1.1.0'),
        ('0xb6029EA3B2c51D09a50B53CA8012FeEB05bDa35A', 10638132, '1.0.0'),
        ('0x8942595A2dC5181Df0465AF0D7be08c8f23C93af', 9465686, '0.1.0'),
    ],
    EthereumNetwork.XDAI: [
        ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 10612049, '1.2.0'),
        ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 10045292, '1.1.1'),
        ('0x2CB0ebc503dE87CFD8f0eCEED8197bF7850184ae', 12529466, '1.1.1-Circles'),
    ],
    EthereumNetwork.ENERGY_WEB_CHAIN: [
        ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 6398655, '1.2.0'),
        ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 6399212, '1.1.1'),
    ],
    EthereumNetwork.VOLTA: [
        ('0x6851D6fDFAfD08c0295C392436245E5bc78B0185', 6876086, '1.2.0'),
        ('0x34CfAC646f301356fAa8B21e94227e3583Fe3F5F', 6876642, '1.1.1'),
    ]

}

PROXY_FACTORIES: Dict[EthereumNetwork, List[Tuple[str, int]]] = {
    EthereumNetwork.MAINNET: [
        ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 9084508),  # v1.1.1
        ('0x50e55Af101C777bA7A1d560a774A82eF002ced9F', 8915731),  # v1.1.0
        ('0x12302fE9c02ff50939BaAaaf415fc226C078613C', 7450116),  # v1.0.0
    ],
    EthereumNetwork.RINKEBY: [
        ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 5590757),
        ('0x50e55Af101C777bA7A1d560a774A82eF002ced9F', 5423494),
        ('0x12302fE9c02ff50939BaAaaf415fc226C078613C', 4110083),
    ],
    EthereumNetwork.GOERLI: [
        ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 1798666),
        ('0x50e55Af101C777bA7A1d560a774A82eF002ced9F', 1631491),
        ('0x12302fE9c02ff50939BaAaaf415fc226C078613C', 312509),
    ],
    EthereumNetwork.KOVAN: [
        ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 15366151),
        ('0x50e55Af101C777bA7A1d560a774A82eF002ced9F', 14740731),
        ('0x12302fE9c02ff50939BaAaaf415fc226C078613C', 10629898),
    ],
    EthereumNetwork.XDAI: [
        ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 10045327),
    ],
    EthereumNetwork.ENERGY_WEB_CHAIN: [
        ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 6399239),
    ],
    EthereumNetwork.VOLTA: [
        ('0x76E2cFc1F5Fa8F6a5b3fC4c8F4788F0116861F9B', 6876681),
    ]
}


class Command(BaseCommand):
    help = 'Setup Transaction Service Required Tasks'

    def handle(self, *args, **options):
        for task in TASKS:
            _, created = task.create_task()
            if created:
                self.stdout.write(self.style.SUCCESS('Created Periodic Task %s' % task.name))
            else:
                self.stdout.write(self.style.SUCCESS('Task %s was already created' % task.name))

        self.stdout.write(self.style.SUCCESS('Setting up Safe Contract Addresses'))
        self.setup_my_network()

    def setup_my_network(self):
        SafeMasterCopy.objects.get_or_create(address='0x6C068d89dDF42F10f5c66bEB89bbCcD036C1fcb4',
                                             defaults={
                                                 'initial_block_number': 7398174,
                                                 'tx_block_number': 7398174,
                                             })
        ProxyFactory.objects.get_or_create(address='0x345C53a241D9CB7C2B45380d8f683eD616057279',
                                           defaults={
                                               'initial_block_number': 7398179,
                                               'tx_block_number': 7398179,
                                           })
    def _setup_safe_master_copies(self, safe_master_copies: Sequence[Tuple[str, int, str]]):
        for address, initial_block_number, version in safe_master_copies:
            safe_master_copy, _ = SafeMasterCopy.objects.get_or_create(
                address=address,
                defaults={
                    'initial_block_number': initial_block_number,
                    'tx_block_number': initial_block_number,
                    'version': version,
                }
            )
            if safe_master_copy.version != version:
                safe_master_copy.version = version
                safe_master_copy.save(update_fields=['version'])

    def _setup_safe_proxy_factories(self, safe_proxy_factories: Sequence[Tuple[str, int]]):
        for address, initial_block_number in safe_proxy_factories:
            ProxyFactory.objects.get_or_create(address=address,
                                               defaults={
                                                   'initial_block_number': initial_block_number,
                                                   'tx_block_number': initial_block_number,
                                               })