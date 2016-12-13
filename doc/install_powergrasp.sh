echo "AUTO-INSTALLATION OF POWERGRASP"
echo "This script will probably not work, because overly complicated."
echo "You should probably just install python 3, pip for python 3, then use pip to install powergrasp."
echo "This is basically what this script do, plus verification of available packages."
echo "You also should setup a virtualenv before running this script."

if [[ $(which python | grep "which: no") ]];
then
    echo "BAD: Python is not available"
    echo "you should first install it"
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
    exit
fi
binPip=pip3
echo "OK: pip for python 3 ($binPip)"



command1="$binPip install pyasp -U"
command2="$binPip install powergrasp -U"
echo "The following commands will be launch:"
echo "    $command1"
echo "    $command2"

echo "<Press return to run these commands>"
echo "Run commands..."
$($command1)
$($command2)
