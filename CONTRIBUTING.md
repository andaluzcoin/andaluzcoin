Contributing to Andaluzcoin Core
================================

The Andaluzcoin Core project operates an open contributor model where anyone is
welcome to contribute towards development in the form of peer review, testing
and patches. This document explains the practical process and guidelines for
contributing.

First, in terms of structure, there is no particular concept of "Andaluzcoin Core
developers" in the sense of privileged people. Open source often naturally
revolves around a meritocracy where contributors earn trust from the developer
community over time. Nevertheless, some hierarchy is necessary for practical
purposes. As such, there are repository maintainers who are responsible for
merging pull requests, the release cycle, and moderation.

Project Direction (important)
----------------------------

Andaluzcoin is a culture / meme coin that intentionally starts as a **Andaluzcoin-compatible fork**.

**Current policy (Path 1):**
- Keep consensus changes **out** initially (no block timing changes, no subsidy changes, no PoW swaps, etc.).
- Focus on: branding, network separation, CI + tests, wallet/app experience, release pipeline.

**If you want to propose consensus changes (Path 2):**
Open an issue first with:
- a written spec + motivation,
- a threat model,
- test vectors,
- upgrade mechanism (softfork/hardfork),
- replay protection (if sharing any history).

Pull requests that change consensus rules are high-risk and will require extra review and testing.

Getting Started
---------------

New contributors are very welcome and needed.

Reviewing and testing is highly valued and the most effective way you can contribute
as a new contributor. It also will teach you much more about the code and
process than opening pull requests. Please refer to the [peer review](#peer-review)
section below.

Before you start contributing, familiarize yourself with the Andaluzcoin Core build
system and tests. Refer to the documentation in the repository on how to build
Andaluzcoin Core and how to run the unit tests, functional tests, and fuzz tests.

There are many open issues of varying difficulty waiting to be fixed.
If you're looking for somewhere to start contributing, check out the
`good first issue` list and changes that are `up for grabs` in the issue tracker:

- https://github.com/<ORG>/<REPO>/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22
- https://github.com/<ORG>/<REPO>/issues?q=is%3Aopen+is%3Aissue+label%3A%22Up+for+grabs%22

You do not need to request permission to start working on an issue. However,
you are encouraged to leave a comment if you are planning to work on it.

### Development Setup (Build + Run + Test at a glance)

From a fresh clone, a common dev loop looks like:

### Build (out-of-tree)

./autogen.sh
mkdir -p build && cd build
../configure
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"

Build Instructions
------------------
Andaluzcoin Core follows the Andaluzcoin Core style build system (autotools + optional depends).

### Recommended: out-of-tree builds
./autogen.sh
mkdir -p build && cd build
../configure
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"

### Reproducible / portable builds: depends/

The depends/ system builds pinned third-party dependencies in a controlled way.
This is recommended for CI parity and for producing release artifacts.

cd depends
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
cd ..

./autogen.sh
mkdir -p build && cd build
../configure --prefix="$PWD/../depends/<HOST_TRIPLET>"
make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"

<HOST_TRIPLET> will match a folder under depends/ (for example x86_64-pc-linux-gnu).

### Running the node (regtest)

From your build directory:
./src/andaluzcoind -regtest -daemon
./src/andaluzcoin-cli -regtest getblockchaininfo
./src/andaluzcoin-cli -regtest stop

Tests and CI
------------

### Unit tests

From your build directory:
make check

### Functional tests (from repo root)

From the repo root:
test/functional/test_runner.py

Common options:
test/functional/test_runner.py -h
test/functional/test_runner.py --jobs=4
test/functional/test_runner.py wallet_* p2p_* mempool_*

If you built in a non-default location, set the path to the binaries:

test/functional/test_runner.py --srcdir=build/src
   
### Functional tests that may be skipped locally

Some functional tests require external artifacts or optional build features and may be skipped on developer machines.

- `wallet_backwards_compatibility.py` / `wallet_migration.py`:
  These require “previous release” binaries (a populated `PREVIOUS_RELEASES_DIR`). Andaluzcoin does not ship prior-release artifacts early in the project, so these tests may be skipped until we have tagged releases to validate against.

- `interface_zmq.py`: requires building with ZMQ enabled (e.g. a `build-zmq/` profile).
- `interface_usdt_*.py`: requires building with USDT enabled and sufficient BPF permissions (often run with `sudo`, e.g. `build-usdt-noinline/`).
- `interface_ipc.py`: requires IPC enabled and the Python `capnp` module (pycapnp).
   
### How to run CI locally

Our CI is designed to be reproducible locally. Before pushing, you should be able to run:

  * build (standard and/or depends),
  * unit tests,
  * functional tests,
  * linters/formatters.

A suggested local “CI-like” sequence:

  1. Clean build
     ./autogen.sh
     rm -rf build
     mkdir -p build && cd build
     ../configure
     make -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"
  2. Unit tests
     make check
     cd ..
  3. Functional tests
     test/functional/test_runner.py --jobs=4
  4. Lint / format checks (see Coding Standards)

Optional: run GitHub Actions locally (requires Docker) using act:
  - act -l
  - act -W .github/workflows/ci.yml
  
Coding Standards
----------------

### C++ / headers: clang-format
  * Use clang-format for C++ formatting.
  * Do not mix formatting-only changes with behavior changes unless it is a dedicated refactor PR.

Format specific files:
  - clang-format -i src/**/*.cpp src/**/*.h

If the repository includes a formatting helper script (common pattern):
  * contrib/devtools/clang-format-diff.py or similar
  * test/lint/ formatting targets

Prefer the repo-provided script if present.

### Python: ruff (lint + format)

We use ruff for Python linting (and optionally formatting) in our workflow.

Install:
  - python3 -m pip install -U ruff

Run lint:
  - ruff check .
  
Auto-fix (safe fixes):
  - ruff check . --fix

Format:
  - ruff format .

If your environment still uses legacy lint scripts in test/lint/, those remain acceptable; CI is the source of truth.

### Shell: shellcheck (recommended)

Install via your package manager and run:

  - shellcheck contrib/**/*.sh test/**/*.sh || true

### Good First Issue Label

The purpose of the `good first issue` label is to highlight which issues are
suitable for a new contributor without a deep understanding of the codebase.

However, good first issues can be solved by anyone. If they remain unsolved
for a longer time, a frequent contributor might address them.

You do not need to request permission to start working on an issue. However,
you are encouraged to leave a comment if you are planning to work on it. This
will help other contributors monitor which issues are actively being addressed
and is also an effective way to request assistance if and when you need it.

Communication Channels
----------------------

Discussion about codebase improvements happens in GitHub issues and pull
requests.

Optional real-time chat (recommended for coordination):

  * IRC/Matrix/Discord/Telegram: <PUT YOUR PROJECT LINKS HERE>
  * GitHub Discussions (if enabled): https://github.com/<ORG>/<REPO>/discussions

If/when Andaluzcoin begins considering consensus or P2P protocol changes, use
issues + long-form design docs before code.

Contributor Workflow
--------------------

The codebase is maintained using the "contributor workflow" where everyone
without exception contributes patch proposals using "pull requests" (PRs). This
facilitates social contribution, easy testing and peer review.

To contribute a patch, the workflow is as follows:

  1. Fork repository (only for the first time)
  2. Create topic branch
  3. Commit patches
  4. Push changes to your fork
  5. Create pull request

If this repository is a monotree (node + GUI together), use this repository for
everything. If you split GUI into a separate repository, document that here and
keep the monotree rule consistent.

The project coding conventions in the developer notes (see doc/developer-notes.md)
must be followed.

Committing Patches
------------------
In general, commits should be atomic and diffs should be easy to read. For this
reason, do not mix any formatting fixes or code moves with actual code changes.

Make sure each individual commit is hygienic: that it builds successfully on its
own without warnings, errors, regressions, or test failures.
This means tests must be updated in the same commit that changes the behavior.

Commit messages should be verbose by default consisting of a short subject line
(50 chars max), a blank line and detailed explanatory text as separate
paragraph(s), unless the title alone is self-explanatory (like "Correct typo
in init.cpp") in which case a single title line is sufficient. Commit messages should be
helpful to people reading your code in the future, so explain the reasoning for
your decisions. Further explanation here: https://cbea.ms/git-commit/

If a particular commit references another issue, please add the reference. For
example: refs #1234 or fixes #4321. Using the fixes or closes keywords
will cause the corresponding issue to be closed when the pull request is merged.

Commit messages should never contain any @ mentions (usernames prefixed with "@").

Please refer to the Git manual for more information about Git: https://git-scm.com/doc

### Creating the Pull Request

The title of the pull request should be prefixed by the component or area that
the pull request affects. Valid areas as:

  - `consensus` for changes to consensus critical code
  - `doc` for changes to the documentation
  - `qt` or `gui` for changes to to the GUI
  - `log` for changes to log messages
  - `mining` for changes to the mining code
  - `net` or `p2p` for changes to the peer-to-peer network code
  - `refactor` for structural changes that do not change behavior
  - `rpc`, `rest` or `zmq` for changes to the RPC, REST or ZMQ APIs
  - `contrib` or `cli` for changes to the scripts and tools
  - `test`, `qa` or `ci` for changes to the unit tests, functional tests or CI code
  - `util` or `lib` for changes to the utils or libraries
  - `wallet` for changes to the wallet code
  - `build` for changes to build system (autotools/CMake/etc.)
  - `guix` for changes to reproducible builds

Examples:

    consensus: Add new opcode for BIP-XXXX OP_CHECKAWESOMESIG
    net: Automatically create onion service, listen on Tor
    qt: Add feed bump button
    log: Fix typo in log message

The body of the pull request should contain sufficient description of *what* the
patch does, and even more importantly, *why*, with justification and reasoning.
You should include references to any discussions (for example, other issues).

The description for a new pull request should not contain any `@` mentions. The
PR description will be included in the commit message when the PR is merged and
any users mentioned in the description will be annoyingly notified each time a
fork copies the merge. Instead, make any username mentions in a
subsequent comment to the PR.

### Work in Progress Changes and Requests for Comments

If a pull request is not to be considered for merging (yet), please
prefix the title with [WIP] or use Tasks Lists
in the body of the pull request to indicate tasks are pending.

### Address Feedback

At this stage, one should expect comments and review from other contributors. You
can add more commits to your pull request by committing them locally and pushing
to your fork.

You are expected to reply to any review comments before your pull request is
merged. You may update the code or reject the feedback if you do not agree with
it, but you should express so in a reply. If there is outstanding feedback and
you are not actively working on it, your pull request may be closed.

Please refer to the [peer review](#peer-review) section below for more details.

### Squashing Commits

If your pull request contains fixup commits (commits that change the same line of code repeatedly) or too fine-grained
commits, you may be asked to squash your commits before it will be reviewed. The basic squashing workflow is shown below.

    git checkout your_branch_name
    git rebase -i HEAD~n
    # n is normally the number of commits in the pull request.
    # Set commits (except the one in the first line) from 'pick' to 'squash', save and quit.
    # On the next screen, edit/refine commit messages.
    # Save and quit.
    git push -f # (force push to GitHub)

Please update the resulting commit message, if needed. It should read as a
coherent message. In most cases, this means not just listing the interim
commits.

Please refrain from creating several pull requests for the same change.
Use the pull request that is already open (or was created earlier) to amend
changes. This preserves the discussion and review that happened earlier for
the respective change set.

The length of time required for peer review is unpredictable and will vary from
pull request to pull request.

### Rebasing Changes

When a pull request conflicts with the target branch, you may be asked to rebase it on top of the current target branch.

    git fetch https://github.com/andaluzcoin/andaluzcoin # Fetch the latest upstream commit
    git rebase FETCH_HEAD  # Rebuild commits on top of the new base

This project aims to have a clean git history, where code changes are only made in non-merge commits. This simplifies
auditability because merge commits can be assumed to not contain arbitrary code changes.

Pull Request Philosophy
-----------------------

Patchsets should always be focused. For example, a pull request could add a
feature, fix a bug, or refactor code; but not a mixture. Please also avoid super
pull requests which attempt to do too much, are overly large, or overly complex
as this makes review difficult.

### Features

When adding a new feature, thought must be given to the long term technical debt
and maintenance that feature may require after inclusion. Before proposing a new
feature that will require maintenance, please consider if you are willing to
maintain it (including bug fixing). If features get orphaned with no maintainer
in the future, they may be removed by the Repository Maintainer.

### Refactoring

Refactoring is a necessary part of any software project's evolution. The
following guidelines cover refactoring pull requests for the project.

There are three categories of refactoring: code-only moves, code style fixes, and
code refactoring. In general, refactoring pull requests should not mix these
three kinds of activities in order to make refactoring pull requests easy to
review and uncontroversial. In all cases, refactoring PRs must not change the
behaviour of code within the pull request (bugs must be preserved as is).

Project maintainers aim for a quick turnaround on refactoring pull requests, so
where possible keep them short, uncomplex and easy to verify.

Pull requests that refactor the code should not be made by new contributors. It
requires a certain level of experience to know where the code belongs to and to
understand the full ramification (including rebase effort of open pull requests).

Trivial pull requests or pull requests that refactor the code with no clear
benefits may be immediately closed by the maintainers to reduce unnecessary
workload on reviewing.

"Decision Making" Process
-------------------------

The following applies to code changes to the Andaluzcoin Core project (and related
projects such as libsecp256k1), and is not to be confused with overall 
Network Protocol consensus changes.

Whether a pull request is merged into Andaluzcoin Core rests with the project merge
maintainers.

Maintainers will take into consideration if a patch is in line with the general
principles of the project; meets the minimum standards for inclusion; and will
judge the general consensus of contributors.

In general, all pull requests must:

  - Have a clear use case, fix a demonstrable bug or serve the greater good of
    the project (for example refactoring for modularisation);
  - Be well peer-reviewed;
  - Have unit tests, functional tests, and fuzz tests, where appropriate;
  - Follow code style guidelines (see doc/developer-notes.md), and functional tests docs);
  - Not break the existing test suite;
  - Where bugs are fixed, where possible, there should be unit tests
    demonstrating the bug and also proving the fix. This helps prevent regression.
  - Change relevant comments and documentation when behaviour of code changes.

Patches that change consensus rules are considerably more involved than normal
because they affect the entire ecosystem and must be preceded by extensive design
discussion, strong test coverage, and a clear deployment/upgrade plan.

### Peer Review

Anyone may participate in peer review which is expressed by comments in the pull
request. Typically reviewers will review the code for obvious errors, as well as
test out the patch set and opine on the technical merits of the patch. Project
maintainers take into account the peer review when determining if there is
consensus to merge a pull request.

Code review is a burdensome but important part of the development process, and
as such, certain types of pull requests are rejected. In general, if the
**improvements** do not warrant the **review effort** required, the PR has a
high chance of being rejected. It is up to the PR author to convince the
reviewers that the changes warrant the review effort, and if reviewers are
"Concept NACK'ing" the PR, the author may need to present arguments and/or do
research backing their suggested changes.

#### Conceptual Review

A review can be a conceptual review, where the reviewer leaves a comment
 * `Concept (N)ACK`, meaning "I do (not) agree with the general goal of this pull
   request",
 * `Approach (N)ACK`, meaning `Concept ACK`, but "I do (not) agree with the
   approach of this change".

A `NACK` needs to include a rationale why the change is not worthwhile.
NACKs without accompanying reasoning may be disregarded.

#### Code Review

After conceptual agreement on the change, code review can be provided. A review
begins with `ACK BRANCH_COMMIT`, where `BRANCH_COMMIT` is the top of the PR
branch, followed by a description of how the reviewer did the review. The
following language is used within pull request comments:

  - "I have tested the code", involving change-specific manual testing in
    addition to running the unit, functional, or fuzz tests, and in case it is
    not obvious how the manual testing was done, it should be described;
  - "I have not tested the code, but I have reviewed it and it looks
    OK, I agree it can be merged";
  - A "nit" refers to a trivial, often non-blocking issue.

Project maintainers reserve the right to weigh the opinions of peer reviewers
using common sense judgement and may also weigh based on merit. Reviewers that
have demonstrated a deeper commitment and understanding of the project over time
or who have clear domain expertise may naturally have more weight, as one would
expect in all walks of life.

Where a patch set affects consensus-critical code, the bar will be much
higher in terms of discussion and peer review requirements, keeping in mind that
mistakes could be very costly to the wider community. This includes refactoring
of consensus-critical code.

Backporting
-----------

Security and bug fixes can be backported from `master` to release
branches.
Maintainers will do backports in batches and
use the proper `Needs backport (...)` labels
when needed (the original author does not need to worry about it).

A backport should contain the following metadata in the commit body:

```
Github-Pull: #<PR number>
Rebased-From: <commit hash of the original commit>
```

Copyright
---------

By contributing to this repository, you agree to license your work under the
MIT license unless specified otherwise in `contrib/debian/copyright` or at
the top of the file itself. Any work contributed where you are not the original
author must contain its license header with the original author(s) and source.
