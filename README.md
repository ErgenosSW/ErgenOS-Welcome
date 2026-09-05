# ErgenOS Welcome

ErgenOS Welcome is the first-login application for ErgenOS. It presents the installed system identity, reports whether ErgenCTL is available and provides direct access to project resources.

The application is intentionally read-only. It does not install packages, modify repositories or request administrative privileges.

## Current scope

- GTK4 and libadwaita interface
- system version and build information from `/etc/os-release`
- ErgenCTL availability indicator
- ErgenOS installer launcher visible only in the live ISO
- links to ErgenOS, ErgenCTL and the issue tracker
- automatic startup after login, enabled by default
- user-controlled login startup in the installed system

## Development

Runtime dependencies:

- Python 3.11 or newer
- PyGObject
- GTK4
- libadwaita

Run from the source tree:

```bash
PYTHONPATH=src python -m ergenos_welcome.app
```

Run tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Build and install to a packaging destination:

```bash
meson setup build
DESTDIR=/path/to/package-root meson install -C build
```

## License

ErgenOS Welcome is licensed under GPL-3.0-or-later.
