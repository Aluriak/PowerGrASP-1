echo "This bash script will try to install gringo and clasp binaries into pyasp install dir (in a virtualenv named venv)."
echo "It will perform some verifications before doing anything, but that will not prevent bad things to happen if you do not pay attention."

    echo "
    usage: <path/to/clasp.tar.gz> <path/to/gringo.tar.gz>
"

if [[ -e $1 ]];
then
    echo "clasp seems ok"
else
    echo "need path to clasp-3.2.0-x86_64-linux.tar.gz file"
    echo "you can found it at https://sourceforge.net/projects/potassco/files/clasp/"
    echo "(just pick the last version)"
    exit
fi

if [[ -e $2 ]];
then
    echo "gringo seems ok"
else
    echo "need path to gringo-4.5.4-linux-x86_64.tar.gz file"
    echo "you can found it at https://sourceforge.net/projects/potassco/files/gringo/"
    echo "(just pick the last version)"
    exit
fi

if [[ -e venv ]];
then
    echo "venv seems ok"
else
    echo "You need to have a virtualenv named venv/ in current directory ($(pwd))"
    echo "Probably using a command looking like 'virtualenv -p /usr/bin/python3 venv'"
    exit
fi


if stat -t venv/lib/python3*/site-packages/pyasp/bin >/dev/null 2>&1
then
    echo "pyasp seems ok"
else
    echo "You need to have pyasp installed in your virtualenv"
    echo "Probably using a command looking like 'pip3 install pyasp'"
    exit
fi

pyasp_bindir_template=venv/lib/python3*/site-packages/pyasp/bin
pyasp_bindir=$(for filename in $pyasp_bindir_template; do :; done; echo "$filename")
if [[ -e $pyasp_bindir ]];
then
    echo "pyasp bin directory ok ($pyasp_bindir)"
else
    echo "not found: $pyasp_bindir"
    echo "Weirdly, you have a virtualenv, you have pyasp, but you don't have a binary directory in pyasp install directory."
    echo "One first explanation: you are using python 2."
    echo "Let me verify…"
    if [[ -e $(for filename in venv/lib/python2*; do :; done; echo "$filename") ]];
    then
        echo "I think you are using python 2."
        echo "To fix that problem, use python 3."
    else
        echo "Apparently, no, the problem is elsewhere"
        echo "One second explanation: you are doing something unexpected."
        echo "May the Force be with you !"
    fi
    exit
fi

echo "<Press any key (except ctrl+c) to decompress input files and install the binaries>"
read
echo "Decompress the input files…"
tar xf $1
tar xf $2

echo "binaries ready to be moved into $pyasp_bindir"

cp ./clasp-3.2.0/clasp-3.2.0-x86_64-linux $pyasp_bindir/clasp
cp ./gringo-4.5.4-linux-x86_64/gringo $pyasp_bindir/gringo3  # yes, we don't care about gringo3 compatibility. But you just have to replace that binary by the gringo 3 binary if really that's needed.
cp ./gringo-4.5.4-linux-x86_64/gringo $pyasp_bindir/gringo4
echo "binaries moved into $pyasp_bindir"

echo "If you made it to here without error, probably everything work."
echo "congrats !  \\o/ "
