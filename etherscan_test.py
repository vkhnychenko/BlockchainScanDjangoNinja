import os
import django

from dotenv import load_dotenv



load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from wallets.services.etherscan import get_tx_by_hash_from_scan, get_tx_from_scan


def main():
    print(get_tx_from_scan('0x1d43EBD3090Ba51f2b0D581E594Aca30d1c525bC', 'bsc', 'token')[0])


if __name__ == '__main__':
    main()
    # asyncio.get_event_loop().run_until_complete(main())
