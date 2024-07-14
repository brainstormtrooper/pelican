pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'cphotos')
gnome = import('gnome')

gnome.compile_resources('cphotos',
  'cphotos.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir
)

python = import('python')




conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'cphotos.in',
  output: 'cphotos',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

#install_subdir(
#    'remoteproviders',
#    install_dir: moduledir
#)


cphotos_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'cdata.py',
  'locals.py',
  'dbase.py',
  'dates.py',
  'pager.py',
  'previews.py',
  'mapview.py'
]

install_data(cphotos_sources, install_dir: moduledir)
