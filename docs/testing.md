# Validate both tracks

Run the existing local synthetic tests once per independent tree:

```sh
SNIPER_TRACK=old python3 -m unittest discover -s tests -v
SNIPER_TRACK=new python3 -m unittest discover -s tests -v
```

The tests default to OLD when SNIPER_TRACK is omitted. They exercise local
synthetic Satellite modules and repository-owned code, not real hosts. Supply
the reviewed collection and an appropriate Ansible runtime for syntax checking
all seven entry points in each directory. The root collections requirements
file retains native AAP dependency mapping; each track also has an explicit copy.

For runtime/API verification after environment setup, select that track's
`check_runtime.yml` in AAP. Local tests and syntax checks alone do not establish
live Satellite, host access, installation or patching success.
