python setup.py sdist bdist_wheel
pip install --upgrade .
pack_o_daemon
pip uninstall pack_o_daemon -y