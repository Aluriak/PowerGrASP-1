echo "AUTO-INSTALLATION OF POWERGRASP"
echo "This script will probably not work, because overly complicated."
echo "You should probably just install python 3, pip for python 3, then use pip to install pyasp, then powergrasp in a virtualenv."
echo "This is basically what this script do, plus verification of available packages."


if [[ $(which python | grep "which: no") ]];
then
    echo "BAD: Python is not available"
    echo "you should first install it"
    echo "probably with something like:"
    echo "    sudo apt-get install python3    # if you're using debian/ubuntu/…"
    echo "    sudo dnf install python3        # if you're using fedora/…"
    exit
fi


if [[ $(python --version 2>&1 | grep "ython 3.") ]];
then
        binPy=python
else
        binPy=python3
        if [[ $(which $binPy | grep "which: no") ]];
        then
            echo "BAD: Python 3 not available"
            echo "you should first install it"
            exit
        fi
fi
echo "OK: Python 3 ($binPy)"


if [[ $(which pip3 | grep "which: no") ]];
then
    echo "BAD: pip for python 3 not available"
    echo "you should first install it"
    echo "probably with something like:"
    echo "    sudo apt-get install python3-pip    # if you're using debian/ubuntu/…"
    echo "    sudo dnf install python3-pip        # if you're using fedora/…"
    exit
fi
binPip=pip3
echo "OK: pip for python 3 ($binPip)"



command_venv="$binPip install virtualenv --user -U"
command_createvenv="virtualenv venv -p /usr/bin/python3"
command_loadvenv="source venv/bin/activate"
command_pg="$binPip install powergrasp -U"
command_pyasp="$binPip install pyasp -U"
echo "The following commands will be run:"
echo "    $command_venv"
echo "    $command_createvenv"
echo "    $command_loadvenv"
echo "    $command_pg"
echo "    $command_pyasp"

echo "<Press any key (except ctrl+c) to run these commands>"
read
echo "Run commands... (and hoping for the best)"
$command_venv
$command_createvenv
$command_loadvenv
$command_pg
$command_pyasp

echo "If you made it to here without any error, chances are this script succeed."
echo "(or messed up your system so badly you will have to reinstall everything)"
