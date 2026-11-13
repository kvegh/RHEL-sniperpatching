"""Read native RPM EVR and uname to verify the running NEW-host kernel."""
from functools import cmp_to_key
import json
import os
import platform
import rpm

rows = [item for item in rpm.TransactionSet().dbMatch('name', 'kernel-core')
        if item['arch'] == platform.machine()]
if not rows:
    raise SystemExit('No native kernel-core RPM for the running architecture')


def evr(item):
    return (str(item['epoch'] or 0), str(item['version']), str(item['release']))


latest = max(rows, key=cmp_to_key(lambda left, right: rpm.labelCompare(evr(left), evr(right))))
release = '{}-{}.{}'.format(latest['version'], latest['release'], latest['arch'])
print(json.dumps({'running_latest_kernel': os.uname().release == release,
                  'running_kernel': os.uname().release, 'latest_kernel': release}))
