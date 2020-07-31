pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'liegensteuerung')
gnome = import('gnome')

gnome.compile_resources('liegensteuerung',
  'liegensteuerung.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'liegensteuerung.in',
  output: 'liegensteuerung',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

liegensteuerung_sources = [
  '__init__.py',

  'main.py',
  'window.py',

  'page.py',

  'keyboard.py',

  'edit_patient_page.py',
  'edit_program_page.py',
  'login_page.py',
  'pain_evaluation_page.py',
  'register_page.py',
  'select_patient_page.py',
  'select_program_page.py',
  'set_up_page.py',
  'treatment_page.py',
  'users_page.py',

  'patient_row.py',
  'program_row.py',
  'user_row.py',
  'treatment_row.py',

  'auth_util.py',
  'osk_util.py',
  'opcua_util.py',
  'patient_util.py',
  'program_util.py',
  'usb_util.py',
  'user_util.py',
  'treatment_util.py',
]

install_data(liegensteuerung_sources, install_dir: moduledir)
