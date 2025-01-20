Repository Tools
---------------------

### [Developer tools](/contrib/devtools) ###
Specific tools for developers working on this repository.
Additional tools, including the `github-merge.py` script, are available in the [maintainer-tools](https://github.com/andaluzcoin-core/andaluzcoin-maintainer-tools) repository.

### [Verify-Commits](/contrib/verify-commits) ###
Tool to verify that every merge commit was signed by a developer using the `github-merge.py` script.

### [Linearize](/contrib/linearize) ###
Construct a linear, no-fork, best version of the blockchain.

### [Qos](/contrib/qos) ###

A Linux bash script that will set up traffic control (tc) to limit the outgoing bandwidth for connections to the Andaluzcoin network. This means one can have an always-on andaluzcoind instance running, and another local andaluzcoind/andaluzcoin-qt instance which connects to this node and receives blocks from it.

### [Seeds](/contrib/seeds) ###
Utility to generate the pnSeed[] array that is compiled into the client.

Build Tools and Keys
---------------------

### Packaging ###
The [Debian](/contrib/debian) subfolder contains the copyright file.

All other packaging related files can be found in the [andaluzcoin-core/packaging](https://github.com/andaluzcoin-core/packaging) repository.

### [MacDeploy](/contrib/macdeploy) ###
Scripts and notes for Mac builds.

Test and Verify Tools
---------------------

### [TestGen](/contrib/testgen) ###
Utilities to generate test vectors for the data-driven Andaluzcoin tests.

### [Verify-Binaries](/contrib/verify-binaries) ###
This script attempts to download and verify the signature file SHA256SUMS.asc from andaluzcoin.org.

Command Line Tools
---------------------

### [Completions](/contrib/completions) ###
Shell completions for bash and fish.
