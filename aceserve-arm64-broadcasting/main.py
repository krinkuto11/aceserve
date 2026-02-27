import os
import sys
import threading
import traceback
import time
import platform
from datetime import datetime
from functools import wraps

# -----------------------------
# Configuración inicial
# -----------------------------
OUTPUT_CONSOLE = True
DEBUG_MODULE = True
GOT_RCP_HOST = True

# -----------------------------
# Simulación de app_bridge.Android
# -----------------------------
class Android:
    def getAceStreamHome(self, *args, **kwargs):
        return "/dev/shm"

    def makeToast(self, msg, *args, **kwargs):
        print(msg)

    def getDisplayLanguage(self, *args, **kwargs):
        return 'en'

    def getRAMSize(self, *args, **kwargs):
        return 1024 * 1024 * 1024

    def getMaxMemory(self, *args, **kwargs):
        return 1024 * 1024 * 1024

    def getDeviceId(self, *args, **kwargs):
        return 'd3efefe5-4ce4-345b-adb6-adfa3ba92eab'

    def getAppId(self, *args, **kwargs):
        return 'd3efefe5-4ce4-345b-adb6-adfa3ba92eab'

    def getDeviceManufacturer(self, *args, **kwargs):
        return 'Samsung'

    def getDeviceModel(self, *args, **kwargs):
        return 'Galaxy S3'

    def onSettingsUpdated(self, *args, **kwargs):
        return

    def onEvent(self, *args, **kwargs):
        return

    def getAppVersionCode(self, *args, **kwargs):
        return "6.6"

    # -----------------------------
    # Detectar arquitectura real
    # -----------------------------
    def getArch(self, *args, **kwargs):
        arch = platform.machine()
        if arch == 'aarch64':
            return 'arm64-v8a'
        elif arch.startswith('arm'):
            return 'armv7h'
        else:
            return arch

    def getLocale(self, *args, **kwargs):
        return "en-US"

    def isAndroidTv(self, *args, **kwargs):
        return False

    def hasBrowser(self, *args, **kwargs):
        return False

    def hasWebView(self, *args, **kwargs):
        return False

    def getMemoryClass(self, *args, **kwargs):
        return 64

    def publishFileReceiverState(self, *args, **kwargs):
        return

    def getAppInfo(self, *args, **kwargs):
        return {
            "appId": "d3efefe5-4ce4-345b-adb6-adfa3ba92eab",
            "appVersionCode": "6.6",
            "deviceId": "d3efefe5-4ce4-345b-adb6-adfa3ba92eab",
            "arch": self.getArch(),
            "locale": "en-US",
            "isAndroidTv": False,
            "hasBrowser": False,
            "hasWebView": False
        }

    def _fake_rpc(self, method, *args):
        print(method, *args)
        if hasattr(Android, method):
            return getattr(Android, method)(self, *args)
        raise Exception("Unknown method: %s" % method)

# Instancia de droid simulada
droid = Android()

# -----------------------------
# Directorio home
# -----------------------------
home_dir = droid.getAceStreamHome()

if not OUTPUT_CONSOLE:
    try:
        sys.stderr = open(os.path.join(home_dir, "acestream_std.log"), 'w')
        sys.stdout = sys.stderr
    except:
        pass

# -----------------------------
# Función de log
# -----------------------------
def log(msg):
    try:
        line = '{}|{}|bootstrap|{}'.format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            threading.currentThread().name,
            msg
        )
        with open(os.path.join(home_dir, 'acestream.log'), 'a') as f:
            f.write(line + '\n')
        print(line)
    except:
        pass

log('Starting AceStream Service on architecture: {}'.format(droid.getArch()))

# -----------------------------
# VPN wait hook: sleep until tun0 is available if WAIT_FOR_VPN is set
# -----------------------------
if os.environ.get('WAIT_FOR_VPN', '').lower() in ('1', 'true', 'yes'):
    log('WAIT_FOR_VPN enabled, waiting for tun0 interface...')
    _vpn_timeout = int(os.environ.get('VPN_TIMEOUT', '60'))
    _vpn_elapsed = 0
    while not os.path.exists('/sys/class/net/tun0'):
        if _vpn_elapsed >= _vpn_timeout:
            log(f'WAIT_FOR_VPN: tun0 not found after {_vpn_timeout}s, proceeding anyway')
            break
        time.sleep(1)
        _vpn_elapsed += 1
    else:
        log('tun0 interface detected, proceeding...')

# -----------------------------
# DNS override via DNS_OVERRIDE env var (e.g. "1.1.1.1" or "1.1.1.1,8.8.8.8")
# Falls back to well-known public DNS if not set.
# -----------------------------
import dns.resolver
from dnsproxyd import dns_daemon

dns_override = os.environ.get('DNS_OVERRIDE', '').strip()
if dns_override:
    nameservers = [ns.strip() for ns in dns_override.split(',') if ns.strip()]
    log(f'Override DNS usando DNS_OVERRIDE: {nameservers}')
else:
    nameservers = ['1.1.1.1', '1.0.0.1']
    log(f'DNS_OVERRIDE no definido, usando DNS por defecto: {nameservers}')

RESOLVER = dns.resolver.Resolver()
RESOLVER.nameservers = nameservers
dns.resolver.override_system_resolver(RESOLVER)
dns_daemon(RESOLVER)


# -----------------------------
# Monkey patch NetworkConnectionMonitor
# -----------------------------
try:
    from ACEStream.Core.Utilities.NetworkConnectionMonitor import NetworkConnectionMonitor
    NetworkConnectionMonitor.check_connection = lambda self, *args, **kwargs: True
except ImportError:
    log('Could not patch NetworkConnectionMonitor')

# -----------------------------
# Monkey patch TimedTaskQueue / LiveDownload
# -----------------------------
try:
    from ACEStream.Utilities.TimedTaskQueue import TimedTaskQueue
    from ACEStream.Core.LiveDownload import LiveDownload

    def add_task_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "args" in kwargs and isinstance(kwargs["args"], list):
                if any(isinstance(item, LiveDownload) for item in kwargs["args"]):
                    return None
            return func(*args, **kwargs)
        return wrapper

    TimedTaskQueue.add_task = add_task_decorator(TimedTaskQueue.add_task)
except ImportError:
    log('Could not patch TimedTaskQueue')

# -----------------------------
# Arranque de AceStream
# -----------------------------
try:
    from acestreamengine import Core
    Core.run(sys.argv[1:])
except Exception as e:
    log('Error starting Core: {}'.format(e))
    try:
        with open(os.path.join(home_dir, "acestream_error.log"), 'a') as f:
            traceback.print_exc(file=f)
    except Exception as e2:
        log('Failed to write error log: {}'.format(e2))
    droid.makeToast("%r" % e)



