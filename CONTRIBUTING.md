# Contributing to AISonobuoy

Want to hack on AISonobuoy? Awesome! Here are instructions to get you started.
If you have any questions or find the instructions to be incomplete, please do
open an issue to let us know about it.

## Contribution guidelines

### Pull requests are always welcome

We are always thrilled to receive pull requests and do our best to
process them as fast as possible. Not sure if that typo is worth a pull
request? Do it! We will appreciate it.

If your pull request is not accepted on the first try, don't be
discouraged! If there's a problem with the implementation, hopefully you
received feedback on what to improve.

### Create issues...

Any significant improvement should be documented as [a github
issue](https://github.com/IQTLabs/AISonobuoy/issues) before anybody
starts working on it.

### ...but check for existing issues first!

Please take a moment to check that an issue doesn't already exist
documenting your bug report or improvement proposal. If it does, it
never hurts to add a quick "+1" or "I have this problem too". This will
help prioritize the most common problems and requests.

### Conventions

#### Submitting a pull request

Fork the repo and make changes on your fork in a feature branch.

Make sure you include relevant updates or additions to documentation and
tests when creating or modifying features.

Pull requests descriptions should be as clear as possible and include a
reference to all the issues that they address.

Code review comments may be added to your pull request. Discuss, then make the
suggested modifications and push additional commits to your feature branch. Be
sure to post a comment after pushing. The new commits will show up in the pull
request automatically, but the reviewers will not be notified unless you
comment.

Before the pull request is merged, make sure that you squash your commits into
logical units of work using `git rebase -i` and `git push -f`. After every
commit the test suite should be passing. Include documentation changes in the
same commit so that a revert would remove all traces of the feature or fix.

Commits that fix or close an issue should include a reference like `Closes #XXX`
or `Fixes #XXX`, which will automatically close the issue when merged.

## Decision process

### How are decisions made?

Short answer: with pull requests to the AISonobuoy repository.

All decisions affecting AISonobuoy, big and small, follow the same 3 steps:

* Step 1: Open a pull request. Anyone can do this.

* Step 2: Discuss the pull request. Anyone can do this.

* Step 3: Accept or refuse a pull request. A maintainer does this.


### How can I become a maintainer?

* Step 1: learn the code inside out
* Step 2: make yourself useful by contributing code, bugfixes, support etc.

Don't forget: being a maintainer is a time investment. Make sure you will have time to make yourself available.
You don't have to be a maintainer to make a difference on the project!

### What are a maintainer's responsibility?

It is every maintainer's responsibility to:

* 1) Deliver prompt feedback and decisions on pull requests.
* 2) Be available to anyone with questions, bug reports, criticism etc. on AISonobuoy.

### How is this process changed?

Just like everything else: by making a pull request :)

*Derivative work from [Docker](https://github.com/moby/moby/blob/master/CONTRIBUTING.md).*

### Any questions?

As stated above, if you have any questions or encounter any problems, we recommend checking the
pre-existing issues on the project page. If nothing relates or the discussion turns out to not relate
any longer, feel free to start a new issue. We do our best to respond in a timely fashion and to
keep all discussions open and transparent.
