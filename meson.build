project(
  'ergenos-welcome',
  version: '0.1.0',
  meson_version: '>=1.3.0',
)

gnome = import('gnome')
python = import('python').find_installation('python3')

python.install_sources(
  files(
    'src/ergenos_welcome/__init__.py',
    'src/ergenos_welcome/app.py',
    'src/ergenos_welcome/settings.py',
    'src/ergenos_welcome/system_info.py',
  ),
  subdir: 'ergenos_welcome',
)

launcher_configuration = configuration_data()
launcher_configuration.set('PYTHON', python.full_path())
configure_file(
  input: 'data/ergenos-welcome.in',
  output: 'ergenos-welcome',
  configuration: launcher_configuration,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x',
)

install_data(
  'data/io.github.ergenossw.ergenoswelcome.desktop',
  install_dir: get_option('datadir') / 'applications',
)
install_data(
  'data/io.github.ergenossw.ergenoswelcome-autostart.desktop',
  install_dir: get_option('sysconfdir') / 'xdg' / 'autostart',
  rename: 'io.github.ergenossw.ergenoswelcome.desktop',
)
install_data(
  'data/io.github.ergenossw.ergenoswelcome.metainfo.xml',
  install_dir: get_option('datadir') / 'metainfo',
)
install_data(
  'data/io.github.ergenossw.ergenoswelcome.png',
  install_dir: get_option('datadir') / 'icons' / 'hicolor' / '256x256' / 'apps',
)

gnome.post_install(gtk_update_icon_cache: true)
