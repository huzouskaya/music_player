import contextlib
import hashlib
import platform
import uuid
import os

class DeviceFingerprint:
    @staticmethod
    def get_fingerprint() -> str:
        components = [f"host:{platform.node()}"]

        components.append(f"user:{os.path.expanduser('~')}")

        with contextlib.suppress(Exception):
            mac = uuid.getnode()
            components.append(f"mac:{mac & 0xFFFFFF:06x}")
        components.append(f"arch:{platform.machine()}")
        components.append(f"os:{platform.system()}_{platform.release()}")

        components_sorted = sorted(components)
        combined = "|".join(components_sorted)

        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def get_simple_fingerprint() -> str:
        data = f"{platform.node()}:{os.path.expanduser('~')}"
        return hashlib.md5(data.encode()).hexdigest()